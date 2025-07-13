from .path import Path


class PathScript(Path):
    FILE_FILTER = 'Python Files (*.py)'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
