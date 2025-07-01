from .tool_tip import Tooltip
import jedi
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
import subprocess
import sys

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

class ScriptEditor(QtWidgets.QTextEdit):
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
        self.update_timer.timeout.connect(self.update_tick)
        self.update_timer.start(10)
        self.lint_process = None
        self.lint_output = None
        self.lint_timer = QtCore.QTimer()
        self.lint_timer.timeout.connect(self.lint)
        self.lint_timer.start(1)
        self.prev_lint_data = [None, None]

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
        if self.lint_output is None:
            return
        cursor = self.textCursor()
        extra_selections = []
        if cursor.block().blockNumber() not in self.lint_output.keys():
            extra_selection = self.ExtraSelection()
            extra_selection.cursor = cursor
            extra_selection.format.setBackground(QtGui.QColor(50, 50, 50))
            extra_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
            extra_selections.append(extra_selection)
        for line_number in self.lint_output.keys():
            lint_selection = self.ExtraSelection()
            lint_selection.cursor = self.textCursor()
            lint_selection.cursor.setPosition(self.document().findBlockByLineNumber(line_number).position() + self.lint_output[line_number][2][0])
            if self.lint_output[line_number][2][1] == -1:
                lint_selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
            else:
                lint_selection.cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.MoveMode.KeepAnchor, self.lint_output[line_number][2][1] - self.lint_output[line_number][2][0])
            lint_selection.format.setFontUnderline(True)
            lint_selection.format.setUnderlineStyle(lint_selection.format.UnderlineStyle.WaveUnderline)
            if self.lint_output[line_number][0] == 'E':
                lint_selection.format.setUnderlineColor(QtGui.QColor(255, 50, 50))
            else:
                lint_selection.format.setUnderlineColor(QtGui.QColor(255, 255, 0))
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
        if self.lint_output and line_number in self.lint_output and self.hasFocus() and column in range(*self.lint_output[line_number][2]):
            lint_info = self.lint_output[line_number]
            tooltip_text = lint_info[1]
            self.lint_tooltip.setFont(QtGui.QFont('Consolas', 11))
            self.lint_tooltip.setText(tooltip_text)
            self.lint_tooltip.adjustSize()
            self.lint_tooltip.show()
        else:
            self.lint_tooltip.hide()

    def get_completions(self, source_code, position):
        line, column = self.get_line_and_column(source_code, position)
        if (source_code[position - 1] == ' ') or (self.textCursor().atBlockStart()):
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
        if self.lint_process is not None:
            if self.lint_process.poll() is not None:
                output, error = self.lint_process.communicate()
                self.lint_output = {}
                self.lint_process = self.spawn_lint_process()
                for line in output.split('\n')[1:-1]:
                    if line and line[0] in 'WE':
                        try:
                            column = (int(line.split(';')[1].split(':')[0]), int(line.split(';')[1].split(':')[1]))
                        except ValueError:
                            column = (0, -1)
                        self.lint_output[int(line.split(';')[0][1:]) - 1] = [line[0], line.split(';')[2], column]
        else:
            self.lint_process = self.spawn_lint_process()
        self.update_tooltip_based_on_cursor()

    def spawn_lint_process(self):
        return subprocess.Popen(
            [sys.executable, '-m', 'pylint', '--msg-template={C}{line};{column}:{end_column};{msg_id}: {msg}', '-sn', self.script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

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