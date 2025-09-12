class BaseNodeProperties:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.properties = self.default_properties

    @property
    def default_properties(self):
        properties = {} # name: property
        return properties
    
    def set_property(self, name, value):
        self.properties[name].value = value
