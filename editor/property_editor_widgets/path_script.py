from .path import Path


class PathScript(Path):
    FILE_FILTER = 'Javascript Files (*.js)'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
