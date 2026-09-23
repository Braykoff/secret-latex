# Windows: TeXstudio / TeXworks (MiKTeX)

## 1. Install

```powershell
pip install --user pipx  # if you don't already have pipx
pipx install secret-latex
secret-latex --version
```

(Plain `pip install secret-latex` also works on Windows, but pipx keeps it
isolated and reliably on `PATH`.) If `secret-latex --version` says "not
recognized", run `python -m pip show -f secret-latex` to find where it was
installed, add that folder's `Scripts` directory to your `PATH` (System
Properties > Environment Variables), then open a new terminal.

Then run the wrapper-script installer:

```powershell
cd install\scripts\windows
.\install.ps1
```

(If PowerShell blocks the script, run it from an elevated prompt with
`Set-ExecutionPolicy -Scope Process RemoteSigned` first, or right-click the
file and choose "Run with PowerShell".)

This copies `secret-pdflatex.bat`, `secret-xelatex.bat`, and
`secret-lualatex.bat` into `%USERPROFILE%\secret-latex\bin\` and prints
their full paths — you'll paste those into your editor's config below.

## 2. TeXstudio

Options > Configure TeXstudio > Build > Commands. Replace the default
command for each engine you use with the matching `.bat` file's full path,
keeping the existing flags. For example, the default PdfLaTeX command:

```
pdflatex -synctex=1 -interaction=nonstopmode %.tex
```

becomes:

```
C:\Users\<you>\secret-latex\bin\secret-pdflatex.bat -synctex=1 -interaction=nonstopmode %.tex
```

## 3. TeXworks (bundled with MiKTeX)

Edit > Preferences > Typesetting > Processing tools. Add a new tool:

- **Program**: `C:\Users\<you>\secret-latex\bin\secret-pdflatex.bat`
- **Arguments**: `-synctex=1`, `-interaction=nonstopmode`, `$fullname`

Select it from the toolbar dropdown before typesetting.

## 4. Set up your project

In the same directory as your `.tex` file, add:

- a secrets file — `.env`, `secrets.json`, or `secrets.yaml`
- optionally a `secret-latex.toml` if you need a non-default secrets
  filename, output directory, or placeholder pattern (see the repo README)

Reference secrets in your source with `{{ secret.NAME }}` or
`{{ secret.NAME:default value }}`, then build as usual. The compile happens
directly in your project directory (no build directory involved), so the
PDF, `.log`, `.synctex.gz`, etc. show up exactly where they always would.
