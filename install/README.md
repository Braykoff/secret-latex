# Installing secret-latex as an editor "engine"

Most LaTeX editors don't compile documents themselves — they shell out to
`pdflatex`/`xelatex`/`lualatex` and show you the result. That means you can
point them at `secret-latex` instead: it substitutes secrets directly into
your `.tex` source, compiles it right there with the real engine, then
restores the source to its original placeholder form. No build directory,
no copies left behind anywhere — the PDF, `.log`, `.synctex.gz`, etc. land
exactly where they always would, because the compile happens in your
project directory, not somewhere else.

```
editor  --(runs)-->  secret-latex engine pdflatex [flags...] main.tex
                          |
                          v
                 1. loads secret-latex.toml + secrets file
                    from main.tex's directory
                 2. substitutes {{ secret.NAME }} placeholders
                    directly into main.tex (and any other
                    matched .tex sources), in place
                 3. runs: pdflatex [flags...] main.tex
                    (in the project directory, as normal)
                 4. restores every substituted file back to
                    its original placeholder form
```

Your `.tex` source only contains the real secret values on disk for the
few seconds the engine is actually compiling; that's restored the instant
it finishes, whether the compile succeeds, fails, or is interrupted
(Ctrl-C). The engine's own exit code is passed straight through, so error
detection in the editor keeps working normally.

The one edge case this can't cover is the process being force-killed
(`kill -9`, a crash, a power loss) mid-compile — the restore step wouldn't
get to run, and the file would keep the resolved secret on disk until the
next successful run. This is the same risk any tool that briefly writes
data to disk has; if that's a concern for your threat model, keep the
placeholders committed and never commit right after a compile without
checking `git diff` first.

## Prerequisites (all platforms)

1. A working LaTeX distribution already installed (TeX Live, MacTeX,
   MiKTeX, ...) — `secret-latex` does not install or replace this, it just
   calls into it.
2. Python 3.9+.
3. `secret-latex` installed and on your `PATH`. The most reliable way on
   any platform is [pipx](https://pipx.pypa.io/), which installs CLI tools
   into their own isolated environment and puts them on `PATH` for you:
   ```bash
   pipx install secret-latex
   secret-latex --version
   ```
   Plain `pip install secret-latex` also works, but on recent macOS and
   Ubuntu it may refuse with `externally-managed-environment` unless you
   add `--user` or use a virtual environment — pipx sidesteps that
   entirely. If `secret-latex --version` doesn't work after installing,
   your Python scripts directory isn't on `PATH` — see your platform's
   guide below.

## Protect your secrets

The compiled PDF (and `.log`/`.aux`/`.synctex.gz`) has your real secret
values baked into it in plain text — that's unavoidable, it's what you
asked to be compiled. `secret-latex`'s own `.gitignore` covers its own
repo, not your LaTeX project, so add this to your **project's**
`.gitignore`:

```gitignore
# secret-latex: secrets files and generated artifacts that may carry them
.env
secrets.json
secrets.yaml
secrets.yml
*.aux
*.log
*.synctex.gz

# only if you use `secret-latex render`/`build` from the CLI, not `engine`
build/
```

If you intentionally track the compiled PDF (e.g. a resume repo), remember
it contains the resolved secret in plain text — treat it as sensitive
before committing or sharing it, the same as you would the secrets file
itself.

## Platform guides

- [macOS: TeXShop / LaTeXiT](macos.md)
- [Linux (Ubuntu, etc.): TeXstudio / TeXworks / Kile](linux.md)
- [Windows: TeXstudio / TeXworks (MiKTeX)](windows.md)
- [VS Code: LaTeX Workshop (any platform)](vscode.md)

Every guide ends at the same place: your editor's "engine" or "build tool"
runs `secret-latex engine <name> ...` instead of `<name> ...` directly.
