# secret-latex

Keep secrets (API keys, tokens, personal info) out of your `.tex` sources and
your git history. Reference them with a placeholder, keep the real values in
a local secrets file, and let `secret-latex` fill them in at build time.

```tex
\author{ {{ secret.AUTHOR_NAME }} }
My API key is: {{ secret.API_KEY }}
Environment: {{ secret.ENVIRONMENT:staging }}
```

The secrets file can be `.env`, `.json`, or `.yaml`/`.yml` — the format is
picked from its extension (anything else, including a plain `.env` with no
extension, is parsed as dotenv syntax). All three are gitignored, never
committed:

```env
# .env
AUTHOR_NAME=Ada Lovelace
API_KEY=sk-live-...
```

```json
{ "AUTHOR_NAME": "Ada Lovelace", "API_KEY": "sk-live-..." }
```

```yaml
AUTHOR_NAME: Ada Lovelace
API_KEY: sk-live-...
```

Each one must be a flat mapping of names to plain values; a nested
object/list under a key is skipped with a console warning rather than used.

A placeholder can carry a default after a colon:
`{{ secret.NAME:default value here }}`. Substitution never fails the build:

- if the secrets file is missing or fails to parse, every placeholder falls
  back to its default
- if a key isn't in the secrets file, that placeholder falls back to its
  default
- if there's no default either, the placeholder is simply replaced with an
  empty string

Every one of those cases is printed to the console as it happens, so the
build log shows exactly which secrets were loaded, which fell back to a
default, and which were left blank.

## Install

```bash
pip install secret-latex
```

## Usage

Render placeholders into a `build/` copy of your project without compiling:

```bash
secret-latex render
```

Render and immediately compile with your LaTeX engine:

```bash
secret-latex build main.tex
```

This writes the rendered project to `build/` (copying every file so
`\input`, images, and `.cls`/`.bib` files still resolve) and runs
`pdflatex -interaction=nonstopmode main.tex` inside it. The output PDF ends
up at `build/main.pdf`.

Both commands read `secret-latex.toml` from the project root if present (see
[`secret-latex.example.toml`](secret-latex.example.toml)):

```toml
[secret-latex]
secrets_file = ".env"
sources = ["**/*.tex"]
output_dir = "build"
engine = "pdflatex"
engine_args = ["-interaction=nonstopmode"]
```

CLI flags override the config file:

```bash
secret-latex build main.tex --engine xelatex --output-dir dist
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```
