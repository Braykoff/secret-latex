"""Core find-and-replace logic: substitute {{ secret.NAME }} / {{ secret.NAME:default }}
placeholders. This never raises over a missing .env file or a missing key: it falls
back to the placeholder's default, or an empty string if there is no default, and
prints what it did for each occurrence so the LaTeX build log shows exactly which
secrets were used.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from .config import Config

LOG_PREFIX = "[secret-latex]"


def _log(message: str) -> None:
    print(f"{LOG_PREFIX} {message}")


@dataclass
class RenderResult:
    output_dir: Path
    processed_files: list[Path]


def load_secrets(env_file: Path) -> dict[str, str]:
    if not env_file.is_file():
        _log(
            f".env file not found at {env_file}; no secrets loaded, "
            "defaults (or blanks) will be used for every placeholder"
        )
        return {}
    values = dotenv_values(env_file)
    secrets = {k: v for k, v in values.items() if v is not None}
    _log(f"loaded {len(secrets)} key(s) from {env_file}")
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
            _log(f"{source_label}: {name} -> replaced with value from .env")
            return secrets[name]
        if default is not None:
            _log(f'{source_label}: {name} -> not found in .env, using default "{default}"')
            return default
        _log(f"{source_label}: {name} -> not found in .env and no default given, leaving blank")
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
    env_path = project_root / config.env_file
    secrets = load_secrets(env_path)

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
