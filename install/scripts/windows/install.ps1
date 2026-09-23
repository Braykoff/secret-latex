# Installs secret-latex and drops convenience wrapper scripts for
# TeXstudio/TeXworks into a folder you can reference directly.
# Usage (PowerShell): .\install.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $env:USERPROFILE "secret-latex\bin"

Write-Host "==> Installing/upgrading secret-latex"
if (Get-Command pipx -ErrorAction SilentlyContinue) {
    pipx install --force secret-latex
} else {
    python -m pip install --user --upgrade secret-latex
}

$onPath = $null -ne (Get-Command secret-latex -ErrorAction SilentlyContinue)
if (-not $onPath) {
    Write-Host ""
    Write-Host "WARNING: 'secret-latex' isn't on your PATH yet." -ForegroundColor Yellow
    Write-Host "If you used pipx, run: pipx ensurepath"
    Write-Host "If you used pip, run 'python -m pip show -f secret-latex' to find its"
    Write-Host "Scripts folder and add that folder to your PATH before continuing."
    Write-Host ""
}

Write-Host "==> Installing wrapper scripts into $InstallDir"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
foreach ($name in "secret-pdflatex.bat", "secret-xelatex.bat", "secret-lualatex.bat") {
    Copy-Item (Join-Path $ScriptDir $name) (Join-Path $InstallDir $name) -Force
    Write-Host "  installed $name"
}

Write-Host ""
Write-Host "Done."
Write-Host ""
Write-Host "In TeXstudio: Options > Configure TeXstudio > Build, and replace the"
Write-Host "pdflatex/xelatex/lualatex command with:"
Write-Host "  $InstallDir\secret-pdflatex.bat -synctex=1 -interaction=nonstopmode %.tex"
Write-Host ""
Write-Host "In TeXworks: Edit > Preferences > Typesetting, add a tool whose Program is"
Write-Host "  $InstallDir\secret-pdflatex.bat"
Write-Host ""
Write-Host "Put a secret-latex.toml and a .env/.json/.yaml secrets file next to your"
Write-Host ".tex source -- see the repo's README for the placeholder syntax."
