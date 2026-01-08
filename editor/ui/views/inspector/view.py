from ..base_view import BaseView
from PySide6 import QtWidgets, QtCore


class InspectorView(BaseView):
    def __init__(self, editor):
        super().__init__(editor)
        self.properties = {}
        self.property_views = {}
        self.property_tree_items = {}
        
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QStackedLayout(self.main_widget)

        self.property_tree = QtWidgets.QTreeWidget()
        self.property_tree.setColumnCount(2)
        self.property_tree.setHeaderLabels(['Name', 'Value'])
        self.property_tree.setIndentation(10)
        self.main_layout.addWidget(self.property_tree)

        self.empty_view = QtWidgets.QLabel('Nothing selected')
        self.empty_view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.empty_view)

        self.main_widget.resize(self.property_tree.width(), self.main_widget.height())

    def cleanup(self):
        super().cleanup()
        for prop_view in self.property_views.values():
            prop_view.cleanup()
        self.property_views = {}
        self.property_tree_items = {}
        self.properties = {}

        for i in range(self.property_tree.topLevelItemCount()):
            self.property_tree.takeTopLevelItem(0)
        

    def display(self):
        assert self.model is not None # For type checker
        self.properties = self.model.properties
        
        for name, prop in self.properties.items():
            prop_view = self.model.recommended_view(self.editor)
            prop_view.set_model(prop)
            self.property_views[name] = prop_view

        self.main_layout.setCurrentWidget(self.property_tree)

        property_groups = {}

        for prop in self.property_views.values():
            prefix = ''
            for group in prop.model.name.split('/')[:-1]:
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
            property_groups[prop.model.name.rsplit('/', 1)[0]].addChild(item) if '/' in prop.model.name else self.property_tree.addTopLevelItem(item)
            self.property_tree.setItemWidget(item, 0, prop.title_widget)
            self.property_tree.setItemWidget(item, 1, prop.editor_widget)

            self.property_tree_items[prop.model.name] = item

    def display_empty(self):
        self.main_layout.setCurrentWidget(self.empty_view)
