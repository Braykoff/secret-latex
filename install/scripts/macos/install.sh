#!/bin/sh
# Installs secret-latex and registers it as a TeXShop engine.
# Usage: sh install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINES_DIR="$HOME/Library/TeXShop/Engines"

echo "==> Installing/upgrading secret-latex"
if command -v pipx >/dev/null 2>&1; then
    pipx install --force secret-latex
else
    pip_log="$(mktemp)"
    trap 'rm -f "$pip_log"' EXIT
    if ! python3 -m pip install --user --upgrade secret-latex >"$pip_log" 2>&1; then
        cat "$pip_log" >&2
        echo >&2
        echo "pip refused to install outside a virtual environment (this is normal on" >&2
        echo "recent macOS Python installs). Install pipx and re-run this script:" >&2
        echo "  brew install pipx && pipx ensurepath" >&2
        exit 1
    fi
fi

if ! command -v secret-latex >/dev/null 2>&1; then
    echo
    echo "WARNING: 'secret-latex' isn't on your PATH yet."
    echo "If you used pipx, run: pipx ensurepath"
    echo "If you used pip --user, find its bin dir with: python3 -m pip show -f secret-latex"
    echo "and add that directory to your PATH before continuing."
    echo
fi

echo "==> Installing TeXShop engine scripts into $ENGINES_DIR"
mkdir -p "$ENGINES_DIR"
for engine in Secret-pdfLaTeX.engine Secret-XeLaTeX.engine Secret-LuaLaTeX.engine; do
    cp "$SCRIPT_DIR/$engine" "$ENGINES_DIR/$engine"
    chmod +x "$ENGINES_DIR/$engine"
    echo "  installed $engine"
done

cat <<'EOF'

Done.

TeXShop: quit and reopen TeXShop, then pick "Secret-pdfLaTeX" (or
Secret-XeLaTeX / Secret-LuaLaTeX) from the Typeset menu / engine dropdown.

LaTeXiT: in Preferences > Compilation, point the pdflatex/xelatex/lualatex
path field at one of these scripts instead of the real binary, e.g.:
  ~/Library/TeXShop/Engines/Secret-pdfLaTeX.engine

Either way, put a secret-latex.toml and a .env/.json/.yaml secrets file next
to your .tex source — see the repo's README for the placeholder syntax.
EOF
