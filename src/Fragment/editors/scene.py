from widgets.node_tree import NodeTree
from widgets.property_list import PropertyList
from widgets.viewport import Viewport
from dialogs.new_node_selection import NewNodeSelectionDialog
from dialogs.text_selection import TextSelectionDialog
from node_properties.loader import tree as node_properties
from .editor import Editor
from utils import get_node_data, string_to_node_data, node_data_to_string, generate_uuid
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
import os
import shutil
import copy


class SceneEditor(Editor):
    def __init__(self, path, editor, scene):
        super().__init__(path, editor, scene)

        self.scene = scene
        self.current_node = None

        fp = open(self.scene)
        content = fp.read()
        fp.close()

        self.nodes = string_to_node_data(eval(content))

        self.central_widget = QtWidgets.QWidget()
        self.central_widget_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.menu_bar = QtWidgets.QFrame(self)
        self.menu_bar.setFixedHeight(34)
        self.menu_bar_layout = QtWidgets.QHBoxLayout(self.menu_bar)
        self.run_button = QtWidgets.QPushButton()
        self.run_button.setFixedHeight(20)
        self.run_button.setIcon(QtGui.QIcon('assets/ui_icons/play.png'))
        self.run_button.setIconSize(QtCore.QSize(10, 10))
        self.run_button.clicked.connect(self.run)
        self.menu_bar_layout.addWidget(self.run_button)
        self.central_widget_layout.addWidget(self.menu_bar)

        self.node_tree_dock = QtWidgets.QDockWidget()
        self.node_tree_dock.setWindowTitle('Node Tree')
        self.node_tree_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.node_tree_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.node_tree = NodeTree()
        self.node_tree.setExpandsOnDoubleClick(False)
        self.node_tree.itemClicked.connect(lambda item, column: self.set_current_node(item.node_path))
        self.node_tree.itemDoubleClicked.connect(lambda item, column: self.open_script(column, item.node_path))
        self.node_tree.new_node_action.triggered.connect(self.gui_add_new_node)
        self.node_tree.new_nested_scene_action.triggered.connect(self.gui_add_nested_scene)
        self.node_tree.delete_node_action.triggered.connect(lambda: self.delete_node(self.current_node))
        self.node_tree.set_root_action.triggered.connect(lambda: self.gui_add_new_node(True))
        self.node_tree.rename_node_action.triggered.connect(self.gui_rename_node)
        self.node_tree.node_dragged_signal.connect(lambda sources, dest: self.reparent_nodes([item.node_path for item in sources], dest.node_path))
        self.node_tree_dock.setWidget(self.node_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.node_tree_dock)

        self.property_list_dock = QtWidgets.QDockWidget()
        self.property_list_dock.setWindowTitle('Property List')
        self.property_list_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.property_list_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.property_list = PropertyList(self.nodes, self.scene_property_changed, self.path)
        self.property_list_dock.setWidget(self.property_list)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_list_dock)

        if not self.nodes:
            self.node_tree.with_root = False

        self.viewport = Viewport(self)
        self.central_widget_layout.addWidget(self.viewport)

        self.setCentralWidget(self.central_widget)

        self.load_node_tree()

    def gui_add_new_node(self, ignore_parent=False):
        dialog = NewNodeSelectionDialog(self, ignore_parent)

        if ignore_parent:
            dialog.accepted.connect(lambda: self.new_node(dialog.node_tree.currentItem().text(0), os.path.basename(self.scene).split('.')[0], ''))

        else:
            dialog.accepted.connect(lambda: self.new_node(dialog.node_tree.currentItem().text(0), (dialog.name_edit.text() if dialog.name_edit.text() else dialog.node_tree.currentItem().text(0)), (self.node_tree.currentItem().node_path if self.node_tree.currentItem() else self.node_tree.topLevelItem(0).node_path)))

        if not ignore_parent:
            dialog.info_label.setText(f'Will be child of:\n{(self.node_tree.currentItem().node_path if self.node_tree.currentItem() else self.node_tree.topLevelItem(0).node_path)}')

        dialog.exec()

    def gui_add_nested_scene(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Import Scene', self.path, 'Fragment Scenes (*.fscene)')[0]
        if not path:
            return
        self.new_nested_scene(path, (self.node_tree.currentItem().node_path if self.node_tree.currentItem() else self.node_tree.topLevelItem(0).node_path))

    def new_node(self, type, name, parent):
        data = get_node_data(name, generate_uuid(), parent, type, copy.deepcopy(node_properties[type]))
        self.nodes[list(data.keys())[0]] = data[list(data.keys())[0]]
        self.add_node_to_tree(list(data.keys())[0])

    def new_nested_scene(self, dir, parent, old_data=None):
        if not os.path.exists(dir):
            return
        fp = open(dir)
        content = fp.read()
        fp.close()
        nodes = string_to_node_data(eval(content))

        for node_path in list(nodes.keys()):
            self.nodes[node_path] = nodes[node_path]
            if node_path.parent:
                self.nodes[node_path]['scene_root_node'] = self.nodes[node_path.parent]['scene_root_node']
            else:
                node_path.reparent_to(parent)
                self.nodes[node_path]['scene_root_node'] = node_path
            self.nodes[node_path]['changed_props'] = []
            self.nodes[node_path]['scene_path'] = dir

            new_old_node_path_map = {}
            if old_data is not None:
                for old_node in list(old_data.keys()):
                    if old_node.get_python_tag('uid') == node_path.get_python_tag('uid'):
                        new_old_node_path_map[node_path] = old_node

            if old_data is not None and new_old_node_path_map.get(node_path):
                self.nodes[node_path]['changed_props'] += old_data[new_old_node_path_map[node_path]]['changed_props']
                self.nodes[node_path]['changed_props'] = list(set(self.nodes[node_path]['changed_props']))
                for changed_prop in self.nodes[node_path]['changed_props']:
                    for category in self.nodes[node_path]['properties']:
                        try:
                            self.nodes[node_path]['properties'][category][changed_prop] = old_data[new_old_node_path_map[node_path]]['properties'][category][changed_prop]
                        except:
                            pass
            self.add_node_to_tree(node_path)

    def load_node_tree(self):
        self.node_tree.takeTopLevelItem(0)
        for path in self.nodes.keys():
            self.add_node_to_tree(path)

    def add_node_to_tree(self, node):
        self.nodes[node]['element'] = QtWidgets.QTreeWidgetItem([node.get_name(), ''])
        self.nodes[node]['element'].setIcon(0, QtGui.QIcon('assets/node_icons/' + self.nodes[node]['type'] + '.png'))
        if self.nodes[node]['script']:
            self.nodes[node]['element'].setIcon(1, QtGui.QIcon('assets/ui_icons/script.png'))
        else:
            self.nodes[node]['element'].setIcon(1, QtGui.QIcon('assets/ui_icons/add.png'))

        self.nodes[node]['element'].node_path = node
        parent = node.parent
        if not parent:
            self.node_tree.insertTopLevelItem(0, self.nodes[node]['element'])
        else:
            self.nodes[parent]['element'].addChild(self.nodes[node]['element'])

        type = self.nodes[node]['type']

        properties = {}

        for value in list(copy.deepcopy(self.nodes[node]['properties']).values()):
            properties = {**properties, **value}

        for key in list(properties.keys()):
            properties[key] = properties[key][0]
        if self.nodes[node].get('viewport_entity') is None:
            if node.parent:
                self.nodes[node]['viewport_entity'] = self.viewport.add_entity(type, self.nodes[node.parent]['viewport_entity'], properties, node)
            else:
                self.nodes[node]['viewport_entity'] = self.viewport.add_entity(type, self.viewport.scene, properties, node)

    def set_current_node(self, node):
        self.save_current_node_properties()
        self.current_node = node
        self.property_list.set_current_node(node)
        self.viewport.selected_entity = self.nodes[node]['viewport_entity']

    def scene_property_changed(self, node, p):
        self.save_current_node_properties()
        properties = {}

        property = p.text(0)

        for value in list(copy.deepcopy(self.nodes[node]['properties']).values()):
            properties = {**properties, **value}

        for key in list(properties.keys()):
            properties[key] = properties[key][0]

        self.nodes[node]['viewport_entity']._properties = properties
        self.nodes[node]['viewport_entity']._property_init()

        if self.nodes[node].get('changed_props') is None:
            return
        if property not in self.nodes[node]['changed_props']:
            self.nodes[node]['changed_props'].append(property)

        font = p.font(0)
        font.setBold(True)
        font.setItalic(True)
        p.setFont(0, font)

    def save_current_node_properties(self):
        if not self.current_node:
            return
        if self.nodes.get(self.current_node) is None:
            return

        for i in range(self.property_list.topLevelItem(0).childCount()):
            child = self.property_list.topLevelItem(0).child(i)
            for j in range(child.childCount()):
                prop_child = child.child(j)
                self.nodes[self.current_node]['properties'][child.text(0)][prop_child.text(0)] = [self.property_list.itemWidget(prop_child, 1).get(), self.property_list.itemWidget(prop_child, 1).type]
                try:
                    eval(self.nodes[self.current_node]['properties'][child.text(0)][prop_child.text(0)])
                    self.nodes[self.current_node]['properties'][child.text(0)][prop_child.text(0)] = eval(self.nodes[self.current_node]['properties'][child.text(0)][prop_child.text(0)])

                except:
                    pass

    def delete_node(self, node):
        for i in range(self.nodes[node]['element'].childCount()):
            self.nodes[node]['element'].removeChild(self.nodes[node]['element'].child(i))

        if node == list(self.nodes.keys())[0]:
            self.node_tree.takeTopLevelItem(0)

        else:
            if self.nodes.get(node.parent) is not None:
                self.nodes[node.parent]['element'].removeChild(self.nodes[node]['element'])

        self.nodes[node]['viewport_entity'].destroy()
        self.viewport.entities.remove(self.nodes[node]['viewport_entity'])

        for path in list(self.nodes.keys()):
            if node.is_ancestor_of(path) or path == node:
                self.nodes.pop(path)
        if len(self.nodes.keys()) > 0:
            self.set_current_node(list(self.nodes.keys())[0])
        else:
            self.current_node = None
            self.property_list.takeTopLevelItem(0)
            self.node_tree.with_root = False

    def rename_node(self, node, name):
        node.set_name(name)
        self.nodes[node]['element'].setText(0, name)

    def gui_rename_node(self):
        node = self.node_tree.currentItem().node_path
        dialog = TextSelectionDialog(self, 'Rename Node', 'New Name')
        dialog.accepted.connect(lambda: self.rename_node(node, dialog.line_edit.text()))
        dialog.exec()

    def reparent_nodes(self, nodes, parent):
        for node in nodes:
            if (self.nodes[node].get('scene_root_node') is not None and self.nodes[node].get('scene_root_node') != node) or self.nodes[parent].get('scene_root_node') is not None:
                continue
            if node.parent is not None:
                self.nodes[node.parent]['element'].removeChild(self.nodes[node]['element'])
            node.reparent_to(parent)
            self.nodes[parent]['element'].addChild(self.nodes[node]['element'])
        self.sort_nodes()

    def sort_nodes(self):
        node_string_path_map = {}
        sorted_nodes = {}
        for node in self.nodes:
            node_string_path_map[str(node)] = node
        sorted_string_paths = list(sorted(node_string_path_map))
        for string_path in sorted_string_paths:
            node = node_string_path_map[string_path]
            sorted_nodes[node] = self.nodes[node]
        self.nodes = sorted_nodes

    def reload_viewport_entities(self):
        list(self.nodes.values())[0]['viewport_entity'].destroy()
        self.viewport.entities = []
        for node in list(self.nodes.keys()):
            type = self.nodes[node]['type']

            properties = {}

            for value in list(copy.deepcopy(self.nodes[node]['properties']).values()):
                properties = {**properties, **value}

            for key in list(properties.keys()):
                if properties[key][1] == 'path':
                    properties[key][0] = self.path + '/' + properties[key][0]
                elif properties[key][1] == 'path_dict':
                    for name in list(properties[key][0].keys()):
                        properties[key][0][name] = self.path + '/' + properties[key][0][name]
                properties[key] = properties[key][0]

            if node.parent:
                self.nodes[node]['viewport_entity'] = self.viewport.add_entity(type, self.nodes[node.parent]['viewport_entity'], properties, node)
            else:
                self.nodes[node]['viewport_entity'] = self.viewport.add_entity(type, self.viewport.scene, properties, node)

    def open_script(self, column, node):
        if column != 1:
            return
        if self.nodes[node]['type'] == 'Scene':
            return
        if not self.nodes[node]['script']:
            path = QtWidgets.QFileDialog.getSaveFileName(self, 'New Script', self.path)[0]
            if not path:
                return
            path += '.py'
            shutil.copy('python_file/main.py', path)
            fp = open(path, 'w')
            fp.write(f'# Node Script\nimport fragment.nodes.{self.nodes[node]["type"].lower()}\n\n\nclass Node(fragment.nodes.{self.nodes[node]["type"].lower()}.{self.nodes[node]["type"]}):\n    pass\n')
            fp.close()
            self.nodes[node]['script'] = path
            self.nodes[node]['element'].setIcon(1, QtGui.QIcon('assets/ui_icons/script.png'))

        self.open_script_(self.nodes[node]['script'])

    def open_script_(self, script):
        self.editor.open(script)

    def run(self):
        self.editor.task_manager.new_task('execute_scene', [self])

    def save(self):
        self.save_current_node_properties()

        elements = []
        for path in self.nodes.keys():
            elements.append(self.nodes[path]['element'])
            self.nodes[path]['element'] = None

        viewport_entities = []
        for node in list(self.nodes.keys()):
            viewport_entities.append(self.nodes[node]['viewport_entity'])
            self.nodes[node].pop('viewport_entity')
        fp = open(self.scene, 'w')
        fp.write(str(node_data_to_string(self.nodes)))
        fp.close()

        for i, path in enumerate(self.nodes.keys()):
            self.nodes[path]['element'] = elements[i]

        for i, node in enumerate(self.nodes.keys()):
            self.nodes[node]['viewport_entity'] = viewport_entities[i]

    def _close(self):
        self.save()

    def _reload(self):
        self.save()

        if self.current_node is not None:
            self.set_current_node(self.current_node)

        scene_root_nodes = []
        for node in list(self.nodes.keys()):
            if self.nodes[node].get('changed_props') is not None:
                if self.nodes[node]['scene_root_node'] not in scene_root_nodes:
                    scene_root_nodes.append(self.nodes[node]['scene_root_node'])

        for node in scene_root_nodes:
            data = self.nodes[node]['scene_path'], node.parent
            elements = []

            for path in self.nodes.keys():
                elements.append(self.nodes[path]['element'])
                self.nodes[path]['element'] = None

            viewport_entities = []
            for node_ in list(self.nodes.keys()):
                viewport_entities.append(self.nodes[node_]['viewport_entity'])
                self.nodes[node_].pop('viewport_entity')

            old_data = copy.deepcopy(self.nodes)

            for i, path in enumerate(self.nodes.keys()):
                self.nodes[path]['element'] = elements[i]

            for i, node_ in enumerate(self.nodes.keys()):
                self.nodes[node_]['viewport_entity'] = viewport_entities[i]

            self.delete_node(node)
            self.new_nested_scene(*data, old_data=old_data)

    def _destroy(self):
        self.viewport.on_destroy()
