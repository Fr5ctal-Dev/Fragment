from ..base_model import BaseModel
from .path import PathModel
from .file_node import FileNode
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.events import (
    FileMovedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    DirCreatedEvent,
    FileDeletedEvent,
    DirDeletedEvent,
)
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from PySide6.QtCore import Signal
from pathlib import Path
import os
import shutil

def iter_tree(root: Path):
    yield root
    if not root.is_dir():
        return
    for p in root.iterdir():
        if p.is_dir() and not p.is_symlink():
            yield from iter_tree(p)
        else:
            yield p


class FileSystemModel(BaseModel):
    path_created = Signal(FileNode)
    path_deleted = Signal(FileNode)
    path_renamed = Signal(FileNode, str)
    path_moved = Signal(FileNode, FileNode)  # item, new parent

    file_event = Signal(FileSystemEvent)
    def __init__(self, editor, directory: Path):
        super().__init__()
        self.editor = editor
        self.directory = directory
        self.asset_directory = Path('assets')
        self.root_file_node: FileNode | None = None
        self.file_observer: BaseObserver | None = None

        self.file_event.connect(self.on_file_system_event) # Moves to main thread

        self.setup_file_system()
        self.setup_file_watcher()

    def setup_file_system(self):
        self.new_path_model(Path('.'))  # Root noode
        for p in iter_tree(self.directory / self.asset_directory):
            self.new_path_model(p.relative_to(self.directory))

    def setup_file_watcher(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_any_event = lambda event: self.file_event.emit(event)
        self.file_observer = Observer()
        self.file_observer.schedule(event_handler, str(self.directory / self.asset_directory), recursive=True)
        self.file_observer.start()

    def new_path_model(self, path: Path):
        file_node = FileNode(path.name)
        path_model = PathModel(self.editor, path.name)

        path_parent = path.parent
        if path_parent == path: # Root Directory
            assert self.root_file_node is None
            self.root_file_node = file_node
        else:
            assert self.root_file_node is not None, f'{path}'
            parent_node = self.root_file_node.find_node(path_parent)
            assert parent_node is not None, f'{path_parent}'
            file_node.reparent(parent_node)

        file_node.set_properties(path_model)
        self.path_created.emit(file_node)

    def on_path_rename(self, file_node: FileNode, name: str):
        file_node.set_name(name)

        path_model = file_node.file_properties
        assert path_model is not None
        path_model.set_property('Name', name)
        self.path_renamed.emit(file_node, name)

    def on_path_delete(self, file_node: FileNode):
        file_node.cleanup()
        self.path_deleted.emit(file_node)

    def on_path_move(self, old_file_node: FileNode, new_parent: FileNode): # Path move without rename
        old_file_node.reparent(new_parent)
        self.path_moved.emit(old_file_node, new_parent)

    def on_file_system_event(self, event: FileSystemEvent):
        if self.root_file_node is None:
            return # Not initialized yet / already cleaned up
        src_path = Path(os.fsdecode(event.src_path)).relative_to(self.directory)
        
        if isinstance(event, (FileMovedEvent, DirMovedEvent)):
            dest_path = Path(os.fsdecode(event.dest_path)).relative_to(self.directory)
            src_path_node = self.root_file_node.find_node(src_path)
            dest_path_parent_node = self.root_file_node.find_node(dest_path.parent)
            assert dest_path_parent_node is not None
            if src_path_node is not None:
                self.on_path_move(src_path_node, dest_path_parent_node)

            rename_node = self.root_file_node.find_node(dest_path.parent / src_path.name)
            assert rename_node is not None, dest_path.parent / src_path.name
            self.on_path_rename(rename_node, dest_path.name)
        
        elif isinstance(event, (FileCreatedEvent, DirCreatedEvent)):
            self.new_path_model(src_path)
        
        elif isinstance(event, (FileDeletedEvent, DirDeletedEvent)):
            src_path_node = self.root_file_node.find_node(src_path)
            assert src_path_node is not None
            self.on_path_delete(src_path_node)

    def delete_path(self, node: FileNode):
        path = self.directory / node.get_path()
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def new_file(self, path: Path):
        full_path: Path = self.directory / path
        full_path.touch()

    def new_script_file(self, path: Path):
        full_path: Path = self.directory / path
        with open(full_path, 'w') as f:
            f.write('// Write your code here\n')

    def new_scene_file(self, path: Path):
        full_path: Path = self.directory / path
        with open(full_path, 'w') as f:
            f.write('{}')

    def rename_path(self, node: FileNode, new_name: str):
        old_path: Path = self.directory / node.get_path()
        new_path = old_path.with_name(new_name)
        shutil.move(old_path, new_path)

    def move_path(self, old_node: FileNode, new_parent: FileNode):
        old_path: Path = self.directory / old_node.get_path()
        new_parent_path: Path = self.directory / new_parent.get_path()
        new_path = new_parent_path / old_path.name
        shutil.move(old_path, new_path)

    def cleanup(self):
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None
        if self.root_file_node is not None:
            self.root_file_node.cleanup()
            self.root_file_node = None
        super().cleanup()
