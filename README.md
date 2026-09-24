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
extension, is parsed as dotenv syntax). Keep all three out of git (see
[Protect your secrets](#protect-your-secrets) below):

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
[`examples/secret-latex.example.toml`](examples/secret-latex.example.toml)):

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

## Using it from a LaTeX editor

`secret-latex engine <name> [flags...] file.tex` is meant to be dropped
straight into a LaTeX editor's "engine" or build-tool configuration in
place of `pdflatex`/`xelatex`/`lualatex`. It auto-detects the project root
and secrets file from the `.tex` file's own directory, forwards flags to
the real engine unchanged, and compiles directly in that directory —
substituting placeholders into the source in place just long enough for
the engine to run, then restoring the original placeholder text. No build
directory, no copies left behind: the PDF, `.log`, `.synctex.gz`, etc. show
up exactly where they always would, because that's where the compile
actually happened.

```bash
secret-latex engine pdflatex -interaction=nonstopmode -synctex=1 main.tex
```

**Recommended: tell the editor which engine to use, in the file itself.** Add
one comment on the first line of your `.tex` file, and the editor will pick
the `secret-latex` engine every time you typeset that document, instead of
you having to choose it from a dropdown (and remembering to):

```tex
%!TEX TS-program = Secret-pdfLaTeX
```

In TeXShop, the value is the name of the installed engine without the
`.engine` extension: `Secret-pdfLaTeX`, `Secret-XeLaTeX`, or
`Secret-LuaLaTeX`. Without this line, TeXShop falls back to whatever engine
is currently selected in its toolbar, which is easy to leave on plain
`pdflatex` — and then your `{{ secret.NAME }}` placeholders are compiled
as literal text. Other editors have similar comments, but they choose from
their own configured build tools; see the guide for your editor below.

See [`install/`](install/) for step-by-step setup with TeXShop, LaTeXiT,
TeXstudio, TeXworks, Kile, and VS Code's LaTeX Workshop, on macOS, Linux,
and Windows.

## Protect your secrets

The compiled PDF has your resolved secrets baked into it in plain text —
and so can the `.log`/`.aux`/`.synctex.gz` files a compile produces. None
of that is gitignored automatically; add this to your **project's**
`.gitignore`:

```gitignore
.env
secrets.json
secrets.yaml
secrets.yml
*.aux
*.log
*.synctex.gz

# only if you use `secret-latex render`/`build`, not `engine`
build/
```

See [`install/README.md`](install/README.md#protect-your-secrets) for the
full writeup, including what to do if you intentionally track the PDF.

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```
