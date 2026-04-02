from ..text_selection import TextSelectionDialog


class NewScriptDialog(TextSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New Script', 'Script Name')

    @property
    def script_name(self):
        return self.input_text + '.js'
