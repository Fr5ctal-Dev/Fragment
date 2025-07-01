from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from panda3d.core import GraphicsOutput, Texture, CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, load_prc_file_data
from panda3d.bullet import BulletWorld, BulletDebugNode
from buffer_renderer.direct.showbase.ShowBase import ShowBase
from rpcore import RenderPipeline
import importlib

load_prc_file_data('', 'notify-level fatal')
load_prc_file_data('', 'print-pipe-types 0')


class Viewport(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.scene_editor = editor

        self.entities = []

        self.selected_entity = None

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.pre_showbase_init()

        self.showbase = ShowBase(windowType='offscreen')
        self.showbase.disable_mouse()

        self.render_pipeline.create(self.showbase)
        self.render_pipeline.daytime_mgr.time = 0.0

        self.engine = self.showbase.graphics_engine
        self.buffer = self.showbase.win

        self.texture = Texture()
        self.buffer.add_render_texture(self.texture, GraphicsOutput.RTMCopyRam)

        self.physics_debug_node = BulletDebugNode('Debug')
        self.physics_debug_node = self.showbase.render.attach_new_node(self.physics_debug_node)
        self.physics_debug_node.show()

        self.physics_world = BulletWorld()
        self.physics_world.set_debug_node(self.physics_debug_node.node())

        class BaseScene:
            def __init__(self_, render):
                self_._node = render

        self.scene = BaseScene(self.showbase.render)
        self.showbase.render.set_transparency(True)

        self.showbase.render.set_python_tag('render_pipeline', self.render_pipeline)
        self.showbase.render.set_python_tag('physics_world', self.physics_world)

        self.camera = self.showbase.camera
        self.camera.set_y(-20)

        lens = self.showbase.cam.node().get_lens()
        lens.set_fov(90)
        self.showbase.cam.node().set_lens(lens)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(25)

        self.update_physics_timer = QtCore.QTimer(self)
        self.update_physics_timer.timeout.connect(lambda: self.physics_world.do_physics(0.01))
        self.update_physics_timer.start(100)

        self.display_label = QtWidgets.QLabel(self)
        self.display_label.move(0, 0)
        self.display_label.resize(self.size())

        self.movement_control_input = {'w': False, 'a': False, 's': False, 'd': False}
        self.can_control_camera = False

        self.object_picker_traverser = CollisionTraverser()
        self.object_picker_queue = CollisionHandlerQueue()
        self.object_picker_ray_node = CollisionNode('picker_ray')
        self.object_picker_ray_node.set_from_collide_mask(GeomNode.get_default_collide_mask())
        self.object_picker_ray = CollisionRay()
        self.object_picker_ray_node.add_solid(self.object_picker_ray)
        self.object_picker_ray_node = self.camera.attach_new_node(self.object_picker_ray_node)
        self.object_picker_traverser.add_collider(self.object_picker_ray_node, self.object_picker_queue)

    def on_destroy(self):
        self.timer.stop()
        self.showbase.ignore_all()
        del self.render_pipeline
        for task in self.showbase.taskMgr.getAllTasks():
            self.showbase.taskMgr.remove(task)
        self.showbase.destroy()
        del self.showbase.taskMgr
        del self.showbase

    def resizeEvent(self, event):
        new_width = event.size().width()
        new_height = event.size().height()

        self.display_label.resize(QtCore.QSize(new_width, new_height))

        self.buffer.set_size(new_width, new_height)

        self.render_pipeline._handle_resize()

        lens = self.showbase.cam.node().get_lens()
        lens.set_aspect_ratio(new_width / new_height)

        super().resizeEvent(event)

    def render_(self):
        for entity in self.entities:
            entity._property_init()
            if entity == self.selected_entity:
                entity._node.set_render_mode_filled_wireframe((1, 1, 0, 1))

            else:
                entity._node.set_render_mode_filled()

        self.render_pipeline.prepare_scene(self.showbase.render)

        self.showbase.taskMgr.step()

        if self.texture.has_ram_image():
            tex_data = self.texture.get_ram_image_as('RGB')
            img_data = tex_data.get_data()
            image = QtGui.QImage(img_data, self.texture.get_x_size(), self.texture.get_y_size(),
                                 3 * self.texture.get_x_size(), QtGui.QImage.Format.Format_RGB888)
        else:
            image = QtGui.QImage()
        return image.mirrored()

    def update(self):
        super().update()
        if self.scene_editor.editor.tab_view.widget(self.scene_editor.editor.tab_view.currentIndex()) == self.scene_editor:
            image = self.render_()
            if not image.isNull():
                self.display_label.setPixmap(QtGui.QPixmap(image))

        if self.can_control_camera:
            movement = [self.movement_control_input['d'] - self.movement_control_input['a'], self.movement_control_input['w'] - self.movement_control_input['s']]
            if movement[0] != 0 and movement[1] != 0:
                movement[0] *= 0.7071
                movement[1] *= 0.7071
            try:
                self.pan_camera(movement[0] / 2, 0)
                self.zoom_camera(movement[1] / 2)
            except:
                pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_W:
            self.movement_control_input['w'] = True
        elif event.key() == Qt.Key.Key_A:
            self.movement_control_input['a'] = True
        elif event.key() == Qt.Key.Key_S:
            self.movement_control_input['s'] = True
        elif event.key() == Qt.Key.Key_D:
            self.movement_control_input['d'] = True

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_W:
            self.movement_control_input['w'] = False
        elif event.key() == Qt.Key.Key_A:
            self.movement_control_input['a'] = False
        elif event.key() == Qt.Key.Key_S:
            self.movement_control_input['s'] = False
        elif event.key() == Qt.Key.Key_D:
            self.movement_control_input['d'] = False

        super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.RightButton and self.rect().contains(event.position().toPoint()):
            delta = event.position().toPoint().x() - self.previous_mouse_position.x(), event.position().toPoint().y() - self.previous_mouse_position.y()
            self.previous_mouse_position = event.position().toPoint()
            self.rotate_camera(*delta)

        elif event.buttons() == Qt.MouseButton.MiddleButton and self.rect().contains(event.position().toPoint()):
            delta = event.position().toPoint().x() - self.previous_mouse_position.x(), event.position().toPoint().y() - self.previous_mouse_position.y()
            self.previous_mouse_position = event.position().toPoint()
            self.pan_camera(-delta[0] / 10, delta[1] / 10)

        if event.buttons():
            self.handle_drag(event)

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 32
        self.zoom_camera(delta)

    def mousePressEvent(self, event):
        if event.button():
            self.previous_mouse_position = event.position().toPoint()

        if event.buttons() == Qt.MouseButton.RightButton and self.rect().contains(event.position().toPoint()):
            self.can_control_camera = True

        elif event.buttons() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            position = event.position().toPoint()
            rect_width, rect_height = self.rect().width(), self.rect().height()
            rel_position = ((position.x() / rect_width) * 2 - 1, -((position.y() / rect_height) * 2 - 1))
            self.pick_object(rel_position[0], rel_position[1])

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.can_control_camera = False

        super().mouseReleaseEvent(event)

    def handle_drag(self, event):
        if not self.rect().contains(event.position().toPoint()):
            mouse_x = event.position().toPoint().x() % self.width()
            mouse_y = event.position().toPoint().y() % self.height()
            QtGui.QCursor.setPos(self.mapToGlobal(QtCore.QPoint(mouse_x, mouse_y)))
            self.previous_mouse_position = QtCore.QPoint(mouse_x, mouse_y)

    def rotate_camera(self, x, y):
        self.camera.set_hpr(self.camera.get_hpr() - (x / 4, y / 4, 0))

    def zoom_camera(self, amount):
        amount = self.scene._node.get_relative_vector(self.camera, (0, 1, 0)) * amount
        self.camera.set_pos(self.camera.get_pos() + amount)

    def pan_camera(self, x, y):
        x_axis = self.scene._node.get_relative_vector(self.camera, (1, 0, 0))
        y_axis = self.scene._node.get_relative_vector(self.camera, (0, 0, 1))
        amount = x_axis * x + y_axis * y
        self.camera.set_pos(self.camera.get_pos() + amount)

    def add_entity(self, type, parent, properties, node_path):
        node_file = importlib.import_module(f'fragment.nodes.{type.lower()}')
        node_class = getattr(node_file, type)
        node = node_class.to_viewport(parent, node_path, viewport_card_texture=f'assets/node_icons/{type.lower()}.png', **properties)
        if type in ['Light', 'SpotLight']:
            self.render_pipeline.add_light(node.light)

        self.entities.append(node)
        return node

    def pick_object(self, x, y):
        self.object_picker_ray.set_from_lens(self.showbase.camNode, x, y)
        self.object_picker_traverser.traverse(self.showbase.render)
        if self.object_picker_queue.get_num_entries() > 0:
            self.object_picker_queue.sort_entries()
            picked_object = self.object_picker_queue.get_entry(0).get_into_node_path()
            if picked_object.has_python_tag('viewport_pickable'):
                self.scene_editor.set_current_node(picked_object.get_python_tag('viewport_pickable')._node_path)
