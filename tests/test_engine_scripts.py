import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "install" / "scripts" / "macos"

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="POSIX shell scripts")


def _run_script(script: str, tmp_path: Path, *args: str, install_fake: bool):
    fake_home = tmp_path / "home"
    fake_bin = fake_home / ".local" / "bin"
    fake_bin.mkdir(parents=True)
    record = tmp_path / "argv.txt"
    if install_fake:
        fake = fake_bin / "secret-latex"
        fake.write_text('#!/bin/sh\nfor a in "$@"; do printf "%s\\n" "$a"; done > "$RECORD"\n')
        fake.chmod(0o755)

    # A GUI app like TeXShop starts scripts with a bare launchd-style PATH.
    env = {"HOME": str(fake_home), "PATH": "/usr/bin:/bin", "RECORD": str(record)}
    result = subprocess.run(
        ["sh", str(SCRIPTS_DIR / script), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, record


@pytest.mark.parametrize(
    ("script", "engine"),
    [
        ("Secret-pdfLaTeX.engine", "pdflatex"),
        ("Secret-XeLaTeX.engine", "xelatex"),
        ("Secret-LuaLaTeX.engine", "lualatex"),
    ],
)
def test_engine_script_finds_secret_latex_and_passes_only_the_file(
    tmp_path: Path, script: str, engine: str
):
    tex_path = str(tmp_path / "doc.tex")

    # TeXShop may pass extra arguments after the file; they must not be forwarded.
    result, record = _run_script(script, tmp_path, tex_path, "extra args", install_fake=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert record.read_text().splitlines() == [
        "engine",
        engine,
        "-file-line-error",
        "-synctex=1",
        tex_path,
    ]


def test_engine_script_reports_clearly_when_secret_latex_is_missing(tmp_path: Path):
    result, _ = _run_script(
        "Secret-pdfLaTeX.engine", tmp_path, str(tmp_path / "doc.tex"), install_fake=False
    )

    assert result.returncode == 127
    assert "secret-latex: command not found" in result.stdout
