from PySide6 import QtWidgets, QtGui, QtCore


class NodeTree(QtWidgets.QTreeWidget):
    node_dragged_signal = QtCore.Signal(list, QtWidgets.QTreeWidgetItem) # Sources, Dest
    def __init__(self):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(['Name', 'Script'])

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.set_root_action = QtGui.QAction('Set Root Node', self)
        self.new_node_action = QtGui.QAction('New Node', self)
        self.new_nested_scene_action = QtGui.QAction('New Scene', self)
        self.delete_node_action = QtGui.QAction('Delete', self)
        self.rename_node_action = QtGui.QAction('Rename', self)

        self.with_root = True

    def contextMenuEvent(self, event):
        if self.currentItem() is not None:
            self.itemClicked.emit(self.currentItem(), 0)

        context_menu = QtWidgets.QMenu(self)
        if self.with_root:
            self.set_root_action.setEnabled(False)
            self.new_node_action.setEnabled(True)
            self.new_nested_scene_action.setEnabled(True)
        else:
            self.set_root_action.setEnabled(True)
            self.new_node_action.setEnabled(False)
            self.new_nested_scene_action.setEnabled(False)

        if self.currentItem() is not None:
            self.delete_node_action.setEnabled(True)
            self.rename_node_action.setEnabled(True)
        else:
            self.delete_node_action.setEnabled(False)
            self.rename_node_action.setEnabled(False)

        new_menu = context_menu.addMenu('New')
        new_menu.addAction(self.new_node_action)
        new_menu.addAction(self.new_nested_scene_action)

        context_menu.addAction(self.delete_node_action)
        context_menu.addAction(self.rename_node_action)
        context_menu.addAction(self.set_root_action)

        context_menu.exec(self.mapToGlobal(event.pos()))

    def dragEnterEvent(self, event):
        if event.source() is self:
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        src = event.source()

        dragged_items = src.selectedItems()

        drop_pos = event.position().toPoint()
        dest_item = self.itemAt(drop_pos)

        self.node_dragged_signal.emit(dragged_items, dest_item)

        event.ignore()

    def insertTopLevelItem(self, index, item):
        super().insertTopLevelItem(index, item)
        self.with_root = True
