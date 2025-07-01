from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
from PySide6 import QtGui
from library import Library
from splash_screen import SplashScreen
from qdarktheme import setup_theme
import sys
import platform

if __name__ == '__main__':
    app = QApplication()
    setup_theme()
    if platform.system() == 'Windows':
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon_win.ico'))
    else:
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon.png'))

    window = QWidget()
    window.setWindowTitle('Fragment Library')
    window_layout = QStackedLayout(window)

    library = Library()
    window_layout.addWidget(library)

    splash = SplashScreen()
    splash.splash_ended.connect(lambda: window_layout.setCurrentWidget(library))
    window_layout.addWidget(splash)

    window_layout.setCurrentWidget(splash)

    window.show()

    sys.exit(app.exec())
