"""JSONL loading for image-text datasets."""

import json
from pathlib import Path

from mew.data.schema import ImageTextDataset, ImageTextPair


def load_jsonl(path: Path) -> ImageTextDataset:
    """Load ordered pairs with image paths relative to the JSONL directory.

    Ignore blank lines. Raise ValueError with the source line and cause for invalid
    records; let FileNotFoundError propagate for missing files.
    """
    pairs: list[ImageTextPair] = []
    with path.open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            prefix = f"JSONL line {line_number}"
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{prefix}: malformed JSON: {error.msg}") from error
            if not isinstance(record, dict):
                raise ValueError(f"{prefix}: expected a JSON object")
            for field in ("image_path", "caption"):
                if field not in record:
                    raise ValueError(f"{prefix}: missing required key '{field}'")
                if not isinstance(record[field], str):
                    raise ValueError(f"{prefix}: '{field}' must be a string")
            identifier = record.get("id")
            if identifier is not None:
                if not isinstance(identifier, str):
                    raise ValueError(f"{prefix}: 'id' must be a string or null")
                if not identifier.strip():
                    identifier = None
            image_path = Path(record["image_path"])
            if not image_path.is_absolute():
                image_path = path.parent / image_path
            pairs.append(ImageTextPair(image_path, record["caption"], identifier))

    return ImageTextDataset(tuple(pairs))
