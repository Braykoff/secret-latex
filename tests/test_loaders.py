from pathlib import Path

import pytest

from secret_latex.loaders import load_secrets_file


def _warnings():
    messages: list[str] = []
    return messages, messages.append


def test_load_dotenv_file(tmp_path: Path):
    path = tmp_path / ".env"
    path.write_text("API_KEY=abc123\n")
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {"API_KEY": "abc123"}
    assert messages == []


def test_load_json_file(tmp_path: Path):
    path = tmp_path / "secrets.json"
    path.write_text('{"API_KEY": "abc123", "PORT": 8080, "DEBUG": true}')
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {
        "API_KEY": "abc123",
        "PORT": "8080",
        "DEBUG": "True",
    }
    assert messages == []


def test_load_yaml_file(tmp_path: Path):
    path = tmp_path / "secrets.yaml"
    path.write_text("API_KEY: abc123\nPORT: 8080\n")
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {"API_KEY": "abc123", "PORT": "8080"}
    assert messages == []


def test_load_yml_extension_uses_yaml_parser(tmp_path: Path):
    path = tmp_path / "secrets.yml"
    path.write_text("API_KEY: abc123\n")
    _, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {"API_KEY": "abc123"}


def test_json_nested_value_is_skipped_with_warning(tmp_path: Path):
    path = tmp_path / "secrets.json"
    path.write_text('{"API_KEY": "abc123", "nested": {"a": 1}}')
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {"API_KEY": "abc123"}
    assert any("nested" in m for m in messages)


def test_yaml_null_value_is_skipped_with_warning(tmp_path: Path):
    path = tmp_path / "secrets.yaml"
    path.write_text("API_KEY: abc123\nEMPTY:\n")
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {"API_KEY": "abc123"}
    assert any("EMPTY" in m for m in messages)


def test_json_top_level_list_is_rejected(tmp_path: Path):
    path = tmp_path / "secrets.json"
    path.write_text("[1, 2, 3]")
    messages, warn = _warnings()
    assert load_secrets_file(path, warn=warn) == {}
    assert messages


def test_malformed_json_raises_json_decode_error(tmp_path: Path):
    import json

    path = tmp_path / "secrets.json"
    path.write_text("{not valid json")
    with pytest.raises(json.JSONDecodeError):
        load_secrets_file(path, warn=lambda _: None)
