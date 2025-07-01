from .node import Node
from panda3d.core import NodePath, StringStream, Loader
from direct.actor.Actor import Actor
import os


class Character(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_animation = None
        self.future_animation = None
        self.current_blend_task = None

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        loader = Loader.get_global_ptr()

        ss_model = StringStream()
        with open(self._properties['model'], 'rb') as fp:
            ss_model.set_data(fp.read())

        for key in list(self._properties['animations'].keys()):
            anim_ss_model = StringStream()
            if os.path.exists(self._properties['animations'][key]):
                with open(self._properties['animations'][key], 'rb') as fp:
                    anim_ss_model.set_data(fp.read())
                self._properties['animations'][key] = NodePath(loader.load_bam_stream(anim_ss_model))
            else:
                del self._properties['animations'][key]
        self.main_model = Actor(NodePath(loader.load_bam_stream(ss_model)), self._properties['animations'])

        node = self.main_model
        node.reparent_to(self._properties['parent']._node)
        node.enable_blend()
        for animation in list(self._properties['animations'].keys()):
            node.set_control_effect(animation, 0)
        return node

    def handle_animation_change(self, animation):
        if self.current_blend_task is not None:
            taskMgr.remove(self.current_blend_task)
            self._node.set_control_effect(self.current_animation, 0)
            self._node.set_control_effect(self.future_animation, 0)
        self.future_animation = animation
        self.current_blend_task = taskMgr.add(self.blend_update, 'blend_update')

    def blend_update(self, task):
        if self.current_animation is None:
            self._node.set_control_effect(self.future_animation, 1)
            self.current_animation = self.future_animation
            self.future_animation = None
            return task.exit
        if self.future_animation is None:
            return task.exit

        if task.time > 1 / 4:
            self._node.set_control_effect(self.current_animation, 0)
            self._node.set_control_effect(self.future_animation, 1)
            self.current_animation = self.future_animation
            self.future_animation = None
            return task.exit

        self._node.set_control_effect(self.future_animation, task.time * 4)
        self._node.set_control_effect(self.current_animation, 1 - task.time * 4)
        return task.cont

    def play_animation(self, animation):
        self._node.play(animation)
        self.handle_animation_change(animation)

    def loop_animation(self, animation):
        self._node.loop(animation)
        self.handle_animation_change(animation)

    def stop_animation(self):
        self._node.stop()
        self.current_animation = None
        self.future_animation = None
        if self.current_blend_task is not None:
            taskMgr.remove(self.current_blend_task)
            self.current_blend_task = None
        self._node.set_control_effect(self.current_animation, 0)
        self._node.set_control_effect(self.future_animation, 0)

    def destroy(self):
        self._node.cleanup()
        super().destroy()
