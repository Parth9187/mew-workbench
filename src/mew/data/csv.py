"""CSV loading for image-text datasets."""

import csv
from pathlib import Path

from mew.data.schema import ImageTextDataset, ImageTextPair


def load_csv(path: Path) -> ImageTextDataset:
    """Load ordered pairs, resolving relative image paths against the CSV directory.

    Raise ValueError for missing required headers, null rows, or incomplete required fields,
    with CSV line numbers. Missing files raise FileNotFoundError.
    """
    pairs: list[ImageTextPair] = []
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required = ("image_path", "caption")
        missing = [name for name in required if name not in (reader.fieldnames or ())]
        if missing:
            raise ValueError(f"CSV row 1: missing required headers: {', '.join(missing)}")

        for row in reader:
            if all(
                value is None or (isinstance(value, str) and not value.strip())
                for value in row.values()
            ):
                raise ValueError(f"CSV row {reader.line_num}: null row; all fields are empty")
            missing = [name for name in required if row[name] is None]
            if missing:
                raise ValueError(
                    f"CSV row {reader.line_num}: incomplete row; missing fields: "
                    f"{', '.join(missing)}"
                )
            image_path = Path(row["image_path"])
            if not image_path.is_absolute():
                image_path = path.parent / image_path
            identifier = row.get("id")
            if identifier is not None and not identifier.strip():
                identifier = None
            pairs.append(ImageTextPair(image_path, row["caption"], identifier))

    return ImageTextDataset(tuple(pairs))
