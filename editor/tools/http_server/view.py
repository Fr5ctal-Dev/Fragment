from PySide6 import QtWidgets, QtWebEngineWidgets, QtGui, QtCore
import sys

port = sys.argv[1]
app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()

view = QtWebEngineWidgets.QWebEngineView()
view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
view.load(f'http://localhost:{port}')

devtools = QtWebEngineWidgets.QWebEngineView()
devtools.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
view.page().setDevToolsPage(devtools.page())

devtools_dock = QtWidgets.QDockWidget('DevTools', window)
devtools_dock.setWidget(devtools)
devtools.page().windowCloseRequested.connect(devtools_dock.hide)
devtools_dock.setAllowedAreas(QtCore.Qt.DockWidgetArea.RightDockWidgetArea | QtCore.Qt.DockWidgetArea.LeftDockWidgetArea)
window.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, devtools_dock)
devtools_dock.hide()

menu_bar = window.menuBar()
debug_menu = menu_bar.addMenu('Debug')
open_devtools_action = QtGui.QAction('Open DevTools', window)
open_devtools_action.triggered.connect(devtools_dock.show)
debug_menu.addAction(open_devtools_action)

window.setCentralWidget(view)
window.resize(1200, 800)
window.setWindowTitle('Preview')
window.show()
app.exec()
