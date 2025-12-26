from pathlib import Path
from datetime import datetime
import exifread


def get_image_date(image_path):
    """
    Returns (year, month_name) or None
    """
    try:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")

        date_tag = tags.get("EXIF DateTimeOriginal")

        if not date_tag:
            return None

        date_str = str(date_tag)
        dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

        return dt.year, dt.strftime("%b")

    except Exception:
        return None
