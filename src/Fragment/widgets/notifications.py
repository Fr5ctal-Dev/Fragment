from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class Notification(QTreeWidgetItem):
    def __init__(self, title, message):
        self.title = title
        self.message = message
        super().__init__([self.title, self.message])


class Notifications(QTreeWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setColumnCount(2)
        self.setHeaderLabels(['Title', 'Message'])

    def new_notification(self, title, message):
        notification = Notification(title, message)
        self.addTopLevelItem(notification)
