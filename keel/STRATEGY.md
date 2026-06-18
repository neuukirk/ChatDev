# Keel — Product Strategy

Working title: **Keel** (the structural backbone of a ship; it keeps the vessel
steady and on course). Generalized from Austin Newkirk's personal "Codex OS."

Last updated: 2026-06-18

---

## Thesis (read this first)

The bottleneck for getting useful work out of AI is no longer model quality. It
is that AI starts every conversation with amnesia. It does not know who you are,
how you work, what your business sells, or what "good" looks like for you.

Sophisticated operators solve this by hand-building a structured, file-based
operating system that any AI tool can read at the start of a session. Most
people, and almost every small business, cannot build that themselves.

**Keel productizes the operating system.** It interviews a user or a business,
generates a portable, plain-text AI operating context they own, and gives them a
one-paste bootstrap prompt that makes any AI tool work like it already knows
them.

---

## The insight (where this comes from)

This product is reverse-engineered from a real, working artifact: Austin's
"Codex OS." It is a folder of markdown files that encodes:

- **Identity** — who he is and how he works
- **Operating principles** — the actual rules that govern his decisions
- **An output-delivery standard** — what a finished deliverable must look like
- **Per-project memory** — durable context for each active workstream
- **Skills** — small reusable procedures the AI can invoke
- **A bootstrap prompt** — one block of text that loads all of the above into a
  fresh AI chat

The result: any new AI session recovers full operating context from files
instead of being re-taught from scratch, and produces work in his voice, tied to
his goals, at his quality bar.

The pattern is generalizable. The methodology is the product. Most users will
never build this on their own, which is exactly the opportunity.

---

## The problem

1. **AI has no durable memory of you.** Vendor "memory" features are shallow,
   siloed per tool, and not portable. Switch from one assistant to another and
   you start over.
2. **Context is hard to author well.** Good context is structured, prioritized,
   and written in a way models can actually use. Non-experts produce vague,
   low-signal context and get vague, low-signal output.
3. **Quality is inconsistent.** Without a defined output standard, AI output
   varies wildly and almost always needs heavy rework.
4. **Small businesses are locked out.** They are increasingly "AI friendly" and
   want the leverage, but they lack the time and sophistication to set AI up so
   it actually understands their business.

---

## The product

Keel turns a short interview into a complete, portable AI operating system.

**What the user gets:**

- A generated workspace of plain-text files (identity, principles, output
  standard, project memory, skills, an index).
- A **bootstrap prompt**: one paste that loads the whole context into Claude,
  ChatGPT/Codex, or any chat model.
- Files they fully own and can version, edit, and move between tools.
- A repeatable structure that grows with them, so context compounds instead of
  decaying.

**Two modes, one engine:**

- **Operator mode** — for an individual professional (RevOps, ops, founders,
  consultants, analysts). Captures how *you* work and think.
- **Business mode** — for a local business. Captures who the business is, its
  voice, its offers, its customers, and its standard operating procedures, so
  any AI the staff touches sounds like the business and knows its details.

---

## Who it is for

### Segment 1: Operators and power-users (depth-led)

RevOps, partner/alliance ops, founders, consultants, and analysts who already
use AI daily and want control, portability, and depth. They value owning their
context as files and using it across tools. They are early adopters and the
credibility/distribution engine.

- **Job to be done:** "Make every AI tool I touch work like it already knows how
  I operate, without me re-explaining myself each session."

### Segment 2: AI-friendly local businesses (service-led)

Local businesses (clinics, agencies, trades, retail, professional services) that
are open to AI but lack the sophistication to set it up. They will not write
their own context files. They want the outcome, delivered.

- **Job to be done:** "Make AI actually know my business so my team gets
  on-brand, accurate output without becoming prompt engineers."
- **Reach them through done-with-you onboarding**, not a blank CLI.

---

## How it works (user flow)

1. **Interview.** Keel asks a focused set of questions (adapted to operator vs
   business). It is designed so non-experts give high-signal answers.
2. **Generate.** Keel writes the workspace: global context, output standard,
   project/area memory, a sample skill, and an index.
3. **Bootstrap.** Keel prints a paste-ready prompt that loads the context into
   any AI chat.
4. **Use and grow.** As work happens, summaries and new context get appended,
   so the system gets sharper over time.

---

## Why now

- AI adoption is mainstream, but "make it sound like us / know us" is unsolved
  for non-experts.
- Plain-text, model-agnostic context is the durable layer as models churn.
- Small businesses are actively looking for practical AI help and will pay for a
  done-for-them setup.

---

## Differentiation and moat

- **Portable and owned.** Plain files the user controls, not vendor-locked
  memory. Model-agnostic by design.
- **Methodology, not just a folder.** The interview encodes operator best
  practices (signal over noise, output standards, AI_Draft to Human_Final), so
  non-experts get expert-quality context.
- **Compounding switching cost.** The more a user's context grows, the more
  valuable and sticky it becomes.
- **Two-sided template library.** Operator and business templates seed a
  community library; shared skills and templates strengthen the network.

---

## Business model

Open core plus services.

- **Free / OSS CLI** (this prototype): generate and own your workspace locally.
  Drives adoption and credibility with operators.
- **Keel Cloud (subscription):** web onboarding, hosted sync across devices,
  team sharing, integrations (Drive, Notion, Slack, CRM), and update reminders.
  - Solo: low monthly. Team: per-seat.
- **Keel for Business (service + subscription):** done-with-you onboarding for
  local businesses, delivered by Keel or certified partners (agencies,
  consultants), plus an ongoing subscription to keep context current.
- **Partner program:** local agencies and consultants resell setup and earn
  recurring revenue, which is the scalable channel into Segment 2.

---

## Go-to-market

- **Operators (Segment 1):** open-source led. Ship the CLI, write in public,
  seed in RevOps/AI-ops/founder communities. Land power-users who become
  advocates and template contributors.
- **Local businesses (Segment 2):** service-led through partners. Recruit local
  agencies and consultants to deliver onboarding using Keel. They get a
  productized offer; Keel gets distribution it cannot build alone.

---

## Risks and watch-outs

- **Vendor memory improves.** Counter with portability, cross-tool support, and
  methodology depth that single-vendor memory will not match.
- **Interview quality is the product.** If the questions are weak, output is
  weak. Invest disproportionately here; treat the question sets as core IP.
- **Local-business setup does not self-serve.** Accept this; route Segment 2
  through done-with-you partners rather than forcing self-serve.
- **Privacy.** Context is sensitive. Default to local files the user owns; make
  any cloud sync explicit and encrypted.

---

## Roadmap

- **Phase 1 (MVP, this prototype):** CLI that runs the interview and generates a
  complete, portable workspace plus a bootstrap prompt. Operator and business
  modes. Non-interactive mode (from an answers file) for repeatability and
  partner-delivered setups.
- **Phase 2:** Web onboarding wizard, template library, `keel update` to refresh
  context, richer skills.
- **Phase 3:** Keel Cloud (sync, team sharing, integrations) and the partner
  program for local-business delivery.

---

## What the MVP proves

The MVP (the prototype shipped alongside this doc) validates the core bet: that
a short, well-designed interview can generate an expert-quality, portable AI
operating system for someone who could not have built it themselves. Everything
else (cloud, partners, library) is distribution on top of that engine.
