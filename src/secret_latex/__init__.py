"""secret-latex: inject secrets from a .env file into LaTeX sources at build time."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("secret-latex")
except PackageNotFoundError:
    __version__ = "0+unknown"
