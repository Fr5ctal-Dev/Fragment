from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal
from pathlib import Path
import json


class PropertyNameWidget(QtWidgets.QWidget):
    # A label widget that shows a blue stripe if overridden

    override_changed = Signal(object, object)

    def __init__(self, properties, text, overridden=False):
        super().__init__()
        self.node_properties = properties
        self.text = text
        self.display_text = text.split('/')[-1]
        self.overridden = False
        if overridden:
            self.override()
        
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stripe = QtWidgets.QWidget()
        self.stripe.setFixedWidth(5)
        self.main_layout.addWidget(self.stripe)

        self.label = QtWidgets.QLabel(self.display_text)
        self.main_layout.addWidget(self.label)

        self.override_action = QAction('Enable Override', self)
        self.override_action.triggered.connect(self.override)
        self.override_action.triggered.connect(lambda: self.override_changed.emit(True, self.text))
        
        self.unoverride_action = QAction('Disable Override', self)
        self.unoverride_action.triggered.connect(self.unoverride)
        self.unoverride_action.triggered.connect(lambda: self.override_changed.emit(False, self.text))

    def override(self):
        self.overridden = True
        self.show_stripe()

    def unoverride(self):
        self.overridden = False
        self.hide_stripe()

    def show_stripe(self):
        self.stripe.setStyleSheet('background-color: #4682b4;')

    def hide_stripe(self):
        self.stripe.setStyleSheet('background-color: none;')

    def contextMenuEvent(self, event):
        context_menu = QtWidgets.QMenu(self)

        if self.overridden:
            self.override_action.setEnabled(False)
            self.unoverride_action.setEnabled(True)
        else:
            self.override_action.setEnabled(True)
            self.unoverride_action.setEnabled(False)
        
        if self.node_properties.target_scene is None:
            self.override_action.setEnabled(False)
            self.unoverride_action.setEnabled(False)

        context_menu.addAction(self.override_action)
        context_menu.addAction(self.unoverride_action)
        context_menu.exec(self.mapToGlobal(event.pos()))


class BaseNodeProperties:
    def __init__(self, scene_editor, uuid, type):
        self.scene_editor = scene_editor
        self.type = type
        self.uuid = uuid

        self.target_scene = None # Scene path
        self.target_scene_node = None # Node path in target scene

        self.properties = self.default_properties
        self.property_tree = None
        self.property_tree_items = {} # name: item
        self.setup_property_tree()

    @property
    def default_properties(self):
        properties = {} # name: property
        return properties
    
    def set_property(self, name, value):
        self.properties[name].value = value

    def override_property(self, name):
        self.properties[name].scene_override = True
        if self.property_tree is not None:
            self.property_tree.itemWidget(self.property_tree_items[name], 0).override()
    
    def unoverride_property(self, name):
        self.properties[name].scene_override = False
        if self.property_tree is not None:
            self.property_tree.itemWidget(self.property_tree_items[name], 0).unoverride()

    def setup_property_tree(self):
        self.setup_property_editors()
        self.property_tree = QtWidgets.QTreeWidget()
        self.property_tree.setColumnCount(2)
        self.property_tree.setHeaderLabels(['Name', 'Value'])
        self.property_tree.setIndentation(10)

        property_groups = {}

        for prop in self.properties.values():
            prefix = ''
            for group in prop.name.split('/')[:-1]:
                prefix += group
                if prefix not in property_groups:
                    group_item = QtWidgets.QTreeWidgetItem([group, ''])
                    parent_item = property_groups[prefix.rsplit('/', 1)[0]] if '/' in prefix else None
                    if parent_item:
                        parent_item.addChild(group_item)
                    else:
                        self.property_tree.addTopLevelItem(group_item)
                    group_item.setExpanded(True)
                    property_groups[prefix] = group_item
                prefix += '/'

            item = QtWidgets.QTreeWidgetItem(['', ''])
            property_groups[prop.name.rsplit('/', 1)[0]].addChild(item) if '/' in prop.name else self.property_tree.addTopLevelItem(item)
            self.property_tree.setItemWidget(item, 1, prop.editor_widget)
            name_widget = PropertyNameWidget(self, prop.name, prop.scene_override)
            name_widget.override_changed.connect(lambda overridden, name: self.override_property(name) if overridden else self.unoverride_property(name))
            self.property_tree.setItemWidget(item, 0, name_widget)

            self.property_tree_items[prop.name] = item

    def setup_property_editors(self):
        for prop in self.properties.values():
            prop.setup_property_editor(self.scene_editor)

    def to_data(self):
        data = {'type': self.type, 'properties': {}}

        data['target_scene'] = self.target_scene.as_posix() if self.target_scene else None
        data['target_scene_node'] = self.target_scene_node

        for name, property in self.properties.items():
            data['properties'][name] = property.to_data()
        return data
    
    def load_data(self, data):
        for name, property in data['properties'].items():
            self.set_property(name, property['value'])
            if property['scene_override']:
                self.override_property(name)

        if 'target_scene' in data and data['target_scene'] is not None:
            self.connect_scene(Path(data['target_scene']), data['target_scene_node'])

    def connect_scene(self, scene_path, node_path):
        self.target_scene = scene_path
        self.target_scene_node = tuple(node_path)

    def update_scene_properties(self):
        if self.target_scene and self.target_scene_node:
            with open(self.scene_editor.path / self.target_scene) as f:
                content = json.load(f)

            data = {}
            for json_key, node_data in content.items():
                path_list = json.loads(json_key)
                data[tuple(path_list)] = node_data

            if self.target_scene_node in data:
                node_data = data[self.target_scene_node]
                for name, property in node_data['properties'].items():
                    if name in self.properties and not self.properties[name].scene_override:
                        self.set_property(name, property['value'])
