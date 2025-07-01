from .collection import Collection
from .float import Float
from PySide6.QtWidgets import QSpacerItem


class Coordinates(Collection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.collection_layout.addSpacerItem(QSpacerItem(3, 6))
        for i in range(3):
            self.add_editor(Float, [self.value[i], 'float'])
        self.collection_layout.addSpacerItem(QSpacerItem(3, 6))
