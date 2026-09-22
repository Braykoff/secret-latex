"""Command-line interface for secret-latex."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__
from .config import Config
from .render import render_project


def _build_config(args: argparse.Namespace) -> Config:
    config = Config.load(args.root)
    if args.env_file is not None:
        config.env_file = args.env_file
    if args.output_dir is not None:
        config.output_dir = args.output_dir
    return config


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="project root containing the LaTeX sources and .env file (default: cwd)",
    )
    parser.add_argument("--env-file", help="path to the .env file, relative to --root")
    parser.add_argument("--output-dir", help="directory to write rendered output into")


def _run_render(args: argparse.Namespace) -> int:
    try:
        config = _build_config(args)
        result = render_project(args.root, config)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"rendered {len(result.processed_files)} file(s) into {result.output_dir}")
    return 0


def _run_build(args: argparse.Namespace) -> int:
    try:
        config = _build_config(args)
        if args.engine is not None:
            config.engine = args.engine
        if args.engine_arg:
            config.engine_args = args.engine_arg
        result = render_project(args.root, config)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    main_tex = result.output_dir / args.main_tex
    if not main_tex.is_file():
        print(f"error: main tex file not found after rendering: {main_tex}", file=sys.stderr)
        return 1

    command = [config.engine, *config.engine_args, main_tex.name]
    print(f"running: {' '.join(command)} (in {result.output_dir})")
    proc = subprocess.run(command, cwd=result.output_dir, check=False)
    return proc.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="secret-latex",
        description="Inject secrets from a .env file into LaTeX sources at build time.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser(
        "render", help="find-and-replace secrets into a rendered copy of the project"
    )
    _add_common_args(render_parser)
    render_parser.set_defaults(func=_run_render)

    build_parser_ = subparsers.add_parser(
        "build", help="render secrets, then invoke the LaTeX engine on the result"
    )
    _add_common_args(build_parser_)
    build_parser_.add_argument("main_tex", help="path to the main .tex file, relative to --root")
    build_parser_.add_argument("--engine", help="LaTeX engine to invoke (default: pdflatex)")
    build_parser_.add_argument(
        "--engine-arg",
        action="append",
        help="extra argument to pass to the engine (repeatable)",
    )
    build_parser_.set_defaults(func=_run_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
