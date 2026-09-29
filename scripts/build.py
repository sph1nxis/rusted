#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
LANGUAGES_DIR = SRC_DIR / "languages"
THEMES_DIR = ROOT_DIR / "themes"
THEME_PATH = THEMES_DIR / "rusted.json"

PALETTE_REFERENCE = re.compile(r"\$\{palette\.([^}]+)\}")


def load_json(path: Path) -> Any:
    """Load and parse a JSON file."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_nested_value(obj: Any, path: str) -> Any:
    """Resolve a dotted path inside a nested dictionary."""
    current = obj

    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None

        current = current[key]

    return current


def resolve_string(value: str, palette: dict[str, Any]) -> str:
    """Resolve ${palette.foo.bar} references in a string."""

    def replace(match: re.Match[str]) -> str:
        reference = match.group(0)
        path = match.group(1)

        resolved = get_nested_value(palette, path)

        if resolved is None:
            print(
                f"Warning: Palette reference not found: {reference}",
                file=sys.stderr,
            )
            return reference

        return str(resolved)

    return PALETTE_REFERENCE.sub(replace, value)


def resolve_references(value: Any, palette: dict[str, Any]) -> Any:
    """Recursively resolve palette references in JSON-compatible data."""

    if isinstance(value, str):
        return resolve_string(value, palette)

    if isinstance(value, list):
        return [resolve_references(item, palette) for item in value]

    if isinstance(value, dict):
        return {
            key: resolve_references(item, palette)
            for key, item in value.items()
        }

    return value


def load_language_tokens(directory: Path) -> list[Any]:
    """Load and concatenate all language token definitions."""

    if not directory.exists():
        print(
            f"Warning: Languages directory not found: {directory}",
            file=sys.stderr,
        )
        return []

    tokens: list[Any] = []

    files = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix == ".json"
    )

    for path in files:
        try:
            language_tokens = load_json(path)
            language_name = path.stem

            if not isinstance(language_tokens, list):
                raise ValueError("expected a JSON array")

            print(
                f"  Loaded language: "
                f"{language_name} ({len(language_tokens)} scopes)"
            )

            tokens.extend(language_tokens)

        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"  Error loading {path.name}: {error}", file=sys.stderr,)

    return tokens


def write_json(path: Path, data: Any) -> None:
    """Write JSON using stable, human-readable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")

        temporary_path.replace(path)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def build() -> bool:
    """Build the rusted VS Code theme.

    Returns True on success and False on failure.
    """

    print("Building rusted theme...\n")

    try:
        palette = load_json(SRC_DIR / "palette.json")
        print("Loaded palette")

        workbench_colors = load_json(SRC_DIR / "workbench-colors.json")
        resolved_workbench = resolve_references(
            workbench_colors,
            palette,
        )
        print("Resolved workbench colors")

        print("\nLoading language tokens:")

        syntax_tokens = load_language_tokens(LANGUAGES_DIR)
        resolved_syntax = resolve_references(
            syntax_tokens,
            palette,
        )

        print(f"\nTotal syntax scopes: {len(resolved_syntax)}")

        semantic_tokens = load_json(SRC_DIR / "semantic-tokens.json")
        resolved_semantic = resolve_references(semantic_tokens, palette)
        print("Resolved semantic tokens")

        terminal_colors = load_json(SRC_DIR / "terminal-colors.json")
        resolved_terminal = resolve_references(terminal_colors, palette)
        print("Resolved terminal colors")

        all_colors = { **resolved_workbench, **resolved_terminal }

        theme = {
            "name": "rusted",
            "type": "dark",
            "semanticHighlighting": True,
            "colors": all_colors,
            "tokenColors": resolved_syntax,
            "semanticTokenColors": resolved_semantic,
        }

        write_json(THEME_PATH, theme)

        print("\nTheme built successfully!")
        print(f"Output: {THEME_PATH}")

        color_count = len(all_colors)
        semantic_count = len(resolved_semantic)

        print("\nTheme stats:")
        print(f"   • Colors: {color_count}")
        print(f"   • Syntax scopes: {len(resolved_syntax)}")
        print(f"   • Semantic tokens: {semantic_count}")

        return True

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(f"\nBuild failed: {error}", file=sys.stderr)
        return False


def main() -> int:
    return 0 if build() else 1


if __name__ == "__main__":
    raise SystemExit(main())

