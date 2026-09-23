from pathlib import Path

from secret_latex.config import Config
from secret_latex.render import render_in_place, render_project, substitute


def test_substitute_replaces_known_placeholder():
    text = r"\author{ {{ secret.AUTHOR_NAME }} }"
    new_text = substitute(text, Config().pattern, {"AUTHOR_NAME": "Jane Doe"})
    assert new_text == r"\author{ Jane Doe }"


def test_substitute_uses_default_when_key_missing():
    text = "{{ secret.API_KEY:fallback-key }}"
    new_text = substitute(text, Config().pattern, {})
    assert new_text == "fallback-key"


def test_substitute_prefers_env_value_over_default():
    text = "{{ secret.API_KEY:fallback-key }}"
    new_text = substitute(text, Config().pattern, {"API_KEY": "real-key"})
    assert new_text == "real-key"


def test_substitute_leaves_blank_when_no_value_and_no_default():
    text = "before {{secret.MISSING_KEY}} after"
    new_text = substitute(text, Config().pattern, {})
    assert new_text == "before  after"


def test_render_project_never_raises_when_env_file_missing(tmp_path: Path):
    (tmp_path / "main.tex").write_text(r"\newcommand{\key}{ {{ secret.API_KEY:demo }} }")

    result = render_project(tmp_path, Config())

    rendered = (result.output_dir / "main.tex").read_text()
    assert "demo" in rendered


def test_render_project_writes_output_and_copies_other_files(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=abc123\n")
    (tmp_path / "main.tex").write_text(r"\newcommand{\key}{ {{ secret.API_KEY }} }")
    (tmp_path / "figure.png").write_bytes(b"\x89PNG\r\n")

    result = render_project(tmp_path, Config())

    rendered = (result.output_dir / "main.tex").read_text()
    assert "abc123" in rendered
    assert (result.output_dir / "figure.png").read_bytes() == b"\x89PNG\r\n"


def test_render_project_reads_json_secrets_file(tmp_path: Path):
    (tmp_path / "secrets.json").write_text('{"API_KEY": "abc123"}')
    (tmp_path / "main.tex").write_text(r"{{ secret.API_KEY }}")

    result = render_project(tmp_path, Config(secrets_file="secrets.json"))

    rendered = (result.output_dir / "main.tex").read_text()
    assert rendered == "abc123"


def test_render_project_reads_yaml_secrets_file(tmp_path: Path):
    (tmp_path / "secrets.yaml").write_text("API_KEY: abc123\n")
    (tmp_path / "main.tex").write_text(r"{{ secret.API_KEY }}")

    result = render_project(tmp_path, Config(secrets_file="secrets.yaml"))

    rendered = (result.output_dir / "main.tex").read_text()
    assert rendered == "abc123"


def test_render_in_place_substitutes_during_block_and_restores_after(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=abc123\n")
    tex_path = tmp_path / "main.tex"
    original = r"\newcommand{\key}{ {{ secret.API_KEY }} }"
    tex_path.write_text(original)

    with render_in_place(tmp_path, Config()) as rendered:
        assert rendered == [Path("main.tex")]
        assert "abc123" in tex_path.read_text()
        assert not (tmp_path / "build").exists()

    assert tex_path.read_text() == original


def test_render_in_place_restores_file_even_if_block_raises(tmp_path: Path):
    (tmp_path / ".env").write_text("API_KEY=abc123\n")
    tex_path = tmp_path / "main.tex"
    original = r"{{ secret.API_KEY }}"
    tex_path.write_text(original)

    try:
        with render_in_place(tmp_path, Config()):
            assert tex_path.read_text() == "abc123"
            raise RuntimeError("simulated engine crash")
    except RuntimeError:
        pass

    assert tex_path.read_text() == original
