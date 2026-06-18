# Keel

**Turn a short interview into a portable AI operating system.**

Keel productizes a pattern that sophisticated operators build by hand: a
structured, plain-text context layer that any AI tool can read so it works like
it already knows you. Keel interviews a person or a business and generates that
layer automatically, plus a one-paste bootstrap prompt for any AI chat.

This repository contains the **MVP prototype** and the **product strategy**.
See [`STRATEGY.md`](STRATEGY.md) for the full strategy; this README is the brief.

---

## The brief

- **Problem:** AI starts every session with amnesia. It does not know who you
  are, how you work, or what your business sells. Experts fix this with a
  hand-built file system. Most people and small businesses cannot.
- **Product:** an interview that generates a portable, owned, plain-text AI
  operating system, model-agnostic and ready to paste into any tool.
- **Who it is for:**
  1. Operators and power-users (RevOps, founders, consultants, analysts) who
     want depth, control, and portability.
  2. AI-friendly local businesses that want the outcome without the setup work.
- **Why it wins:** portable and owned (not vendor-locked memory), methodology
  baked into the interview (non-experts get expert-quality context), and it
  compounds (the more context you add, the stickier it gets).
- **Model:** open-core CLI (this prototype) plus Keel Cloud (sync, web
  onboarding, teams) plus Keel for Business (partner-delivered setup).

---

## Try the prototype

No dependencies. Python 3.8+.

Interactive interview:

```bash
cd keel
python -m keel init
```

Generate from a saved answers file (non-interactive, repeatable, partner-ready):

```bash
# An individual operator (reverse-engineered from the original Codex OS)
python -m keel init --from examples/austin.operator.json --out /tmp/austin-keel

# An AI-friendly local business
python -m keel init --from examples/local-business.json --out /tmp/dental-keel
```

Print the bootstrap prompt for an existing workspace:

```bash
python -m keel bootstrap --workspace /tmp/dental-keel
```

Add a project/area later:

```bash
python -m keel add-project "Events" --workspace /tmp/dental-keel
```

---

## What it generates

```
<workspace>/
  00_Global_Context/
    START_HERE.md            # how the system works
    WHO_I_AM_AND_HOW_I_WORK.md   (or WHO_WE_ARE.md for a business)
    OPERATING_PRINCIPLES.md  # the rules that govern decisions and tone
    OUTPUT_STANDARD.md       # what a finished deliverable must look like
    CONTEXT_INDEX.md         # a map of the workspace
    BOOTSTRAP_PROMPT.md      # one paste to load it into any AI
  <Project>/CHAT_SUMMARY.md  # durable per-project memory
  <Project>/NOTES.md
  skills/data-dump/SKILL.md  # a reusable procedure
  README.md
```

The output is plain markdown you own. Edit it, version it, move it between
tools. The more current you keep it, the better your AI output gets.

---

## Run the tests

```bash
cd keel
python -m unittest discover
```

---

## Project layout

```
keel/
  STRATEGY.md          # full product strategy
  README.md            # this brief
  keel/                # the CLI package
    cli.py             # commands: init, add-project, bootstrap
    interview.py       # the onboarding question sets (core IP)
    scaffold.py        # writes the workspace
    templates.py       # the generated markdown
  examples/            # sample answer files
  tests/               # unit tests
```
