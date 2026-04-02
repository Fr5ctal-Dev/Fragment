from ..text_selection import TextSelectionDialog


class NewSceneDialog(TextSelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New Scene', 'Scene Name')

    @property
    def scene_name(self):
        return self.input_text + '.fscene'
