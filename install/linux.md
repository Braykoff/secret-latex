# Linux (Ubuntu, etc.): TeXstudio / TeXworks / Kile

## 1. Install

```bash
sudo apt install pipx && pipx ensurepath   # if you don't already have pipx
pipx install secret-latex
secret-latex --version
```

(Plain `pip3 install --user secret-latex` may fail on Ubuntu 23.04+ with an
`externally-managed-environment` error — pipx avoids that.)

If `secret-latex --version` says "command not found" after installing,
open a new terminal so your updated `PATH` takes effect, or run `pipx
ensurepath` again and re-check.

No wrapper scripts are needed on Linux — once `secret-latex` is on `PATH`,
you reference it directly in your editor's build command.

## 2. TeXstudio

Options > Configure TeXstudio > Build > Commands. Replace the default
command for each engine you use, prefixing it with `secret-latex engine
<name>`. For example, the default PdfLaTeX command:

```
pdflatex -synctex=1 -interaction=nonstopmode %.tex
```

becomes:

```
secret-latex engine pdflatex -synctex=1 -interaction=nonstopmode %.tex
```

Do the same for XeLaTeX/LuaLaTeX if you use them. TeXstudio still expands
`%.tex` to the real filename before running the command, so nothing else
about your build configuration needs to change.

## 3. TeXworks

Edit > Preferences > Typesetting > Processing tools. Add a new tool:

- **Program**: `secret-latex`
- **Arguments**: `engine`, `pdflatex`, `-synctex=1`, `-interaction=nonstopmode`, `$fullname`

(one argument per line/field, in that order). Select it from the toolbar
dropdown before typesetting.

## 4. Kile

Settings > Configure Kile > Build > select your LaTeX tool and change its
command from `pdflatex` to `secret-latex engine pdflatex`, keeping the
existing arguments/options field as-is.

## 5. Set up your project

In the same directory as your `.tex` file, add:

- a secrets file — `.env`, `secrets.json`, or `secrets.yaml`
- optionally a `secret-latex.toml` if you need a non-default secrets
  filename, output directory, or placeholder pattern (see the repo README)

Reference secrets in your source with `{{ secret.NAME }}` or
`{{ secret.NAME:default value }}`, then build as usual. The compile happens
directly in your project directory (no build directory involved), so the
PDF, `.log`, `.synctex.gz`, etc. show up exactly where they always would.
