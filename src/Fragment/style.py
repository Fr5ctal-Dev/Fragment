STYLE = '''
/* General Styling */
* {
    background-color: #181818;
    color: #FFFFF;
    selection-background-color: #2A2A2A;
    selection-color: #FFFFFF;
    border: 1px solid #3C3C3C;
    border-radius: 5px;
    padding: 0px;
    margin: 0px;
}

/* QPushButton Styling */
QPushButton {
    background-color: #222222;
    border: 1px solid #303030;
    border-radius: 8px;
    color: #AAAAAA;
}
QPushButton:hover {
    background-color: #2A2A2A;
}
QPushButton:pressed {
    background-color: #444444;
    border-color: #383838;
}

/* QTreeView and QTreeWidget Styling */
QTreeView, QTreeWidget, QListWidget {
    background-color: #202020;
    border: 1px solid #303030;
    border-radius: 8px;
    color: #CCCCCC;
    alternate-background-color: #1C1C1C;
}
QTreeView::item:selected, QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #444444;
    color: #FFFFFF;
}
QTreeView::item:hover, QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #2A2A2A;
}

QHeaderView::section {
    background-color: #222222;
    padding: 4px;
    border: 1px solid #303030;
}

/* ScrollBar Styling */
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
    width: 8px;
    height: 8px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #383838;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #444444;
}
QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

/* QListWidget Item alternate color */
QListWidget::item {
    padding: 5px;
}

/* QToolTip Styling */
QToolTip {
    background-color: #222222;
    color: #CCCCCC;
    border: 1px solid #303030;
    padding: 5px;
    border-radius: 8px;
}

/* QComboBox Styling */
QComboBox {
    background-color: #202020;
    border: 1px solid #303030;
    border-radius: 8px;
    padding: 5px;
    color: #CCCCCC;
}
QComboBox:hover {
    background-color: #222222;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #202020;
    selection-background-color: #444444;
    color: #CCCCCC;
}

/* QTabWidget Styling */
QTabBar::tab {
    background-color: #222222;
    padding: 8px 16px;
    border: none;
    color: #AAAAAA;
}
QTabBar::tab:selected {
    border-bottom: 2px solid #444444;
    color: #FFFFFF;
}
QTabBar::tab:hover {
    background-color: #2A2A2A;
}

'''