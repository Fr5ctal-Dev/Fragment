from property_editor_widgets.string import String
from property_editor_widgets.bool import Bool
from property_editor_widgets.float import Float
from property_editor_widgets.vector2 import Vector2
from property_editor_widgets.path import Path
from property_editor_widgets.color import Color
from property_editor_widgets.timeline import Timeline
from property_editor_widgets.path_dict import PathDict
from property_editor_widgets.input_map import InputMap
from property_editor_widgets.hidden import Hidden
from property_editor_widgets.path_node_script import PathNodeScript
from utils.node import node_path_to_string
from utils.path import get_resource_path
from node_properties.loader import node_types
from PySide6 import QtWidgets, QtGui
import os

EDITOR_TYPE_CLASS_MAP = {
    'string': String,
    'bool': Bool,
    'float': Float,
    'vector2': Vector2,
    'path': Path,
    'color': Color,
    'timeline': Timeline,
    'path_dict': PathDict,
    'input_map': InputMap,
    'hidden': Hidden,
    'path_node_script': PathNodeScript
}


class PropertyList(QtWidgets.QTreeWidget):
    def __init__(self, editor, nodes, set_changed_prop_action, path):
        super().__init__()
        self.scene_editor = editor
        self.nodes = nodes
        self.set_changed_prop_action = set_changed_prop_action
        self.path = path

        self.setColumnCount(2)
        self.setHeaderLabels(['Name', 'Value'])
        self.setIndentation(15)
        top_level = QtWidgets.QTreeWidgetItem(['Properties'])
        self.addTopLevelItem(top_level)
        self.setRootIndex(self.indexFromItem(top_level))

    def set_current_node(self, node):
        self.takeTopLevelItem(0)
        top_level = QtWidgets.QTreeWidgetItem(['Properties'])
        self.addTopLevelItem(top_level)
        self.setRootIndex(self.indexFromItem(top_level))
        self.expandItem(self.topLevelItem(0))

        widget_tree_item_map = {}

        for type in self.nodes[node]['properties'].keys():
            chunk = QtWidgets.QTreeWidgetItem([type])
            chunk.setIcon(0, QtGui.QIcon(get_resource_path(f'assets/node_icons/{type}.png')))
            self.topLevelItem(0).addChild(chunk)
            self.expandItem(chunk)
            for prop in self.nodes[node]['properties'][type].keys():
                p = QtWidgets.QTreeWidgetItem([prop, ''])
                if self.nodes[node].get('changed_props') is not None:
                    if prop in self.nodes[node]['changed_props']:
                        font = p.font(0)
                        font.setBold(True)
                        font.setItalic(True)
                        p.setFont(0, font)

                    else:
                        if not os.path.exists(self.nodes[node]['scene_path']):
                            return

                        with open(self.nodes[node]['scene_path']) as f:
                            nodes = eval(f.read())

                        self.nodes[node]['properties'][type][prop] = nodes[tuple(node_path_to_string(node)[len(node_path_to_string(self.nodes[node]['scene_root_node'].parent)):])]['properties'][type][prop]

                chunk.addChild(p)

                data = (self.nodes[node]['properties'][type][prop], node_types[type][prop]), self.path, self.nodes[node]['type'], self.scene_editor

                if EDITOR_TYPE_CLASS_MAP.get(node_types[type][prop]) is not None:
                    editor = EDITOR_TYPE_CLASS_MAP[node_types[type][prop]](*data)
                else:
                    editor = String(*data)

                widget_tree_item_map[editor] = p

                editor.value_changed.connect(lambda widget: self.set_changed_prop_action(node, widget_tree_item_map[widget]))

                self.setItemWidget(p, 1, editor)
