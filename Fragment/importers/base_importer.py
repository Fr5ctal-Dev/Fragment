import shutil
import os


class BaseImporter:
    def __init__(self, project_path):
        self.path = project_path

    def import_file(self, file):
        if os.path.isdir(file):
            shutil.copytree(file, self.path + '/' + os.path.basename(file))
        else:
            shutil.copy(file, self.path + '/' + os.path.basename(file))
