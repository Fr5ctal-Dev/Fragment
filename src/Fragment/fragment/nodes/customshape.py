from .node import Node
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh
from panda3d.core import Loader, StringStream, NodePath, PandaNode
import os


class CustomShape(Node):
    def _get_node(self):
        if not os.path.exists(self._properties['mesh']):
            return self._properties['parent']._node.attach_new_node(PandaNode('node'))

        ss = StringStream()
        fp = open(self._properties['mesh'], 'rb')
        ss.set_data(fp.read())
        fp.close()

        mesh = NodePath(Loader.get_global_ptr().load_bam_stream(ss))
        mesh.flatten_light()

        triangle_mesh = BulletTriangleMesh()
        triangle_mesh.add_geom(mesh.find_all_matches('**/+GeomNode').get_path(0).node().get_geom(0))
        shape = BulletTriangleMeshShape(triangle_mesh, dynamic=True)
        try:
            self._properties['parent']._node.node().add_shape(shape)
        except:
            try:
                self._properties['parent'].full_init(shape)
            except BaseException as b:
                print(b)
        return super()._get_node()

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)