from editor.tasks import TASKS
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal


class TaskListWidget(QtWidgets.QWidget):
    delete_task = Signal(QtWidgets.QWidget)
    def __init__(self, task):
        super().__init__()
        self.tree_widget_item = None
        self.task = task

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.label.setText(self.task.name)
        self.main_layout.addWidget(self.label)

        self.progress_bar = QtWidgets.QProgressBar()
        if not self.task.determinate:
            self.progress_bar.setRange(0, 0)
        self.main_layout.addWidget(self.progress_bar)

        self.task.finished.connect(self.finish)
        QtCore.QTimer.singleShot(0, self.task.run)

    def finish(self):
        self.delete_task.emit(self)

    def terminate(self):
        self.task.terminate()


class TaskManager(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.task_list = QtWidgets.QTreeWidget()
        self.task_list.setColumnCount(1)
        self.task_list.setHeaderLabels([''])
        self.main_layout.addWidget(self.task_list)

    def new_task(self, name, args):
        task = TASKS[name](*args)

        task_list_widget = TaskListWidget(task)

        def notify():
            self.editor.notifications.new_notification('Task finished', f'Task "{name}" has finished.')

        task_list_widget.task.finished.connect(notify)
        tree_widget_item = QtWidgets.QTreeWidgetItem([''])
        task_list_widget.tree_widget_item = tree_widget_item
        self.task_list.addTopLevelItem(tree_widget_item)
        self.task_list.setCurrentItem(tree_widget_item)
        self.task_list.setItemWidget(tree_widget_item, 0, task_list_widget)

        task_list_widget.delete_task.connect(self.delete_task_widget)

    def delete_task_widget(self, task_list_widget):
        self.task_list.takeTopLevelItem(self.task_list.indexOfTopLevelItem(task_list_widget.tree_widget_item))

    def terminate_task(self, task_list_widget):
        task_list_widget.terminate()
        self.delete_task_widget(task_list_widget)

    def terminate_all_tasks(self):
        for i in range(self.task_list.topLevelItemCount()):
            item = self.task_list.topLevelItem(0)
            task_list_widget = self.task_list.itemWidget(item, 0)
            self.terminate_task(task_list_widget)

    def cleanup(self):
        self.terminate_all_tasks()
