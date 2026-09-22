"""Configuration loading for secret-latex.

Settings are resolved in this order (later wins): built-in defaults,
``secret-latex.toml`` in the project root, then CLI flags.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, fields
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_FILENAME = "secret-latex.toml"

# Matches placeholders like {{ secret.API_KEY }} or {{ secret.API_KEY:fallback value }}
# inside .tex sources. Group 1 is the key name, group 2 (optional) is the default.
DEFAULT_PATTERN = r"\{\{\s*secret\.([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\s*\}\}"


@dataclass
class Config:
    env_file: str = ".env"
    sources: list[str] = field(default_factory=lambda: ["**/*.tex"])
    output_dir: str = "build"
    engine: str = "pdflatex"
    engine_args: list[str] = field(default_factory=lambda: ["-interaction=nonstopmode"])
    pattern: str = DEFAULT_PATTERN

    @classmethod
    def load(cls, project_root: Path) -> Config:
        config_path = project_root / CONFIG_FILENAME
        if not config_path.is_file():
            return cls()

        with config_path.open("rb") as fh:
            raw = tomllib.load(fh)

        data = raw.get("tool", {}).get("secret-latex", raw.get("secret-latex", {}))
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(
                f"Unknown key(s) in {CONFIG_FILENAME}: {', '.join(sorted(unknown))}"
            )
        return cls(**data)
