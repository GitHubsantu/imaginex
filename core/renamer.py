from pathlib import Path

_last_rename = None

def preview_rename(old_path, new_name):
    old_path = Path(old_path)
    return old_path.with_name(new_name + old_path.suffix)

def rename_file(old_path, new_name):
    global _last_rename

    old_path = Path(old_path)
    new_path = old_path.with_name(new_name + old_path.suffix)

    if not old_path.exists():
        raise FileNotFoundError("File not found")

    if new_path.exists():
        raise FileExistsError("File with same name already exists")

    old_path.rename(new_path)
    _last_rename = (new_path, old_path)

    return new_path

def undo_rename():
    global _last_rename

    if not _last_rename:
        raise Exception("Nothing to undo")

    new_path, old_path = _last_rename
    new_path.rename(old_path)
    _last_rename = None

    return old_path
