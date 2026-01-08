class NodeItem:
    def __init__(self):
        self.parent = None
        self.children = []
    
    def reparent(self, parent):
        if self.parent is not None:
            self.parent.children.remove(self)
        self.parent = parent
        if parent is not None:
            parent.children.append(self)
