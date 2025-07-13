from .editor_widget import EditorWidget
from PySide6.QtWidgets import QTreeWidget, QPushButton, QTreeWidgetItem, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QIcon


class BaseListEditor(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_layout = QVBoxLayout()
        self.main_layout.addLayout(self.list_layout)

        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon('assets/ui_icons/add.png'))
        self.remove_button = QPushButton()
        self.remove_button.setIcon(QIcon('assets/ui_icons/minus.png'))
        self.remove_button.clicked.connect(self.remove_current_item)
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.list_layout.addLayout(self.button_layout)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(['', ''])
        self.list_layout.addWidget(self.tree_widget)

        self.items = [] # Containing all TreeWidgetItems

    def remove_item(self, item):
        self.tree_widget.takeTopLevelItem(self.tree_widget.indexOfTopLevelItem(item))
        self.items.remove(item)

    def remove_current_item(self):
        current_item = self.tree_widget.currentItem()
        if current_item is not None:
            self.remove_item(current_item)
            self.change_property()

    def new_item(self):
        item = QTreeWidgetItem(['' for i in range(self.tree_widget.columnCount())])
        self.tree_widget.addTopLevelItem(item)
        self.items.append(item)
        return item
