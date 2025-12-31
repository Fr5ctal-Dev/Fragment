import shutil


class BaseImporter:
    def __init__(self, project_path):
        self.path = project_path

    def import_file(self, file):
        if file.is_dir():
            shutil.copytree(file, self.path / file.name)
        else:
            shutil.copy(file, self.path / file.name)
