from pathlib import Path
from core.cleaner import clean_filename

# Stack for undo (supports batch + single)
MAX_UNDO = 20
_undo_stack = []

def preview_rename(old_path, new_name):
    old_path = Path(old_path)
    return old_path.with_name(new_name + old_path.suffix)


def rename_file(old_path, new_name):
    global _undo_stack

    old_path = Path(old_path)
    cleaned = clean_filename(new_name)
    new_path = old_path.with_name(cleaned + old_path.suffix)

    if not old_path.exists():
        raise FileNotFoundError("File not found")

    if new_path.exists():
        raise FileExistsError("File with same name already exists")

    old_path.rename(new_path)

    # push single undo
    _undo_stack.append([(new_path, old_path)])

    if len(_undo_stack) > MAX_UNDO:
        _undo_stack.pop(0)

    return new_path


def batch_rename(files, name_input):
    global _undo_stack

    if not files:
        raise ValueError("No files provided")

    # split by comma (Name1, Name2)
    name_list = [clean_filename(n.strip()) for n in name_input.split(",") if n.strip()]

    undo_batch = []
    renamed = []

    for i, file in enumerate(files):
        old_path = Path(file)

        if i < len(name_list):
            base_name = name_list[i]
        else:
            base_name = f"{name_list[0]}_{i+1}"

        new_path = old_path.with_name(base_name + old_path.suffix)

        if new_path.exists():
            raise FileExistsError(f"{new_path.name} already exists")

        old_path.rename(new_path)

        renamed.append(new_path)
        undo_batch.append((new_path, old_path))

    # push full batch undo
    _undo_stack.append(undo_batch)
    if len(_undo_stack) > MAX_UNDO:
        _undo_stack.pop(0)


    return renamed


def undo_rename():
    global _undo_stack

    if not _undo_stack:
        raise Exception("Nothing to undo")

    last_batch = _undo_stack.pop()

    for new_path, old_path in reversed(last_batch):
        if new_path.exists():
            new_path.rename(old_path)

    return len(last_batch)
