import sys
from pathlib import Path

from secret_latex.cli import main

FAKE_ENGINE = """
import pathlib
import sys

tex_path = pathlib.Path(sys.argv[-1])
stem = tex_path.stem
pathlib.Path(f"{stem}.pdf").write_bytes(b"%PDF-fake")
pathlib.Path(f"{stem}.log").write_text("fake compile log\\n")
"""


def test_engine_command_compiles_in_place_and_restores_source(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=abc123\n")
    (tmp_path / "main.tex").write_text(r"\newcommand{\key}{ {{ secret.API_KEY }} }")

    fake_engine = tmp_path / "fake_engine.py"
    fake_engine.write_text(FAKE_ENGINE)

    exit_code = main(
        ["engine", sys.executable, str(fake_engine), str(tmp_path / "main.tex")]
    )

    assert exit_code == 0
    # Output lands directly next to the source -- no build/ directory at all.
    assert (tmp_path / "main.pdf").read_bytes() == b"%PDF-fake"
    assert (tmp_path / "main.log").is_file()
    assert not (tmp_path / "build").exists()
    # The source is restored to its original placeholder form afterward.
    assert "{{ secret.API_KEY }}" in (tmp_path / "main.tex").read_text()


def test_engine_command_restores_source_even_if_engine_fails(tmp_path: Path):
    (tmp_path / "main.tex").write_text(r"{{ secret.API_KEY }}")
    failing_engine = tmp_path / "failing_engine.py"
    failing_engine.write_text("import sys\nsys.exit(1)\n")

    exit_code = main(
        ["engine", sys.executable, str(failing_engine), str(tmp_path / "main.tex")]
    )

    assert exit_code == 1
    assert (tmp_path / "main.tex").read_text() == r"{{ secret.API_KEY }}"


def test_engine_command_errors_cleanly_on_missing_file(tmp_path: Path):
    exit_code = main(["engine", "pdflatex", str(tmp_path / "nope.tex")])
    assert exit_code == 1


def test_engine_command_errors_cleanly_with_no_file_argument():
    exit_code = main(["engine", "pdflatex"])
    assert exit_code == 1


def test_engine_command_errors_cleanly_when_engine_binary_missing(tmp_path: Path):
    (tmp_path / "main.tex").write_text(r"{{ secret.API_KEY }}")

    exit_code = main(["engine", "no-such-engine-binary", str(tmp_path / "main.tex")])

    assert exit_code == 1
    assert (tmp_path / "main.tex").read_text() == r"{{ secret.API_KEY }}"
