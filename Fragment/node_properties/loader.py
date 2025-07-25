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
    fp = open(file)
    content = json.loads(fp.read())
    fp.close()
    return content

node_properties = load_json('node_properties/node_properties.json')

node_types = load_json('node_properties/node_types.json')

fp = open('node_properties/tree.vtree')
content = fp.read()
fp.close()

tree = load_tree(content, node_properties)
