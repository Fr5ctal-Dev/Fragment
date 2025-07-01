from .node import Node
from ..vector import Vec2
from panda3d.core import ButtonHandle, WindowProperties

# Workaround
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


class Input(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inverse_input_map = {}
        self.input_map_lock = INPUT_LIST
        self._mouse_visible = True

    @property
    def input_map(self):
        return self._properties['input_map']

    @input_map.setter
    def input_map(self, input_map):
        self.inverse_input_map = {}
        for name, keys in list(input_map.items()):
            for key in keys:
                self.inverse_input_map[key] = name
        self._properties['input_map'] = input_map

    @property
    def mouse_position(self):
        return Vec2(base.win.get_pointer(0).get_x(), base.win.get_pointer(0).get_y())


    @mouse_position.setter
    def mouse_position(self, position):
        base.win.move_pointer(0, int(position[0]), int(position[1]))

    @property
    def mouse_visible(self):
        return self._mouse_visible

    @mouse_visible.setter
    def mouse_visible(self, visible):
        self._mouse_visible = visible
        props = WindowProperties()
        props.set_cursor_hidden(not visible)
        base.win.request_properties(props)

    def _update(self, task):
        self.input_map = self.input_map
        for key in self.inverse_input_map.keys():
            k = ButtonHandle(key)
            if base.mouseWatcherNode.is_button_down(k):
                if key not in self.input_map_lock:
                    self.on_event_activated(self.inverse_input_map[key])
                    self.input_map_lock.append(key)
                self.on_event_held(self.inverse_input_map[key])
            else:
                if key in self.input_map_lock:
                    self.input_map_lock.remove(key)
        return super()._update(task)

    def on_event_held(self, event):
        pass

    def on_event_activated(self, event):
        pass
