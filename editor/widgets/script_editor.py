from .tool_tip import Tooltip
import jedi
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pyflakes.api import check
from pyflakes.reporter import Reporter
import io
import re


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


class CompletionWorker(QtCore.QObject):
    finished = QtCore.Signal(object)

    def __init__(self, script, project_path, line, column):
        super().__init__()
        self.script = script
        self.project_path = project_path
        self.line = line
        self.column = column

    def run(self):
        results = self.get_completions()
        self.finished.emit(results)

    def get_completions(self):
        script = jedi.Script(path=self.project_path / self.script, project=jedi.Project(self.project_path))
        try:
            completions = script.complete(line=self.line, column=self.column)
        except ValueError:
            return {}
        comps = {}
        for completion in completions:
            if completion.complete:
                comps[completion.name_with_symbols] = {'prefix_length': completion.get_completion_prefix_length()}
        return comps


class ScriptEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, script, path):
        super().__init__()
        self.script = script
        self.path = path

        self.indent_spacing = 4

        with open(self.path / self.script) as fp:
            self.insertPlainText(fp.read())

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.on_update)
        self.update_timer.start(10)

        self.main_font = QtGui.QFont('Consolas', 11)
        self.setFont(self.main_font)
        self.setLineWrapMode(self.LineWrapMode.NoWrap)

        self.cursor_extra_selections = []
        self.cursorPositionChanged.connect(self.update_cursor_extra_selections)

        self.syntax_highlighter = SyntaxHighlighter(self.document(), self.script)

        self.completer = QtWidgets.QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completion_model = QtGui.QStandardItemModel()
        self.completer.setModel(self.completion_model)
        self.current_completion = None
        self.textChanged.connect(self.on_text_changed)
        self.completer.activated.connect(self.insert_completion)
        self.completer.highlighted.connect(self.set_highlight_completion)

        self.completion_output = {}

        self.completion_worker = None
        self.completion_worker_thread = None
        self.completion_ran = False

        self.lint_output = {}
        self.lint_extra_selections = []

        self.lint_tooltip = Tooltip(parent=self)
        self.lint_tooltip.hide()
        self.lint_tooltip.setFont(self.main_font)

    def on_update(self):
        self.update_lint_tooltip()
        self.update_extra_selections()

    def get_line_indentation(self, line):
        return len(line) - len(line.lstrip())

    def should_increase_indent(self, line):
        stripped_line = line.strip()
        if ':' in stripped_line:
            colon_pos = stripped_line.rfind(':')
            cursor = self.textCursor()
            if cursor.positionInBlock() > colon_pos:
                after_colon = stripped_line[colon_pos + 1:].strip()
                if not after_colon or after_colon.startswith('#'):
                    return True
        return False

    def should_decrease_indent(self, line):
        stripped_line = line.strip()

        for keyword in ['return', 'pass', 'raise']: # Add more if I missed some
            if stripped_line.startswith(keyword) or stripped_line == keyword + ':':
                return True

        return False

    def keyPressEvent(self, event):
        self.ensureCursorVisible()
        if self.completer.popup().isVisible():
            if event.key() == Qt.Key.Key_Tab:
                event.accept()
                self.insert_completion(self.current_completion)
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.completer.popup().hide()
                event.ignore()
                return
        else:
            if event.key() == Qt.Key.Key_Tab:
                cursor = self.textCursor()
                position = cursor.position()
                cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
                selected_text = cursor.selectedText()
                spaces = self.get_line_indentation(selected_text)
                if selected_text.strip() == '':
                    add_spaces = self.indent_spacing - spaces % self.indent_spacing
                    cursor.beginEditBlock()
                    cursor.setPosition(position, cursor.MoveMode.KeepAnchor)
                    cursor.insertText(' ' * add_spaces)
                    cursor.endEditBlock()
                    event.accept()
                    return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            indents = self.get_line_indentation(cursor.block().text())
            spaces = indents

            if self.should_increase_indent(cursor.block().text()):
                spaces += self.indent_spacing - indents % self.indent_spacing or self.indent_spacing

            elif self.should_decrease_indent(cursor.block().text()):
                spaces = max(spaces - self.indent_spacing, 0)

            self.insertPlainText('\n')
            self.insertPlainText(' ' * spaces)
            event.accept()
            self.ensureCursorVisible()
            return

        if event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            position = cursor.position()
            cursor.movePosition(cursor.MoveOperation.StartOfLine, cursor.MoveMode.KeepAnchor)
            selected_text = cursor.selectedText()
            spaces = self.get_line_indentation(selected_text)
            if spaces > 0 and selected_text.strip() == '' and not self.textCursor().hasSelection():
                delete_spaces = (spaces % self.indent_spacing or self.indent_spacing)
                cursor.beginEditBlock()
                cursor.setPosition(position - delete_spaces, cursor.MoveMode.MoveAnchor)
                cursor.setPosition(position, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
                cursor.endEditBlock()
                event.accept()
                return

        super().keyPressEvent(event)

    def lint_code(self):
        class CustomReporter(Reporter):
            def __init__(self):
                super().__init__(io.StringIO(), io.StringIO())
                self.issues = {}

            def flake(self, message):
                line = message.lineno - 1

                self.issues[line] = {
                    'filename': message.filename,
                    'line': line,
                    'col': message.col + 1,
                    'type': message.__class__.__name__,
                    'text': message.message % message.message_args,
                }

            def syntaxError(self, filename, msg, lineno, offset, text):
                self.issues[lineno - 1] = {
                    'filename': filename, 'line': lineno - 1, 'col': offset,
                    'type': 'SyntaxError', 'text': msg,
                }

        rep = CustomReporter()
        check(self.toPlainText(), filename='main.py', reporter=rep)

        self.lint_output = rep.issues
        self.update_lint_extra_selections()

    def update_lint_extra_selections(self):
        self.lint_extra_selections = []
        for line in self.lint_output:
            lint_selection = QtWidgets.QTextEdit.ExtraSelection()
            lint_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
            lint_selection.cursor = self.textCursor()
            lint_selection.cursor.setPosition(self.document().findBlockByLineNumber(line).position())
            lint_selection.format.setBackground(QtGui.QColor(200, 0, 0))
            self.lint_extra_selections.append(lint_selection)

    def update_cursor_extra_selections(self):
        self.cursor_extra_selections = []
        
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.SelectionType.WordUnderCursor)
            if not cursor.selectedText().isidentifier():
                return
        
        if cursor.selectedText().strip() == '':
            return
        
        matches = re.finditer(rf'{re.escape(cursor.selectedText())}', self.toPlainText())
        for match in matches:
            span = match.span()
            word_under_cursor_selection = QtWidgets.QTextEdit.ExtraSelection()
            word_under_cursor_selection.cursor = self.textCursor()
            word_under_cursor_selection.cursor.setPosition(span[0])
            word_under_cursor_selection.cursor.setPosition(span[1], word_under_cursor_selection.cursor.MoveMode.KeepAnchor)
            word_under_cursor_selection.format.setBackground(QtGui.QColor(70, 70, 70))
            self.cursor_extra_selections.append(word_under_cursor_selection)

    def update_extra_selections(self):
        self.setExtraSelections(self.cursor_extra_selections + self.lint_extra_selections)

    def update_lint_tooltip(self):
        cursor = self.cursorForPosition(self.mapFromGlobal(self.cursor().pos()))
        block = cursor.block()
        line_number = block.blockNumber()

        if self.lint_output.get(line_number) is not None and self.rect().contains(self.mapFromGlobal(self.cursor().pos())) and self.hasFocus():
            self.lint_tooltip.setText(self.lint_output[line_number]['text'])
            self.lint_tooltip.setFont(self.main_font)
            self.lint_tooltip.show()
        else:
            self.lint_tooltip.hide()

    def set_highlight_completion(self, text):
        self.current_completion = text

    def on_text_changed(self):
        self.save()
        self.lint_code()

        self.completion_ran = False

        self.start_completion_worker()

    def start_completion_worker(self):
        if self.completion_ran:
            return

        if self.completion_worker is not None:
            return

        cursor = self.textCursor()
        source_code = self.toPlainText()
        position = cursor.position()

        self.completion_ran = True

        line, column = self.get_line_and_column(source_code, position)

        self.completion_worker = CompletionWorker(self.script, self.path, line, column)
        self.completion_worker_thread = QtCore.QThread()
        self.completion_worker.moveToThread(self.completion_worker_thread)
        self.completion_worker_thread.started.connect(self.completion_worker.run)
        self.completion_worker_thread.start()
        self.completion_worker.finished.connect(self.completion_worker_finished)

    def completion_worker_finished(self, output):
        self.completion_worker_thread.quit()
        self.completion_worker_thread.wait()
        self.completion_worker = None
        self.completion_worker_thread = None

        self.completion_output = output
        if self.completion_output:
            self.show_completions(self.completion_output)
        else:
            self.completer.popup().hide()

    def get_line_and_column(self, text, position):
        text_up_to_cursor = text[:position]
        lines = text_up_to_cursor.splitlines()
        line_number = len(lines)
        column_number = len(lines[-1]) if lines else 0
        return line_number, column_number

    def show_completions(self, completions):
        cursor = self.textCursor()
        if cursor.atStart():
            self.completer.popup().hide()
            return
        char = self.toPlainText()[cursor.position() - 1]
        if not (char.isidentifier() or char == '.'):
            self.completer.popup().hide()
            return

        self.completion_model.removeRows(0, self.completion_model.rowCount())
        for completion in completions:
            item = QtGui.QStandardItem(completion)
            item.setFont(self.main_font)
            self.completion_model.appendRow(item)
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect)
        self.completer.popup().scrollToTop()
        self.completer.popup().setAlternatingRowColors(True)
        self.completer.popup().setCurrentIndex(self.completion_model.index(0, 0))
        self.set_highlight_completion(self.completer.currentCompletion())

    def insert_completion(self, completion):
        # Add more steps and conditions if necessary
        cursor = self.textCursor()

        # To replace a word with the completion, we need to identify the word,
        # delete the word and insert the completion. However, identifying the word
        # may face some challenges.

        # When selecting a word under the cursor, the selection starts from the
        # character to the right of the cursor. In cases like (fo|.bar) where the
        # cursor is at '|', inserting a completion can produce incorrect results
        # (e.g., "fofoobar" instead of "foo.bar").

        if self.completion_output.get(completion) is not None:
            if self.completion_output[completion]['prefix_length'] > 0:
                cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor)
        else:
            return

        # When cursor is located between two symbols (foo.|.bar), the previous case won't
        # catch it since there is a prefix length of 0. Thus, we find the char to the right
        # of the cursor, if it is not alphanumeric or _, we need not delete the word under cursor.

        if cursor.positionInBlock() != len(cursor.block().text()):
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor)
            selected_char = cursor.selectedText()
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor)

            if selected_char.isalnum() or selected_char == '_':
                cursor.select(cursor.SelectionType.WordUnderCursor)
                if cursor.selectedText():
                    cursor.deleteChar()
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        self.completer.popup().hide()

    def save(self):
        with open(self.path / self.script, 'w') as fp:
            fp.write(self.toPlainText())
