from .tool_tip import Tooltip
import jedi
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from pyflakes.api import check as pyflakes_check
from pyflakes.reporter import Reporter
import io


class Highlighter(QtGui.QSyntaxHighlighter):
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

    def lint_code(self, source, filename = 'main.py'):
        results = {}
        lines = source.splitlines()

        class RangeReporter(Reporter):
            def __init__(self):
                super().__init__(io.StringIO(), io.StringIO())

            def syntaxError(self, filename, msg, lineno, offset, text):
                start = offset - 1
                end = start + 1
                lineno -= 1
                results[lineno] = {
                    'filename': filename,
                    'lineno': lineno,
                    'start': start,
                    'end': end,
                    'message': msg
                }

            def flake(self, message):
                lineno = message.lineno
                lineno -= 1
                line = lines[lineno] if 1 <= lineno + 1 <= len(lines) else ''
                name = message.message_args[0] if message.message_args else None

                if name and name in line:
                    start = line.index(name)
                    end = start + len(name)
                elif hasattr(message, 'node') and hasattr(message.node, 'col_offset'):
                    start = message.node.col_offset
                    end = getattr(message.node, 'end_col_offset', start + 1)
                else:
                    start = 0
                    end = 1

                text = message.message % message.message_args
                results[lineno] = {
                    'filename': message.filename,
                    'lineno': lineno,
                    'start': start,
                    'end': end,
                    'message': text
                }

        pyflakes_check(source, filename, RangeReporter())
        return results


class ScriptEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, script, path):
        super().__init__()
        self.script = script
        self.path = path

        with open(self.script) as fp:
            self.insertPlainText(fp.read())

        font = QtGui.QFont('Consolas', 12)

        self.setFont(font)
        self.setLineWrapMode(self.LineWrapMode.NoWrap)
        self.lint_tooltip = Tooltip()
        self.lint_tooltip.setFont(font)
        self.lint_tooltip.hide()
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completion_model = QtGui.QStandardItemModel()
        self.completer.setModel(self.completion_model)
        self.completer_highlight = None
        self.textChanged.connect(self.on_text_changed)
        self.completer.activated.connect(self.insert_completion)
        self.completer.highlighted.connect(self.set_highlight_completion)
        self.previous_text = None
        self.highlighter = Highlighter(self.document(), script)
        self.mouse_position = QtCore.QPoint()
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_linting)
        self.update_timer.timeout.connect(self.update_tick)
        self.update_timer.start(10)

        self.lint_worker_running = False
        self.lint_worker = None # Used to store lint worker in memory so that it does not get garbage collected
        self.lint_worker_thread = None
        self.lint_output = None

    def set_highlight_completion(self, text):
        self.completer_highlight = text

    def on_text_changed(self):
        if (self.previous_text is not None) and (self.toPlainText() == self.previous_text):
            return
        self.previous_text = self.toPlainText()
        self.save()
        cursor = self.textCursor()
        current_text = self.toPlainText()
        position = cursor.position()
        completions = self.get_completions(current_text, position)
        if completions:
            self.show_completions(completions)
        else:
            self.completer.popup().hide()

    def update_tick(self):
        self.update_tooltip_based_on_cursor()
        self.lint()

    def update_linting(self):
        if self.lint_output is None:
            return
        cursor = self.textCursor()
        extra_selections = []
        if cursor.block().blockNumber() not in self.lint_output.keys():
            extra_selection = QtWidgets.QTextEdit.ExtraSelection()
            extra_selection.cursor = cursor
            extra_selection.format.setBackground(QtGui.QColor(50, 50, 50))
            extra_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
            extra_selections.append(extra_selection)
        for line_number in self.lint_output.keys():
            lint_selection = QtWidgets.QTextEdit.ExtraSelection()
            lint_selection.cursor = self.textCursor()
            lint_selection.cursor.setPosition(self.document().findBlockByLineNumber(line_number).position() + self.lint_output[line_number]['start'])
            lint_selection.cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.MoveMode.KeepAnchor, self.lint_output[line_number]['end'] - self.lint_output[line_number]['start'])
            lint_selection.format.setFontUnderline(True)
            lint_selection.format.setUnderlineStyle(lint_selection.format.UnderlineStyle.WaveUnderline)

            lint_selection.format.setUnderlineColor(QtGui.QColor(255, 50, 50))
            extra_selections.append(lint_selection)
        self.setExtraSelections(extra_selections)

    def mouseMoveEvent(self, event):
        self.mouse_position = event.pos()
        super().mouseMoveEvent(event)

    def update_tooltip_based_on_cursor(self):
        cursor = self.cursorForPosition(self.mapFromGlobal(self.cursor().pos()))
        column = cursor.columnNumber()
        block = cursor.block()
        line_number = block.blockNumber()
        if self.lint_output and line_number in self.lint_output and self.hasFocus() and column in range(self.lint_output[line_number]['start'], self.lint_output[line_number]['end'] + 1) and self.rect().contains(self.mapFromGlobal(self.cursor().pos())):
            lint_info = self.lint_output[line_number]
            tooltip_text = lint_info['message']
            self.lint_tooltip.setFont(QtGui.QFont('Consolas', 11))
            self.lint_tooltip.setText(tooltip_text)
            self.lint_tooltip.adjustSize()
            self.lint_tooltip.show()
        else:
            self.lint_tooltip.hide()

    def get_completions(self, source_code, position):
        line, column = self.get_line_and_column(source_code, position)
        try:
            if (source_code[position - 1] == ' ') or (self.textCursor().atBlockStart()):
                return []
        except:
            return []
        script = jedi.Script(path=self.script, project=jedi.Project(self.path))
        completions = script.complete(line=line, column=column)
        comps = []
        for completion in completions:
            if completion.complete:
                comps.append(completion.name)
        return comps

    def get_line_and_column(self, text, position):
        text_up_to_cursor = text[:position]
        lines = text_up_to_cursor.splitlines()
        line_number = len(lines)
        column_number = len(lines[-1]) if lines else 0
        return line_number, column_number

    def show_completions(self, completions):
        self.completion_model.removeRows(0, self.completion_model.rowCount())
        completions = completions[:min(len(completions), 10)]
        for completion in completions:
            item = QtGui.QStandardItem(QtGui.QIcon('assets/file_icons/script.png'), completion)
            item.setFont(QtGui.QFont('Consolas', 11))
            self.completion_model.appendRow(item)
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect)
        self.set_highlight_completion(self.completer.currentCompletion())

    def insert_completion(self, completion):
        cursor = self.textCursor()
        if (not cursor.positionInBlock() == 0) and cursor.block().text().strip():
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, 1)
        cursor.select(cursor.SelectionType.WordUnderCursor)
        cursor.deleteChar()
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        self.completer.popup().hide()

    def lint(self):
        if self.lint_worker is not None: # Previous lint process is not finished
            return

        self.lint_worker = LintWorker(self.toPlainText())
        self.lint_worker_thread = QtCore.QThread()
        self.lint_worker.moveToThread(self.lint_worker_thread)
        self.lint_worker_thread.started.connect(self.lint_worker.run)
        self.lint_worker_thread.start()
        self.lint_worker.finished.connect(self.lint_finished)

    def lint_finished(self, data):
        self.lint_worker_thread.quit()
        self.lint_worker_thread.wait()
        self.lint_worker = None
        self.lint_worker_thread = None
        self.lint_output = data

    def keyPressEvent(self, event):
        self.ensureCursorVisible()
        if self.completer.popup().isVisible():
            if event.key() == Qt.Key.Key_Tab:
                event.accept()
                self.insert_completion(self.completer_highlight)
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
                spaces = len(selected_text) - len(selected_text.lstrip(' '))
                if selected_text.strip() == '':
                    add_spaces = 4 - spaces % 4
                    cursor.beginEditBlock()
                    cursor.setPosition(position, cursor.MoveMode.KeepAnchor)
                    cursor.insertText(' ' * add_spaces)
                    cursor.endEditBlock()
                    event.accept()
                    return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            spaces = 0
            for c in cursor.block().text():
                if c == ' ':
                    spaces += 1
                else:
                    break
            if cursor.block().text().endswith(':'):
                spaces += 4
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
            spaces = len(selected_text) - len(selected_text.lstrip(' '))
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

    def save(self):
        with open(self.script, 'w') as fp:
            fp.write(self.toPlainText())