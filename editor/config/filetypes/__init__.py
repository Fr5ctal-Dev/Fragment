__all__ = ['filetype_to_suffix', 'suffix_to_filetype']
from editor.tools.utils.path import get_resource_path
from pathlib import Path
import json

with open(get_resource_path(Path('editor') / 'config' / 'filetypes' / 'filetypes.json')) as f:
    filetype_data = json.load(f)

inverse_filetype_data = {}
for ft, suffixes in filetype_data.items():
    for suffix in suffixes:
        inverse_filetype_data[suffix] = ft

def filetype_to_suffix(filetype: str) -> list[str] | None:
    return filetype_data.get(filetype)

def suffix_to_filetype(suffix: str) -> str | None:
    return inverse_filetype_data.get(suffix)
