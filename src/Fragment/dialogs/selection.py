from .dialog import Dialog
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class SelectionDialog(Dialog):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setWindowTitle(title)

        self.title_label = QtWidgets.QLabel()
        self.title_label.setText(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.central_layout)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.accept_button = QtWidgets.QPushButton()
        self.accept_button.setText('Confirm')
        self.accept_button.clicked.connect(self.accept)
        self.accept_button.setEnabled(False)
        self.accept_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.button_layout.addWidget(self.accept_button)

        self.reject_button = QtWidgets.QPushButton()
        self.reject_button.setText('Cancel')
        self.reject_button.clicked.connect(self.reject)
        self.reject_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.button_layout.addWidget(self.reject_button)

    def enable_continue(self):
        self.accept_button.setEnabled(True)

    def disable_continue(self):
        self.accept_button.setEnabled(False)
