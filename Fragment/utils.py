from panda3d.core import NodePath
import copy
import uuid


def get_code(scene, project_path):
    code = f'''
import fragment.main
fragment.main.setup('{scene}', '{project_path}')
    '''
    return code


def generate_uuid():
    return uuid.uuid4().hex


def get_node_string_data(name, uid, parent, type, properties, script=None):
    return {'name': name, 'uid': uid, 'parent': parent, 'type': type, 'properties': properties, 'script': script}

def get_node_data(name, uid, parent, type, properties, script=None):
    node_path = NodePath(name)
    node_path.set_python_tag('uid', uid)
    if parent:
        node_path.reparent_to(parent)
    return {node_path: {'uid': uid, 'type': type, 'properties': properties, 'script': script}}

def node_path_to_string(node_path):
    string_path = []
    current_parent_step = node_path
    while True:
        string_path.insert(0, current_parent_step.get_python_tag('uid'))
        current_parent_step = current_parent_step.parent
        if current_parent_step is None:
            break
    return string_path

def node_data_to_string(data):
    result = {}
    for node_path in data.keys():
        tuple_path = node_path_to_string(node_path)
        if data[node_path].get('scene_root_node') is not None:
            scene_root_node_parent_path = node_path_to_string(data[node_path]['scene_root_node'].parent)
        else:
            scene_root_node_parent_path = None
        result[tuple(tuple_path)] = copy.deepcopy(data[node_path])
        result[tuple(tuple_path)]['name'] = node_path.get_name()
        result[tuple(tuple_path)]['parent'] = tuple(tuple_path[:-1])
        if result[tuple(tuple_path)].get('scene_root_node') is not None:
            result[tuple(tuple_path)]['scene_root_node'] = scene_root_node_parent_path + node_path_to_string(result[tuple(tuple_path)]['scene_root_node'])
    return result

def string_to_node_data(data):
    result = {}
    tuple_node_path_map = {}
    for path in data.keys():
        node_path = NodePath(data[path]['name'])
        node_path.set_python_tag('uid', data[path]['uid'])
        result[node_path] = data[path]
        tuple_node_path_map[path] = node_path

    for node_path in list(result.keys()):
        tuple_parent = result[node_path]['parent']
        if tuple_parent:
            node_path.reparent_to(tuple_node_path_map[tuple_parent])
        del result[node_path]['parent']
        if result[node_path].get('scene_root_node') is not None:
            result[node_path]['scene_root_node'] = tuple_node_path_map[tuple(result[node_path]['scene_root_node'])]
    return result
