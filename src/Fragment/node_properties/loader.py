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

fp = open('node_properties/node_properties.json')
content = fp.read()
fp.close()

node_properties = json.loads(content)

fp = open('node_properties/tree.vtree')
content = fp.read()
fp.close()

tree = load_tree(content, node_properties)
