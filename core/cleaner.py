import re

def clean_filename(name):
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"\(\d+\)", "", name)
    name = re.sub(r"_+", "_", name)
    return name.title()
