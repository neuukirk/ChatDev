"""Keel command-line interface.

Commands:
  keel init           Run the interview and generate a workspace.
  keel add-project    Add a project/area folder to an existing workspace.
  keel bootstrap      Print the bootstrap prompt for a workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict

from . import __version__, interview, scaffold


def _load_answers_file(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Answers file must be a JSON object of key/value strings.")
    return {str(k): ("" if v is None else str(v)) for k, v in data.items()}


def _default_out_dir(answers: Dict[str, str]) -> str:
    name = (answers.get("name") or "keel").strip().lower()
    slug = "".join(c if c.isalnum() else "-" for c in name).strip("-") or "keel"
    return f"{slug}-keel-workspace"


def cmd_init(args: argparse.Namespace) -> int:
    preset: Dict[str, str] = {}
    if args.from_file:
        preset = _load_answers_file(args.from_file)

    profile = args.profile or preset.get("profile")
    interactive = not args.yes and not args.from_file

    if not profile:
        if interactive:
            print("Is this for an individual operator or a business?")
            answer = input("Type 'operator' or 'business' > ").strip().lower()
            profile = "business" if answer.startswith("b") else "operator"
        else:
            profile = "operator"

    if interactive:
        print("\nKeel will ask a few questions and generate your AI operating system.")
        print("Answer in plain language. Press Enter to skip an optional question.\n")
        answers = interview.run_interview(profile, preset=preset)
    else:
        # Non-interactive: rely entirely on the preset, filling profile.
        answers = dict(preset)
        answers["profile"] = "business" if profile.lower().startswith("b") else "operator"

    out_dir = args.out or _default_out_dir(answers)

    try:
        written = scaffold.write_workspace(answers, out_dir, force=args.force)
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"\nGenerated {len(written)} files in: {out_dir}")
    print(f"Start here:     {os.path.join(out_dir, '00_Global_Context', 'START_HERE.md')}")
    print(f"Bootstrap with: {os.path.join(out_dir, '00_Global_Context', 'BOOTSTRAP_PROMPT.md')}")
    print("\nPaste the bootstrap prompt into any AI chat to load your context.")
    return 0


def cmd_add_project(args: argparse.Namespace) -> int:
    try:
        written = scaffold.add_project({}, args.workspace, args.name, force=args.force)
    except (FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Added project '{args.name}':")
    for path in written:
        print(f"  {path}")
    return 0


def cmd_bootstrap(args: argparse.Namespace) -> int:
    path = os.path.join(args.workspace, "00_Global_Context", "BOOTSTRAP_PROMPT.md")
    if not os.path.exists(path):
        print(f"Error: no bootstrap prompt found at {path}", file=sys.stderr)
        return 1
    with open(path, "r", encoding="utf-8") as handle:
        sys.stdout.write(handle.read())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="keel",
        description="Generate a portable AI operating system from a short interview.",
    )
    parser.add_argument("--version", action="version", version=f"keel {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Run the interview and generate a workspace.")
    p_init.add_argument("--profile", choices=["operator", "business"], help="Skip the profile question.")
    p_init.add_argument("--out", help="Output directory for the workspace.")
    p_init.add_argument("--from", dest="from_file", help="Path to a JSON answers file (non-interactive).")
    p_init.add_argument("--yes", action="store_true", help="Non-interactive; use defaults/preset only.")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files.")
    p_init.set_defaults(func=cmd_init)

    p_add = sub.add_parser("add-project", help="Add a project/area folder.")
    p_add.add_argument("name", help="Project or area name.")
    p_add.add_argument("--workspace", default=".", help="Workspace directory (default: current).")
    p_add.add_argument("--force", action="store_true", help="Overwrite existing files.")
    p_add.set_defaults(func=cmd_add_project)

    p_boot = sub.add_parser("bootstrap", help="Print a workspace's bootstrap prompt.")
    p_boot.add_argument("--workspace", default=".", help="Workspace directory (default: current).")
    p_boot.set_defaults(func=cmd_bootstrap)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
