from .string_list import StringList
from .string import String
from PySide6.QtWidgets import QCompleter

INPUT_LIST = [
    *list('abcdefghijklmnopqrstuvwxyz'),
    *list('1234567890'),
    *list('`-=[]\\;\',./'),
    'f1',
    'f2',
    'f3',
    'f4',
    'f5',
    'f6',
    'f7',
    'f8',
    'f9',
    'f10',
    'f11',
    'f12',
    'escape',
    'print_screen',
    'scroll_lock',
    'backspace',
    'insert',
    'home',
    'page_up',
    'num_lock',
    'tab',
    'delete',
    'end',
    'page_down',
    'caps_lock',
    'enter',
    'arrow_left',
    'arrow_up',
    'arrow_down',
    'arrow_right',
    'shift',
    'lshift',
    'rshift',
    'control',
    'alt',
    'lcontrol',
    'lalt',
    'space',
    'ralt',
    'rcontrol',
    'mouse1',
    'mouse2',
    'mouse3',
    'wheel_up',
    'wheel_down'
]


class InputList(StringList):
    def add_item(self, value):
        item = self.new_item()
        string_edit = String([value, 'string'], *self.args[1:], **self.kwargs)
        completer = QCompleter(INPUT_LIST)
        string_edit.line_edit.setCompleter(completer)
        string_edit.value_changed.connect(lambda *args: self.change_property())
        self.tree_widget.setItemWidget(item, 0, string_edit)
