from editor.widgets.node_tree import NodeTree
from editor.widgets.inspector import Inspector
from .editor import Editor
from editor.utils.path import get_resource_path
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt


class SceneEditor(Editor):
    def __init__(self, path, editor, scene):
        super().__init__(path, editor, scene)

        self.scene = scene

        self.central_widget = QtWidgets.QWidget()
        self.central_widget_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.menu_bar = QtWidgets.QFrame(self)
        self.menu_bar.setFixedHeight(34)
        self.menu_bar_layout = QtWidgets.QHBoxLayout(self.menu_bar)
        self.run_button = QtWidgets.QPushButton()
        self.run_button.setFixedHeight(20)
        self.run_button.setIcon(QtGui.QIcon(get_resource_path('editor/assets/ui_icons/play.png')))
        self.run_button.setIconSize(QtCore.QSize(10, 10))
        self.run_button.clicked.connect(self.run)
        self.menu_bar_layout.addWidget(self.run_button)
        self.central_widget_layout.addWidget(self.menu_bar)

        self.node_tree_dock = QtWidgets.QDockWidget()
        self.node_tree_dock.setWindowTitle('Node Tree')
        self.node_tree_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.node_tree_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.node_tree = NodeTree(self)
        self.node_tree.setExpandsOnDoubleClick(False)
        self.node_tree_dock.setWidget(self.node_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.node_tree_dock)

        self.inspector_dock = QtWidgets.QDockWidget()
        self.inspector_dock.setWindowTitle('Inspector')
        self.inspector_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.inspector_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.inspector = Inspector(self)
        self.inspector_dock.setWidget(self.inspector)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

        #self.viewport = Viewport(self)
        #self.central_widget_layout.addWidget(self.viewport)

        self.setCentralWidget(self.central_widget)

        self.load_node_tree()

    def load_node_tree(self):
        with open(self.scene) as f:
            content = f.read()

        self.node_tree.load_from_scene_data(eval(content))

    def save(self):
        data = self.node_tree.save_to_scene_data()
        with open(self.scene, 'w') as f:
            f.write(str(data))

    def run(self):
        self.editor.task_manager.new_task('execute_scene', [self])

    def _close(self):
        self.save()
