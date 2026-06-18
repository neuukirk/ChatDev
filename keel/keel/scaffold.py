"""Turn collected answers into a written Keel workspace on disk."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from . import templates


def _projects(answers: Dict[str, str]) -> List[str]:
    raw = answers.get("projects", "")
    items = templates._as_list(raw)
    # Keep names filesystem-friendly but readable.
    cleaned = []
    for item in items:
        name = item.strip().strip("/").replace("/", "-")
        if name:
            cleaned.append(name)
    return cleaned


def build_files(answers: Dict[str, str]) -> List[Tuple[str, str]]:
    """Return a list of (relative_path, content) for the whole workspace."""
    projects = _projects(answers)
    gc = "00_Global_Context"
    files: List[Tuple[str, str]] = [
        (os.path.join(gc, "START_HERE.md"), templates.start_here(answers)),
        (os.path.join(gc, templates.identity_filename(answers)), templates.identity(answers)),
        (os.path.join(gc, "OPERATING_PRINCIPLES.md"), templates.operating_principles(answers)),
        (os.path.join(gc, "OUTPUT_STANDARD.md"), templates.output_standard(answers)),
        (os.path.join(gc, "CONTEXT_INDEX.md"), templates.context_index(answers, projects)),
        (os.path.join(gc, "BOOTSTRAP_PROMPT.md"), templates.bootstrap_prompt(answers, projects)),
        (os.path.join("skills", "data-dump", "SKILL.md"), templates.data_dump_skill()),
        ("README.md", templates.workspace_readme(answers)),
    ]
    for project in projects:
        files.append((os.path.join(project, "CHAT_SUMMARY.md"), templates.project_summary(project, answers)))
        files.append((os.path.join(project, "NOTES.md"), templates.project_notes(project, answers)))
    return files


def write_workspace(answers: Dict[str, str], out_dir: str, force: bool = False) -> List[str]:
    """Write the workspace under ``out_dir``. Returns the list of written paths."""
    files = build_files(answers)
    written: List[str] = []
    for rel_path, content in files:
        dest = os.path.join(out_dir, rel_path)
        if os.path.exists(dest) and not force:
            raise FileExistsError(
                f"{dest} already exists. Use force=True (or --force) to overwrite."
            )
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as handle:
            handle.write(content)
        written.append(dest)
    return written


def add_project(answers: Dict[str, str], out_dir: str, project: str, force: bool = False) -> List[str]:
    """Scaffold a single new project/area folder inside an existing workspace."""
    name = project.strip().strip("/").replace("/", "-")
    if not name:
        raise ValueError("Project name is empty.")
    targets = [
        (os.path.join(name, "CHAT_SUMMARY.md"), templates.project_summary(name, answers)),
        (os.path.join(name, "NOTES.md"), templates.project_notes(name, answers)),
    ]
    written: List[str] = []
    for rel_path, content in targets:
        dest = os.path.join(out_dir, rel_path)
        if os.path.exists(dest) and not force:
            raise FileExistsError(f"{dest} already exists. Use --force to overwrite.")
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "w", encoding="utf-8") as handle:
            handle.write(content)
        written.append(dest)
    return written
