import re
import os
import sys


def extract_extensions_from_filter(filter_string):
    match = re.search(r'\((.*?)\)', filter_string)
    if not match:
        return []
    pattern = match.group(1)
    extensions = []
    for ext in pattern.split():
        ext = ext.strip()
        if ext.startswith('*.'):
            extensions.append(ext[1:])
        elif ext == '*':
            extensions.append('*')
    return extensions


def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', None) # PyInstaller
    if base_path:
        return os.path.join(base_path, relative_path)
    return relative_path
