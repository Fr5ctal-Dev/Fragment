from editor.utils.path import get_resource_path
import json

def load_tree(tree, properties):
    indentation = {}
    data = {}
    for line in tree.split('\n'):
        indent = len(line.split(' ')) - 1
        indentation[indent] = line.strip()
        data[indentation[indent]] = {}
        for i in range(indent, -1, -1):
            data[indentation[indent]][indentation[i]] = properties[indentation[i]]

    return data

def load_json(file):
    with open(file) as f:
        content = json.loads(f.read())
    return content

node_properties = load_json(get_resource_path('editor/node_properties/node_properties.json'))

node_types = load_json(get_resource_path('editor/node_properties/node_types.json'))

with open(get_resource_path('editor/node_properties/tree.vtree')) as f:
    content = f.read()

tree = load_tree(content, node_properties)
