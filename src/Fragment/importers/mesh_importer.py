from .base_importer import BaseImporter
from node_properties.loader import tree as node_properties
from utils import get_node_string_data, generate_uuid, node_path_to_string
from direct.showbase.Loader import Loader
from direct.actor.Actor import Actor
from panda3d.core import GeomNode, Character, AnimBundleNode, PandaNode, ModelRoot, Filename, CharacterJoint
import os
import copy
import shutil


class MeshImporter(BaseImporter):
    def import_file(self, file):
        dest = self.path + '/' + os.path.basename(file).split('.')[0]
        if not os.path.exists(dest):
            os.makedirs(dest)
        file_path = dest + '/' + os.path.basename(file).split('.')[0] + '.fmesh'
        scene_path = dest + '/' + os.path.basename(file).split('.')[0] + '.fscene'
        anim_path = dest + '/' + os.path.basename(file).split('.')[0] + '-anim.fanim'
        shutil.copy(file, file_path)

        loader = Loader(None)

        model = loader.load_model(Filename.from_os_specific(file))
        model.set_python_tag('uid', generate_uuid())

        is_character = bool(model.find_all_matches('**/+Character'))

        if is_character:
            uid = model.get_python_tag('uid')
            name = model.get_name()
            model = Actor(model, {})
            model.set_name(name)
            model.set_python_tag('uid', uid)

        nodes = []
        self.walk_nodepath(nodes, model)

        for node in nodes:
            node.set_python_tag('uid', generate_uuid())

        model.set_name(os.path.basename(file))

        if is_character:
            properties = copy.deepcopy(node_properties['Character'])
            properties['Character']['model'][0] = file_path
            properties['Node']['position'][0] = list(model.get_pos())
            properties['Node']['rotation'][0] = list(model.get_hpr())
            properties['Node']['scale'][0] = list(model.get_scale())
            scene_data = {tuple(node_path_to_string(model)): get_node_string_data(model.get_name(), generate_uuid(), None, 'Character', properties)}
        else:
            properties = copy.deepcopy(node_properties['Model'])
            properties['Model']['model'][0] = file_path
            properties['Node']['position'][0] = list(model.get_pos())
            properties['Node']['rotation'][0] = list(model.get_hpr())
            properties['Node']['scale'][0] = list(model.get_scale())
            scene_data = {tuple(node_path_to_string(model)): get_node_string_data(model.get_name(), generate_uuid(), None, 'Model', properties)}

        for node in nodes:
            node_path = self.node_path_to_tuple(node)

            node_type = None

            if isinstance(node.node(), ModelRoot):
                continue
            elif isinstance(node.node(), AnimBundleNode):
                shutil.copy(file, anim_path)
                node_type = 'AnimationBundle'
            elif isinstance(node.node(), Character):
                node_type = 'Skeleton'
            elif isinstance(node.node(), GeomNode):
                node_type = 'Mesh'
            elif isinstance(node.node(), PandaNode):
                node_type = 'Node'

            if node_type is not None:
                properties = copy.deepcopy(node_properties[node_type])
                if properties.get('ModelRoot') is not None:
                    properties['ModelRoot']['node_path'][0] = node_path
                properties['Node']['position'][0] = list(node.get_pos())
                properties['Node']['rotation'][0] = list(node.get_hpr())
                properties['Node']['scale'][0] = list(node.get_scale())

                string_path = tuple(node_path_to_string(node))

                scene_data[string_path] = get_node_string_data(node.get_name(), generate_uuid(), string_path[:-1], node_type, properties)

        if is_character:
            self.walk_joint_hierarchy(model, model.get_part_bundle('modelRoot'), scene_data)

        scene_data = str(scene_data)
        with open(scene_path, 'w') as fp:
            fp.write(scene_data)


    def walk_nodepath(self, result, node):
        for child in node.get_children():
            result.append(child)
            self.walk_nodepath(result, child)

    def walk_joint_hierarchy(self, actor, part, scene_data, parent_node=None, parent=''):
        if not parent:
            parent = list(scene_data.keys())[0]
        if isinstance(part, CharacterJoint):
            np = actor.expose_joint(None, 'modelRoot', part.get_name())
            node_path = parent + (np.name,)

            properties = copy.deepcopy(node_properties['Bone'])
            properties['Bone']['bone_name'][0] = part.get_name()
            properties['Bone']['controlled'][0] = False
            properties['Node']['position'][0] = list(np.get_pos())
            properties['Node']['rotation'][0] = list(np.get_hpr())
            properties['Node']['scale'][0] = list(np.get_scale())

            scene_data[tuple(node_path)] = get_node_string_data(np.name, generate_uuid(), tuple(parent), 'Bone', properties)

            parent_node = np
            parent = node_path

        for child in part.get_children():
            self.walk_joint_hierarchy(actor, child, scene_data, parent_node, parent)

    def node_path_to_tuple(self, node):
        tuple_data = [node.get_name()]

        curr_parent = node
        while True:
            if curr_parent.parent is not None:
                curr_parent = curr_parent.parent
                tuple_data.insert(0, curr_parent.get_name())
            else:
                break

        return tuple(tuple_data)
