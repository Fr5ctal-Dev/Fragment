from PySide6 import QtWidgets


class BaseNodeProperties:
    def __init__(self, scene_editor, name, type):
        self.scene_editor = scene_editor
        self.name = name
        self.type = type
        self.properties = self.default_properties
        self.property_tree = None
        self.setup_property_tree()

    @property
    def default_properties(self):
        properties = {} # name: property
        return properties
    
    def set_property(self, name, value):
        self.properties[name].value = value
        self.properties[name].update_editor_value()

    def setup_property_tree(self):
        self.setup_property_editors()
        self.property_tree = QtWidgets.QTreeWidget()
        self.property_tree.setColumnCount(2)
        self.property_tree.setHeaderLabels(['Name', 'Value'])
        self.property_tree.setIndentation(15)

        for prop in self.properties.values():
            item = QtWidgets.QTreeWidgetItem([prop.name, ''])
            self.property_tree.addTopLevelItem(item)
            self.property_tree.setItemWidget(item, 1, prop.editor_widget)

    def setup_property_editors(self):
        for prop in self.properties.values():
            prop.setup_property_editor(self.scene_editor, self.type)
