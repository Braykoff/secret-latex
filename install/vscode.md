# VS Code: LaTeX Workshop (macOS / Linux / Windows)

No wrapper scripts needed here — just point a
[LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
tool at `secret-latex engine` in your workspace or user `settings.json`.

```json
{
  "latex-workshop.latex.tools": [
    {
      "name": "secret-pdflatex",
      "command": "secret-latex",
      "args": [
        "engine",
        "pdflatex",
        "-synctex=1",
        "-interaction=nonstopmode",
        "-file-line-error",
        "%DOC%.tex"
      ]
    }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "secret-pdflatex",
      "tools": ["secret-pdflatex"]
    }
  ]
}
```

Then set **secret-pdflatex** as the default recipe (or pick it from the
LaTeX Workshop recipe dropdown before building). Swap `pdflatex` for
`xelatex`/`lualatex` in both the tool name and `args` if you use a
different engine.

First make sure `secret-latex` is installed and on `PATH` (`pip install
secret-latex`, then `secret-latex --version` in a terminal) — VS Code runs
tools using the same `PATH` as the terminal it was launched from.

## Project setup

In the same directory as your `.tex` file, add:

- a secrets file — `.env`, `secrets.json`, or `secrets.yaml`
- optionally a `secret-latex.toml` if you need a non-default secrets
  filename, output directory, or placeholder pattern (see the repo README)

Reference secrets in your source with `{{ secret.NAME }}` or
`{{ secret.NAME:default value }}`. The compile happens directly in your
project directory (no build directory involved), so the PDF, `.log`,
`.synctex.gz`, etc. show up exactly where LaTeX Workshop's PDF viewer and
SyncTeX already expect them.
