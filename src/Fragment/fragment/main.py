import sys
sys.path.insert(0, 'fragment/render_pipeline/')

from .window import Window
from .nodes.node import Node
import builtins
import os
import importlib


class Game:
    def __init__(self, scene, project_path):
        builtins.game = self

        self.project_path = project_path

        self.window = Window()
        self.current_scene = scene

        fp = open(scene)
        content = eval(fp.read())
        fp.close()

        self.scene = content
        self.nodes = {}
        self.base_node = Node(None, '/')
        base.render = self.base_node._node

        self.window.setup()

        self.load_scene(scene)

    def run(self):
        self.window.run()

    def get_scene(self):
        return self.current_scene

    def load_scene(self, scene):
        for node in self.nodes.keys():
            self.nodes[node].destroy()

        self.nodes = {}

        fp = open(scene)
        content = eval(fp.read())
        fp.close()

        self.current_scene = scene

        self._scene = content

        self.scene = {}

        for node in self._scene.keys():
            self.scene[node] = self._scene[node]

        for node in self.scene.keys():
            if self.scene[node]['parent']:
                parent = self.nodes[self.scene[node]['parent']]
            else:
                parent = self.base_node

            node_file = importlib.import_module(f'fragment.nodes.{self.scene[node]["type"].lower()}')
            if self.scene[node]['script']:
                node_ = importlib.import_module(self.scene[node]['script'].replace('/', '.')[len(self.project_path) + 1: -3]).Node

            else:
                node_ = getattr(node_file, self.scene[node]['type'])

            properties = {}

            for value in self.scene[node]['properties'].values():
                properties = {**properties, **value}

            for key in list(properties.keys()):
                properties[key] = properties[key][0]

            self.nodes[node] = node_(parent, node, **properties)

        for node in self.scene.keys():
            self.nodes[node].on_start()

        self.window.render_pipeline.prepare_scene(self.base_node._node)

    def instantiate_scene(self, scene, parent):
        parent = parent._node_path

        fp = open(scene)
        content = eval(fp.read())
        fp.close()

        self._scene = content

        self.scene = {}

        base_parent_path = ''
        old_parent_path = ''

        for node in self._scene.keys():
            if self._scene[node]['parent'] == '':
                extension = ''
                i = 0
                while self.scene.get(parent + node + extension) is not None:
                    i += 1
                    extension = f' COPY - {i}'

                self.scene[parent + node + extension] = self._scene[node]
                self.scene[parent + node + extension]['parent'] = parent + self.scene[parent + node + extension]['parent']
                base_parent_path = parent + node + extension
                old_parent_path = node

            else:
                old_node = node
                node = node[len(old_parent_path):]
                node = base_parent_path + node
                self.scene[node] = self._scene[old_node]
                self.scene[node]['parent'] = base_parent_path + self.scene[node]['parent'][len(old_parent_path):]

        for node in self.scene.keys():
            if self.scene[node]['parent'] == '':
                parent = game.base_node
            else:
                parent = self.nodes[self.scene[node]['parent']]

            node_file = importlib.import_module(f'fragment.nodes.{self.scene[node]["type"].lower()}')
            if self.scene[node]['script']:
                node_ = importlib.import_module(self.scene[node]['script'].replace('/', '.')[len(os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__)))) + 1: -3]).Node

            else:
                node_ = getattr(node_file, self.scene[node]['type'])

            properties = {}

            for value in self.scene[node]['properties'].values():
                properties = {**properties, **value}

            for key in list(properties.keys()):
                properties[key] = properties[key][0]

            self.nodes[node] = node_(parent, node, **properties)

        for node in self.scene.keys():
            self.nodes[node].on_start()

        self.window.render_pipeline.prepare_scene(self.base_node._node)

        return self.nodes[base_parent_path]

    def get_node(self, path):
        return self.nodes[path]


def setup(scene, project_path):
    game = Game(scene, project_path)
    game.run()
