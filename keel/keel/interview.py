"""The Keel onboarding interview.

The interview is the core of the product: it lets a non-expert produce
high-signal context. Question sets are treated as primary IP and are kept
declarative so they are easy to tune and to localize.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


class Question:
    def __init__(self, key: str, prompt: str, help_text: str = "", default: str = ""):
        self.key = key
        self.prompt = prompt
        self.help_text = help_text
        self.default = default


# Shared closing questions, asked in both modes.
_COMMON_TAIL: List[Question] = [
    Question(
        "principles",
        "What rules or values actually govern how you make decisions?",
        "Separate items with semicolons. Think about what you always do or never do.",
    ),
    Question(
        "output_standard",
        "What does a finished, ready-to-use deliverable look like for you?",
        "Optional. Press Enter to use the sensible default standard.",
    ),
    Question(
        "goals",
        "What are your current goals or priorities?",
        "Separate items with semicolons.",
    ),
    Question(
        "tools",
        "What tools and systems do you run on?",
        "Separate items with commas.",
    ),
    Question(
        "projects",
        "Name the projects or areas you want context folders for.",
        "Separate with commas. Example: Marketing, Sales, Front Desk.",
    ),
]

OPERATOR_QUESTIONS: List[Question] = [
    Question("name", "What is your name?"),
    Question("role", "What is your title and company?"),
    Question(
        "summary",
        "In one line, what do you actually do?",
        "The real shape of the job, not the job title.",
    ),
    Question(
        "how_you_work",
        "How do you like to work? Preferences, style, what you avoid.",
        "Separate items with semicolons.",
    ),
] + _COMMON_TAIL

BUSINESS_QUESTIONS: List[Question] = [
    Question("name", "What is the business name?"),
    Question("industry", "What industry or category is it in?"),
    Question("location", "Where is it located?"),
    Question(
        "summary",
        "In one line, what does the business do?",
    ),
    Question(
        "offers",
        "What does the business sell or offer?",
        "Separate items with semicolons.",
    ),
    Question(
        "customers",
        "Who are your customers and what do they need?",
        "Separate items with semicolons.",
    ),
    Question(
        "voice",
        "How should the business sound? Tone, and anything to avoid.",
        "Example: warm and plain-spoken; never pushy; no jargon.",
    ),
] + _COMMON_TAIL


def questions_for(profile: str) -> List[Question]:
    return BUSINESS_QUESTIONS if profile.lower().startswith("b") else OPERATOR_QUESTIONS


def run_interview(
    profile: str,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    preset: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Collect answers for the given profile.

    ``preset`` answers are used as defaults and to skip prompts in
    non-interactive runs. ``input_fn``/``output_fn`` are injectable for testing.
    """
    preset = preset or {}
    answers: Dict[str, str] = {"profile": "business" if profile.lower().startswith("b") else "operator"}
    for q in questions_for(profile):
        if q.key in preset:
            answers[q.key] = preset[q.key]
            continue
        output_fn("")
        output_fn(q.prompt)
        if q.help_text:
            output_fn("  (" + q.help_text + ")")
        response = input_fn("> ").strip()
        answers[q.key] = response or q.default
    return answers
