# macOS: TeXShop / LaTeXiT

## 1. Install

```bash
brew install pipx && pipx ensurepath   # if you don't already have pipx
pipx install secret-latex
```

(Plain `pip3 install secret-latex` often fails on recent macOS with an
`externally-managed-environment` error — pipx avoids that.)

Then run the installer, which registers `secret-latex` as a TeXShop engine:

```bash
cd install/scripts/macos
sh install.sh
```

This copies `Secret-pdfLaTeX.engine`, `Secret-XeLaTeX.engine`, and
`Secret-LuaLaTeX.engine` into `~/Library/TeXShop/Engines/` (creating it if
needed) and makes them executable.

## 2. TeXShop

Quit and reopen TeXShop. In the Typeset menu (or the engine dropdown in the
toolbar), you'll now see **Secret-pdfLaTeX** / **Secret-XeLaTeX** /
**Secret-LuaLaTeX** alongside the built-in engines. Pick one and typeset as
normal — the PDF, `.synctex.gz` (for Cmd-click sync), and log all show up
next to your `.tex` file exactly as they would with the real engine.

TeXShop is a GUI app, so it doesn't see your shell's `PATH`; the engine
scripts add `~/.local/bin` (pipx), Homebrew, and `/Library/TeX/texbin`
themselves. If a typeset does nothing or the console shows
`secret-latex: command not found`, check that `secret-latex --version`
works in Terminal, then re-run `install.sh` so you have the latest scripts
(and quit and reopen TeXShop). You can also reproduce what TeXShop does
from Terminal, which prints any error directly:

```bash
cd /path/to/your/project
env -i HOME="$HOME" PATH=/usr/bin:/bin \
  ~/Library/TeXShop/Engines/Secret-pdfLaTeX.engine "$PWD/main.tex"
```

The **Abort** button is safe: it restores your source file before exiting.

## 3. LaTeXiT

LaTeXiT lets you point its compiler paths at a custom script in
Preferences > Compilation. Set the pdflatex/xelatex/lualatex path field to,
for example:

```
~/Library/TeXShop/Engines/Secret-pdfLaTeX.engine
```

## 4. Set up your project

In the same directory as your `.tex` file, add:

- a secrets file — `.env`, `secrets.json`, or `secrets.yaml`
- optionally a `secret-latex.toml` if you need a non-default secrets
  filename, output directory, or placeholder pattern (see the repo README)

Reference secrets in your source with `{{ secret.NAME }}` or
`{{ secret.NAME:default value }}`, then typeset as usual.
