"""Path and caption validation for image-text datasets."""

from dataclasses import dataclass

from mew.data.schema import ImageTextDataset


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One validation failure at a 1-based dataset position."""

    record_index: int
    field: str
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Validation counts and ordered issues for a dataset."""

    total: int
    valid: int
    invalid: int
    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        """Whether every record passed validation, including an empty dataset."""
        return self.invalid == 0


def validate_dataset(dataset: ImageTextDataset) -> ValidationReport:
    """Check captions, filesystem status, and extensions without reading image contents.

    Issues follow dataset order, then caption, filesystem status, and extension order.
    Each record with issues counts as invalid once. The input is never modified.
    """
    issues: list[ValidationIssue] = []
    invalid = 0
    for index, pair in enumerate(dataset, start=1):
        before = len(issues)
        if not pair.caption.strip():
            issues.append(
                ValidationIssue(index, "caption", "empty_caption", "Caption must not be blank.")
            )
        if not pair.image_path.exists():
            issues.append(
                ValidationIssue(
                    index, "image_path", "missing_image", f"Image does not exist: {pair.image_path}"
                )
            )
        elif not pair.image_path.is_file():
            issues.append(
                ValidationIssue(
                    index,
                    "image_path",
                    "not_a_file",
                    f"Image path is not a file: {pair.image_path}",
                )
            )
        if pair.image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            issues.append(
                ValidationIssue(
                    index,
                    "image_path",
                    "unsupported_extension",
                    f"Unsupported image extension: {pair.image_path.suffix!r}",
                )
            )
        if len(issues) > before:
            invalid += 1

    return ValidationReport(len(dataset), len(dataset) - invalid, invalid, tuple(issues))
