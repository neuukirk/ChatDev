"""Markdown templates for a generated Keel workspace.

Each renderer takes the collected ``answers`` dict and returns the file body.
Templates are intentionally plain text and model-agnostic. Generated copy avoids
em dashes, in keeping with the operating-standard this product is built on.
"""

from __future__ import annotations

import datetime
from typing import Dict, List


def _today() -> str:
    return datetime.date.today().isoformat()


def _as_list(value: str) -> List[str]:
    """Split a free-text answer into clean bullet items.

    Prefers newlines and semicolons as separators so that commas inside a
    clause are preserved. Only falls back to splitting on commas when no
    newline or semicolon is present.
    """
    if not value:
        return []
    if "\n" in value or ";" in value:
        raw = value.replace("\n", ";")
        sep = ";"
    else:
        raw = value
        sep = ","
    return [item.strip() for item in raw.split(sep) if item.strip()]


def _bullets(value: str, fallback: str = "") -> str:
    items = _as_list(value)
    if not items and fallback:
        items = [fallback]
    return "\n".join("- " + item for item in items) if items else "- (add detail here)"


def _is_business(answers: Dict[str, str]) -> bool:
    return answers.get("profile", "operator").lower().startswith("b")


def subject_name(answers: Dict[str, str]) -> str:
    return answers.get("name", "").strip() or (
        "This business" if _is_business(answers) else "This operator"
    )


def identity_filename(answers: Dict[str, str]) -> str:
    return "WHO_WE_ARE.md" if _is_business(answers) else "WHO_I_AM_AND_HOW_I_WORK.md"


# --------------------------------------------------------------------------- #
# Renderers
# --------------------------------------------------------------------------- #

def start_here(answers: Dict[str, str]) -> str:
    name = subject_name(answers)
    kind = "business" if _is_business(answers) else "operator"
    return f"""# START HERE - Keel Operating System

Last updated: {_today()}

This folder is the portable AI operating system for {name}.
It exists so any AI tool can recover full operating context from files instead
of being re-taught from scratch every session.

## How to use this

A new AI chat should:
1. Read the global context files in `00_Global_Context/`
2. Read the relevant project/area folder
3. Then proceed with the work

The fastest way to load it: paste the contents of
`00_Global_Context/BOOTSTRAP_PROMPT.md` into a new chat, then attach or paste
the files it references.

## What is here

- `{identity_filename(answers)}` - who this {kind} is and how it works
- `OPERATING_PRINCIPLES.md` - the rules that govern decisions and tone
- `OUTPUT_STANDARD.md` - what a finished deliverable must look like
- `CONTEXT_INDEX.md` - a map of everything in this workspace
- `BOOTSTRAP_PROMPT.md` - one paste to load this context into any AI

## Global working rules

- Treat folders as retrievable memory, not automatic memory
- Read anchor docs before making assumptions
- Distinguish durable facts from active hypotheses
- Tie recommendations back to goals where possible
- Prefer signal and clear next actions over data exhaust
- If durable new context emerges, update the relevant anchor doc
"""


def identity(answers: Dict[str, str]) -> str:
    name = subject_name(answers)
    if _is_business(answers):
        return f"""# Who We Are

Last updated: {_today()}

## Business
- Name: {answers.get('name', '(business name)')}
- Industry: {answers.get('industry', '(industry)')}
- Location: {answers.get('location', '(location)')}

## What we do
{answers.get('summary', '(one-line description of the business)')}

## What we offer
{_bullets(answers.get('offers', ''), 'Describe each product or service')}

## Who we serve
{_bullets(answers.get('customers', ''), 'Describe the customers and what they need')}

## Our voice
{_bullets(answers.get('voice', ''), 'How the business should sound, and what to avoid')}

## Tools and systems we use
{_bullets(answers.get('tools', ''), 'List the tools the business runs on')}

## Current goals
{_bullets(answers.get('goals', ''), 'What the business is trying to achieve now')}
"""
    return f"""# Who I Am and How I Work

Last updated: {_today()}

## Identity
- Name: {answers.get('name', '(name)')}
- Role: {answers.get('role', '(title and company)')}

## What I do
{answers.get('summary', '(one-line description of what you actually do)')}

## How I work
{_bullets(answers.get('how_you_work', ''), 'Describe your working preferences')}

## Tools and systems I use
{_bullets(answers.get('tools', ''), 'List the tools you run on')}

## Current goals
{_bullets(answers.get('goals', ''), 'What you are trying to achieve now')}
"""


def operating_principles(answers: Dict[str, str]) -> str:
    name = subject_name(answers)
    principles = _as_list(answers.get("principles", ""))
    if not principles:
        principles = [
            "Build repeatable systems over reactive fixes",
            "Reduce noise and increase signal",
            "Frame the decision, not just the data",
            "Keep human judgment in the loop where quality matters",
        ]
    numbered = "\n".join(
        f"**{i}. {p}**\n" for i, p in enumerate(principles, start=1)
    )
    return f"""# Operating Principles

Last updated: {_today()}

These are the principles that govern how {name} works. Use them to calibrate
tone, framing, and decision logic when generating any output.

## Core principles

{numbered}
## Applied to AI use

- AI output is draft material, not a finished deliverable.
- Review and refine with real context before anything reaches an audience.
- The test for any output: would {name} be comfortable sending it as written?
"""


def output_standard(answers: Dict[str, str]) -> str:
    name = subject_name(answers)
    custom = answers.get("output_standard", "").strip()
    custom_block = (
        f"\n## What {name} expects in a finished deliverable\n\n"
        f"{_bullets(custom)}\n"
        if custom
        else ""
    )
    return f"""# Output Standard

Purpose: standardize how AI delivers results for {name} so quality is
consistent and every output is ready to use.

## Default structure (use when it fits)

1. **Headline (1 sentence)** - the single most important takeaway, in plain language.
2. **What changed** - the clearest signal, in 1 to 3 bullets.
3. **So what** - why it matters, tied to a goal where relevant.
4. **Recommended action** - what should happen next, by whom, and when.
5. **Evidence / source** - where the information came from.

## Quality gates

- Lead with the headline. No setup, no warm-up.
- One idea per bullet.
- End with a clear next step.
- Do not dump raw data without interpretation.
- Use plain punctuation. Avoid decorative punctuation and em dashes.
{custom_block}"""


def context_index(answers: Dict[str, str], projects: List[str]) -> str:
    project_lines = "\n".join(
        f"- {p}: `{p}/CHAT_SUMMARY.md`" for p in projects
    ) or "- (no projects yet; add one with `keel add-project`)"
    return f"""# Context Index

A map of this workspace.

## Global context
- `00_Global_Context/{identity_filename(answers)}`
- `00_Global_Context/OPERATING_PRINCIPLES.md`
- `00_Global_Context/OUTPUT_STANDARD.md`

## Projects / areas
{project_lines}

## Skills
- `skills/data-dump/SKILL.md` - append a dated context packet to a project summary.
  Trigger: "pull the context from this chat" or "append a chat summary."
"""


def bootstrap_prompt(answers: Dict[str, str], projects: List[str]) -> str:
    name = subject_name(answers)
    idf = identity_filename(answers)
    project_hint = (
        f"The active projects/areas are: {', '.join(projects)}.\n"
        if projects
        else ""
    )
    return f"""# Bootstrap Prompt

Paste the block below into a new AI chat (Claude, ChatGPT, Codex, or any model)
to load this operating system. Then paste or attach the files it names.

---

You are working as the AI operating layer for {name}.

Before answering substantive requests, read these global context files:

1. `00_Global_Context/{idf}`
2. `00_Global_Context/OPERATING_PRINCIPLES.md`
3. `00_Global_Context/OUTPUT_STANDARD.md`
4. `00_Global_Context/CONTEXT_INDEX.md`

Then read the local context for the project or area you are working in.
{project_hint}
Working rules:
- Do not assume prior chat memory. Recover context from the files first.
- Match the identity, principles, and output standard in those files.
- Distinguish durable facts from current hypotheses.
- Tie recommendations back to the stated goals when relevant.
- Treat AI output as a draft that needs review before it reaches an audience.

When you begin, briefly confirm:
1. which context files you used
2. any key assumptions you had to make

---
"""


def project_summary(project: str, answers: Dict[str, str]) -> str:
    return f"""# {project} - Chat Summary

This file is durable memory for the "{project}" project/area.
Append a dated packet each time meaningful context emerges, newest first.

## {_today()}
- (Add the first context packet here: what this project is, current status,
  open questions, and the next action.)
"""


def project_notes(project: str, answers: Dict[str, str]) -> str:
    return f"""# {project} - Working Notes

Scratch space for "{project}". Promote durable items into CHAT_SUMMARY.md.
"""


def data_dump_skill() -> str:
    return """# Skill: data-dump

## Purpose
Append a dated context packet to a project's CHAT_SUMMARY.md so durable context
is not lost between sessions.

## Trigger
"pull the context from this chat" or "append a chat summary"

## Steps
1. Identify the active project/area folder.
2. Summarize the session into: status, key decisions, open questions, next action.
3. Prepend a dated entry (newest first) to that project's CHAT_SUMMARY.md.
4. Keep it tight. One idea per bullet. Lead with what changed.
"""


def workspace_readme(answers: Dict[str, str]) -> str:
    name = subject_name(answers)
    return f"""# Keel Workspace for {name}

This is a portable AI operating system generated by Keel.

Start with `00_Global_Context/START_HERE.md`.
To load it into any AI tool, paste `00_Global_Context/BOOTSTRAP_PROMPT.md`.

These are your files. Edit them, version them, and move them between tools
freely. The more you keep them current, the better your AI output gets.
"""
