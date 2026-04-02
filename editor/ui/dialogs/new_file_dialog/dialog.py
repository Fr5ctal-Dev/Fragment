from ..text_selection import TextSelectionDialog


class NewFileDialog(TextSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New File', 'File Name')

    @property
    def file_name(self):
        return self.input_text
