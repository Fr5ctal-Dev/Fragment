from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Signal
import importlib


class TaskListWidget(QtWidgets.QWidget):
    delete_task = Signal(QtWidgets.QWidget)
    def __init__(self, task):
        super().__init__()
        self.tree_widget_item = None
        self.task = task
        self.thread = QtCore.QThread()
        self.task.moveToThread(self.thread)
        self.thread.started.connect(self.task.run)
        self.thread.start()

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.label.setText(self.task.name)
        self.main_layout.addWidget(self.label)

        self.progress_bar = QtWidgets.QProgressBar()
        if not self.task.determinate:
            self.progress_bar.setRange(0, 0)
        self.main_layout.addWidget(self.progress_bar)

        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setIcon(QtGui.QIcon('assets/ui_icons/trash.png'))
        self.delete_button.clicked.connect(lambda: self.delete_task.emit(self))
        self.delete_button.setEnabled(False)
        self.main_layout.addWidget(self.delete_button)

        self.task.finished.connect(self.progress_bar.hide)
        self.task.finished.connect(lambda: self.delete_button.setEnabled(True))


class Console(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)
        self.main_layout.addWidget(self.console)

        self.error_console = QtWidgets.QTextEdit()
        self.error_console.setReadOnly(True)
        self.main_layout.addWidget(self.error_console)



class TaskManager(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.tasks = {None: None}
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.task_list = QtWidgets.QTreeWidget()
        self.task_list.setColumnCount(1)
        self.task_list.setHeaderLabels([''])
        self.task_list.currentItemChanged.connect(lambda current, previous: self.stacked_widget.setCurrentWidget(self.tasks[self.task_list.itemWidget(current, 0)]))
        self.main_layout.addWidget(self.task_list)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

    def new_task(self, name, args):
        module = importlib.import_module(f'tasks.{name}')
        get_task = eval(f'module.{name}')
        task = get_task(*args)

        task_list_widget = TaskListWidget(task)

        def notify():
            QtCore.QTimer.singleShot(2000, lambda: self.editor.notifications.new_notification('Task finished', f'Task "{name}" has finished.'))

        task_list_widget.task.finished.connect(notify)
        tree_widget_item = QtWidgets.QTreeWidgetItem([''])
        task_list_widget.tree_widget_item = tree_widget_item
        self.task_list.addTopLevelItem(tree_widget_item)
        self.task_list.setCurrentItem(tree_widget_item)
        self.task_list.setItemWidget(tree_widget_item, 0, task_list_widget)

        console = Console()
        self.stacked_widget.addWidget(console)
        self.stacked_widget.setCurrentWidget(console)
        self.tasks[task_list_widget] = console

        def new_text(chunk):
            console.console.setReadOnly(False)
            console.console.insertPlainText(chunk)
            console.console.setReadOnly(True)
            console.console.verticalScrollBar().setValue(console.console.verticalScrollBar().maximum())

        def new_error(chunk):
            console.error_console.setReadOnly(False)
            console.error_console.insertPlainText(chunk)
            console.error_console.setReadOnly(True)
            console.error_console.verticalScrollBar().setValue(console.error_console.verticalScrollBar().maximum())

        task.new_text_chunk.connect(new_text)
        task.new_error_chunk.connect(new_error)
        task_list_widget.delete_task.connect(self.delete_task)

    def delete_task(self, task_list_widget):
        console = self.tasks[task_list_widget]
        self.task_list.takeTopLevelItem(self.task_list.indexOfTopLevelItem(task_list_widget.tree_widget_item))
        self.stacked_widget.removeWidget(console)
