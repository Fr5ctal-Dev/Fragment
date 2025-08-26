from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pyflakes.api import check
from pyflakes.reporter import Reporter
import io


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, document, script):
        super().__init__(document)
        self.script = script
        self.lexer = PythonLexer()
        self.style = get_style_by_name('lightbulb')
        self.formats = {}
        for token, style in self.style:
            qformat = QtGui.QTextCharFormat()
            if style['color']:
                qformat.setForeground(QtGui.QColor(f'#{style["color"]}'))
            if style['bgcolor']:
                qformat.setBackground(QtGui.QColor(f'#{style["bgcolor"]}'))
            if style['bold']:
                qformat.setFontWeight(QtGui.QFont.Weight.Bold)
            if style['italic']:
                qformat.setFontItalic(True)
            if style['underline']:
                qformat.setFontUnderline(True)
            self.formats[token] = qformat

    def highlightBlock(self, text):
        tokens = lex(text, self.lexer)
        index = 0
        for ttype, value in tokens:
            length = len(value)
            while ttype not in self.formats:
                ttype = ttype.parent
                if ttype is Token:
                    break
            fmt = self.formats.get(ttype, QtGui.QTextCharFormat())
            self.setFormat(index, length, fmt)
            index += length


class LintWorker(QtCore.QObject):
    finished = QtCore.Signal(object)
    def __init__(self, code):
        super().__init__()
        self.code = code

    def run(self):
        results = self.lint_code(self.code)
        self.finished.emit(results)

    def lint_code(self, code):
        class CustomReporter(Reporter):
            def __init__(self):
                super().__init__(io.StringIO(), io.StringIO())
                self.issues = []

            def flake(self, message):
                self.issues.append({
                    'filename': message.filename,
                    'line': message.lineno,
                    'col': message.col + 1,
                    'type': message.__class__.__name__,
                    'text': message.message % message.message_args,
                })

            def syntaxError(self, filename, msg, lineno, offset, text):
                self.issues.append({
                    'filename': filename, 'line': lineno, 'col': offset,
                    'type': 'SyntaxError', 'text': msg,
                })

            def unexpectedError(self, filename, msg):
                self.issues.append({'filename': filename, 'type': 'UnexpectedError', 'text': msg})

        rep = CustomReporter()
        check(code, filename='main.py', reporter=rep)

        return rep.issues


class ScriptEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, script, path):
        super().__init__()
        self.script = script
        self.path = path

        with open(self.script) as fp:
            self.insertPlainText(fp.read())

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.on_update)
        self.update_timer.start(0)

        self.font = QtGui.QFont('Consolas', 11)
        self.setFont(self.font)
        self.setLineWrapMode(self.LineWrapMode.NoWrap)

        self.syntax_highlighter = SyntaxHighlighter(self.document(), self.script)

        self.lint_worker = None
        self.lint_worker_thread = None
        self.lint_output = None

    def on_update(self):
        self.start_lint_worker()

    def get_line_indentation(self, line):
        return len(line) - len(line.lstrip())

    def should_increase_indent(self, line):
        stripped_line = line.strip()
        if ':' in stripped_line:
            colon_pos = stripped_line.find(':')
            after_colon = stripped_line[colon_pos + 1:].strip()
            if not after_colon or after_colon.startswith('#'):
                return True

    def should_decrease_indent(self, line):
        stripped_line = line.strip()

        for keyword in ['return', 'pass', 'raise']: # Add more if I missed some
            if stripped_line.startswith(keyword) or stripped_line == keyword + ':':
                return True

        return False

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            spaces = 0
            for c in cursor.block().text():
                if c == ' ':
                    spaces += 1
                else:
                    break
            if self.should_increase_indent(cursor.block().text()):
                spaces += 4

            elif self.should_decrease_indent(cursor.block().text()):
                spaces = max(spaces - 4, 0)

            self.insertPlainText('\n')
            self.insertPlainText(' ' * spaces)
            event.accept()
            self.ensureCursorVisible()
            return

        if event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            position = cursor.position()
            cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
            selected_text = cursor.selectedText()
            spaces = self.get_line_indentation(selected_text)
            if selected_text.strip() == '':
                add_spaces = 4 - spaces % 4
                cursor.beginEditBlock()
                cursor.setPosition(position, cursor.MoveMode.KeepAnchor)
                cursor.insertText(' ' * add_spaces)
                cursor.endEditBlock()
                event.accept()
                return

        if event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            position = cursor.position()
            cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
            selected_text = cursor.selectedText()
            spaces = self.get_line_indentation(selected_text)
            if spaces > 0 and selected_text.strip() == '':
                delete_spaces = (4 if not spaces % 4 else spaces % 4)
                cursor.beginEditBlock()
                cursor.setPosition(position - delete_spaces, cursor.MoveMode.MoveAnchor)
                cursor.setPosition(position, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.endEditBlock()
                event.accept()
                return

        super().keyPressEvent(event)

    def start_lint_worker(self):
        if self.lint_worker is not None:
            return

        self.lint_worker = LintWorker(self.toPlainText())
        self.lint_worker_thread = QtCore.QThread()
        self.lint_worker.moveToThread(self.lint_worker_thread)
        self.lint_worker_thread.started.connect(self.lint_worker.run)
        self.lint_worker_thread.start()
        self.lint_worker.finished.connect(self.lint_worker_finished)

    def lint_worker_finished(self, output):
        self.lint_worker_thread.quit()
        self.lint_worker_thread.wait()
        self.lint_worker = None
        self.lint_worker_thread = None

        self.lint_output = output

        self.update_lint_extra_selections()

    def update_lint_extra_selections(self):
        extra_selections = []
        for message in self.lint_output:
            lint_selection = QtWidgets.QTextEdit.ExtraSelection()
            lint_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
            lint_selection.cursor = self.textCursor()
            lint_selection.cursor.setPosition(self.document().findBlockByLineNumber(message['line'] - 1).position() + message['col'])
            lint_selection.format.setBackground(QtGui.QColor(200, 0, 0))
            extra_selections.append(lint_selection)

        self.setExtraSelections(extra_selections)

    def save(self):
        with open(self.script, 'w') as fp:
            fp.write(self.toPlainText())
