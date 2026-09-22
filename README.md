# secret-latex

Keep secrets (API keys, tokens, personal info) out of your `.tex` sources and
your git history. Reference them with a placeholder, keep the real values in
a local `.env` file, and let `secret-latex` fill them in at build time.

```tex
\author{ {{ secret.AUTHOR_NAME }} }
My API key is: {{ secret.API_KEY }}
Environment: {{ secret.ENVIRONMENT:staging }}
```

```env
# .env  (gitignored, never committed)
AUTHOR_NAME=Ada Lovelace
API_KEY=sk-live-...
```

A placeholder can carry a default after a colon:
`{{ secret.NAME:default value here }}`. Substitution never fails the build:

- if `.env` is missing entirely, every placeholder falls back to its default
- if a key isn't in `.env`, that placeholder falls back to its default
- if there's no default either, the placeholder is simply replaced with an
  empty string

Every one of those cases is printed to the console as it happens, so the
build log shows exactly which secrets came from `.env`, which fell back to a
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
env_file = ".env"
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
