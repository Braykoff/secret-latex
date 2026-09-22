"""Parsers for the different secrets-file formats: .env, .json, .yaml/.yml.

Every loader returns a flat ``dict[str, str]``. A secrets file is expected to
be a single-level mapping of names to scalar values (strings, numbers,
booleans); nested objects/lists aren't valid secrets and are skipped with a
warning rather than raised, consistent with the rest of secret-latex never
failing a build over a secrets-file problem.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from dotenv import dotenv_values

JSON_EXTENSIONS = {".json"}
YAML_EXTENSIONS = {".yaml", ".yml"}


def _flatten_scalars(data: dict, *, warn) -> dict[str, str]:
    secrets: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            warn(f'key "{key}" is a nested object/list, not a plain value; skipping it')
            continue
        if value is None:
            warn(f'key "{key}" has no value (null); skipping it')
            continue
        secrets[str(key)] = value if isinstance(value, str) else str(value)
    return secrets


def load_dotenv_file(path: Path) -> dict[str, str]:
    values = dotenv_values(path)
    return {k: v for k, v in values.items() if v is not None}


def load_json_file(path: Path, *, warn) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        warn("top-level JSON value must be an object of key-value pairs; ignoring file")
        return {}
    return _flatten_scalars(data, warn=warn)


def load_yaml_file(path: Path, *, warn) -> dict[str, str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        warn("top-level YAML value must be a mapping of key-value pairs; ignoring file")
        return {}
    return _flatten_scalars(data, warn=warn)


def load_secrets_file(path: Path, *, warn) -> dict[str, str]:
    """Parse `path` into a flat dict, choosing the format from its extension.

    Anything that isn't recognized as JSON or YAML (including plain `.env`
    files, which have no extension) is parsed as dotenv syntax.
    """
    suffix = path.suffix.lower()
    if suffix in JSON_EXTENSIONS:
        return load_json_file(path, warn=warn)
    if suffix in YAML_EXTENSIONS:
        return load_yaml_file(path, warn=warn)
    return load_dotenv_file(path)
