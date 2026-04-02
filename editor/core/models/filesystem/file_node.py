from .path import PathModel
from pathlib import Path


class FileNode:
    def __init__(self, name: str):
        self.name = name
        self.parent: FileNode | None = None
        self.children: dict[str, FileNode] = {}
        self.file_properties: PathModel | None = None

    def reparent(self, parent: 'FileNode | None'):
        if self.parent is not None:
            self.parent.children.pop(self.name)
        self.parent = parent
        if parent is not None:
            parent.children[self.name] = self

    def get_path(self) -> Path:
        return self.parent.get_path() / self.name if self.parent else Path(self.name)
    
    def find_node(self, rel_path: Path) -> 'FileNode | None':
        if len(rel_path.parts) == 0:
            return self
        part = rel_path.parts[0]
        if part not in self.children:
            return None
        child = self.children[part]
        return child.find_node(rel_path.relative_to(part))
    
    def dfs_children(self):
        result = []
        for child in self.children.values():
            result.append(child)
            result.extend(child.dfs_children())
        return result
    
    def set_name(self, name: str):
        if self.parent is not None:
            self.parent.children.pop(self.name)
            self.parent.children[name] = self
        self.name = name

    def set_properties(self, properties: PathModel):
        self.file_properties = properties

    def cleanup(self):
        for child in list(self.children.values()):
            child.cleanup()
        self.reparent(None)
        if self.file_properties is not None:
            self.file_properties.cleanup()
