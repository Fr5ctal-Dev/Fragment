from ..text_selection import TextSelectionDialog
import re

PATTERN = r'^[A-Za-z0-9_.-]+$'


class FileRenameDialog(TextSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'Rename File', 'File Name')

    def validate_input(self, text):
        if not re.match(PATTERN, text):
            self.disable_continue()
            return
        super().validate_input(text)
    
    @property
    def file_name(self) -> str:
        return self.input_text
