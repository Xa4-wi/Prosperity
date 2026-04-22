from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple


Replacement = Tuple[str, str]


def load_variant(base_filename: str, replacements: Iterable[Replacement], target_globals: dict) -> None:
    base_path = Path(__file__).with_name(base_filename)
    source = base_path.read_text()

    for old, new in replacements:
        if old not in source:
            raise RuntimeError(f"Could not find expected snippet in {base_filename}: {old[:80]!r}")
        source = source.replace(old, new, 1)

    namespace = {
        "__file__": str(base_path),
        "__name__": target_globals.get("__name__", "__main__"),
        "__package__": target_globals.get("__package__"),
    }
    exec(compile(source, str(base_path), "exec"), namespace)
    target_globals.update(namespace)
