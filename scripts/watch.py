#!/usr/bin/env python3

import sys
import time
from datetime import datetime
from pathlib import Path

from build import build


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
LANGUAGES_DIR = SRC_DIR / "languages"

WATCHED_DIRECTORIES = (
    SRC_DIR,
    LANGUAGES_DIR,
)

POLL_INTERVAL = 0.1
DEBOUNCE_INTERVAL = 0.1


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def get_watched_files() -> dict[Path, tuple[int, int]]:
    """Return file signatures for all watched JSON files."""

    files: dict[Path, tuple[int, int]] = {}

    for directory in WATCHED_DIRECTORIES:
        if not directory.exists():
            continue

        for path in directory.glob("*.json"):
            if not path.is_file():
                continue

            try:
                stat = path.stat()
            except OSError:
                continue

            files[path] = (
                stat.st_mtime_ns,
                stat.st_size,
            )

    return files


def find_changes(
    previous: dict[Path, tuple[int, int]],
    current: dict[Path, tuple[int, int]],
) -> list[Path]:
    """Return paths that were created, deleted or modified."""

    changed = []

    for path in current.keys() | previous.keys():
        if previous.get(path) != current.get(path):
            changed.append(path)

    return sorted(changed)


def print_changes(paths: list[Path]) -> None:
    for path in paths:
        relative_path = path.relative_to(ROOT_DIR)
        print(f"[{timestamp()}] Changed: {relative_path}")


def wait_for_changes(
    previous: dict[Path, tuple[int, int]],
) -> tuple[dict[Path, tuple[int, int]], list[Path]]:
    """Wait until watched files change.

    A short debounce window groups several filesystem changes into
    one build, which is useful when an editor saves a file through
    a temporary file or performs several writes in quick succession.
    """

    while True:
        time.sleep(POLL_INTERVAL)

        current = get_watched_files()
        changes = find_changes(previous, current)

        if not changes:
            continue

        print_changes(changes)

        deadline = time.monotonic() + DEBOUNCE_INTERVAL

        while True:
            remaining = deadline - time.monotonic()

            if remaining <= 0:
                break

            time.sleep(min(POLL_INTERVAL, remaining))

            newer = get_watched_files()

            if newer != current:
                current = newer
                deadline = time.monotonic() + DEBOUNCE_INTERVAL

        return current, find_changes(previous, current)


def main() -> int:
    print("Watching src/*.json and src/languages/*.json...\n")

    if not build():
        print(
            "\nInitial build failed. Watching for changes...\n",
            file=sys.stderr,
        )

    previous = get_watched_files()

    try:
        while True:
            previous, _ = wait_for_changes(previous)

            if not build():
                print(
                    "\nBuild failed. Watching for changes...\n",
                    file=sys.stderr,
                )

    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

