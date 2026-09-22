"""Core find-and-replace logic: substitute {{ secret.NAME }} / {{ secret.NAME:default }}
placeholders. This never raises over a missing or malformed secrets file, or a missing
key: it falls back to the placeholder's default, or an empty string if there is no
default, and prints what it did for each occurrence so the LaTeX build log shows
exactly which secrets were used.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import Config
from .loaders import load_secrets_file

LOG_PREFIX = "[secret-latex]"


def _log(message: str) -> None:
    print(f"{LOG_PREFIX} {message}")


@dataclass
class RenderResult:
    output_dir: Path
    processed_files: list[Path]


def load_secrets(secrets_path: Path) -> dict[str, str]:
    if not secrets_path.is_file():
        _log(
            f"secrets file not found at {secrets_path}; no secrets loaded, "
            "defaults (or blanks) will be used for every placeholder"
        )
        return {}

    def warn(message: str) -> None:
        _log(f"{secrets_path.name}: {message}")

    try:
        secrets = load_secrets_file(secrets_path, warn=warn)
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError, OSError) as exc:
        _log(
            f"could not parse secrets file {secrets_path} ({exc}); "
            "no secrets loaded, defaults (or blanks) will be used for every placeholder"
        )
        return {}

    _log(f"loaded {len(secrets)} key(s) from {secrets_path}")
    return secrets


def substitute(
    text: str, pattern: str, secrets: dict[str, str], *, source_label: str = "<text>"
) -> str:
    """Replace placeholders in `text`, logging each substitution. Never raises."""
    compiled = re.compile(pattern)

    def _replace(match: re.Match) -> str:
        name = match.group(1)
        default = match.group(2)
        if default is not None:
            default = default.strip()

        if name in secrets:
            _log(f"{source_label}: {name} -> replaced with value from secrets file")
            return secrets[name]
        if default is not None:
            _log(f'{source_label}: {name} -> not found in secrets file, using default "{default}"')
            return default
        _log(f"{source_label}: {name} -> not found in secrets file and no default given, leaving blank")
        return ""

    return compiled.sub(_replace, text)


def _source_rel_paths(project_root: Path, sources: list[str]) -> set[Path]:
    matched: set[Path] = set()
    for pattern in sources:
        for path in project_root.glob(pattern):
            if path.is_file():
                matched.add(path.relative_to(project_root))
    return matched


def render_project(project_root: Path, config: Config) -> RenderResult:
    secrets_path = project_root / config.secrets_file
    secrets = load_secrets(secrets_path)

    output_dir = project_root / config.output_dir
    exclude_dirs = {output_dir.resolve(), (project_root / ".git").resolve()}

    all_files = [
        p
        for p in project_root.rglob("*")
        if p.is_file() and not any(p.resolve().is_relative_to(d) for d in exclude_dirs)
    ]
    source_rel_paths = _source_rel_paths(project_root, config.sources)

    output_dir.mkdir(parents=True, exist_ok=True)
    processed: list[Path] = []
    for path in all_files:
        rel_path = path.relative_to(project_root)
        dest = output_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel_path in source_rel_paths:
            text = path.read_text(encoding="utf-8")
            new_text = substitute(text, config.pattern, secrets, source_label=str(rel_path))
            dest.write_text(new_text, encoding="utf-8")
            processed.append(rel_path)
        else:
            shutil.copy2(path, dest)

    return RenderResult(output_dir=output_dir, processed_files=processed)
