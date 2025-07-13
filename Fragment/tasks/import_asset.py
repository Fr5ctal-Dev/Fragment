from .base_task import BaseTask
import json
import importlib


def snake_to_pascal(text):
    words = text.split('_')
    pascal = ''
    for word in words:
        pascal += word.capitalize()
    return pascal


def inverse_dictionary(dict):
    inverse_dict = {}
    for name, keys in list(dict.items()):
        for key in keys:
            inverse_dict[key] = name
    return inverse_dict


class ImportAssetTask(BaseTask):
    def __init__(self, path, files):
        super().__init__('Import Assets', False)
        self.files = files
        self.path = path

        with open('importers/filetypes.json') as fp:
            filetypes = json.loads(fp.read())

        self.filetypes = inverse_dictionary(filetypes)

    def run(self):
        for file in self.files:
            importer_type = self.filetypes.get('.' + file.split('.')[-1])
            if importer_type is None:
                importer_type = 'base_importer'
            importer = getattr(importlib.import_module('importers.' + importer_type), snake_to_pascal(importer_type))(self.path)
            importer.import_file(file)
        self.finished.emit()


def import_asset(path, files):
    return ImportAssetTask(path, files)
