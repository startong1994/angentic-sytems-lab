from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReadFileResult:
    bytes: int
    preview: str


class ReadFileError(Exception):
    pass


def read_file_safe(*, repo_root: Path, relative_path: str, max_bytes: int = 64_000) -> ReadFileResult:
    """
    Read-only tool with guardrails:
    - Only allows reads under <repo_root>/data
    - Blocks path traversal
    - Enforces size limit
    """
    data_root = (repo_root / "data").resolve()
    target = (repo_root / relative_path).resolve()

    if not str(target).startswith(str(data_root) + str(Path("/").as_posix()).replace("//", "/")[:-1]) and target != data_root:
        # simpler: require the target be within data_root
        if data_root not in target.parents and target != data_root:
            raise ReadFileError("path_outside_data_dir")

    if not target.exists() or not target.is_file():
        raise ReadFileError("file_not_found")

    size = target.stat().st_size
    if size > max_bytes:
        raise ReadFileError("file_too_large")

    content = target.read_text(encoding="utf-8", errors="replace")
    preview = content[:200]
    return ReadFileResult(bytes=len(content.encode("utf-8", errors="replace")), preview=preview)
