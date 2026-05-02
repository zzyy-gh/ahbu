# AI-Assisted Heart-Brain Understanding

Autonomous project charter. Organising philosophy: the Layered Endeavor Framework — read it before doing anything else.

https://raw.githubusercontent.com/zzyy-gh/alibrary/main/inbox/layered-endeavor-framework.md

This README adds only what's specific to this project; the framework covers the rest. Implementation details (layer routing, cancel-back protocol, pilot/headline mechanics, agent personas, kickoff sequence, milestone tags) live in `CLAUDE.md`.

## Vision

Resolve real pain points in AI-assisted heart-brain understanding — the use of physiological signals (heart and brain) to infer body state, mental state, or intent.

This is a **portfolio**, not a single-shot project. Multiple pain points may be explored — sequentially or in parallel — and what is developed or learned on one is expected to be reusable on others. Reuse is a first-class outcome, not a side-effect.

## Hard constraints (per pain point)

Three constraints, no exceptions, no "we'll fix it later":

- **Pain point must be real.** Some constituency genuinely feels it; we have evidence.
- **Solution must be feasible.** Public data, OSS tooling, available compute, scoped time horizon.
- **Quality bar is non-negotiable.** Honest held-out testing, ablations where they matter, failure modes characterized, uncertainty reported. No metric gaming, no cherry-picking, no hand-waving.

A pain point that fails any constraint exits the portfolio with a documented reason. Lessons captured regardless.

## Stance

- **Novelty welcome.** Creative, out-of-box, or unconventional framings are first-class outputs of this project, not deviations from it.
- **Honest exits.** Cancelling a pursuit cleanly when a constraint fails is a real outcome, not a project failure.
- **Efficiency over ceremony.** Maximise (new output − risk). Iterate fast where the cost of wrong is low; gate carefully where the cost of wrong is high.

## Repo preview

```
00-vision/        ← why we exist, hard constraints (root layer)
10-pain-point/    ← discover + validate pain (one folder per candidate)
20-plan/          ← pain → technical: design + interpret (one folder per admitted track)
30-implement/     ← code + data + runs + shared substrate + compute + datasets
bin/              ← repo tooling (transcript sync, hooks)
transcripts/      ← raw sub-agent JSONL transcripts (auto-synced pre-commit)
CLAUDE.md         ← agent operating notes
```

Each layer has its own `shared/` subfolder for layer-scoped substrate (registry, reuse sketches, code library). A pain point exists as a folder inside whichever layers it has reached: candidates start in `10-pain-point/<slug>/`; admitted tracks add `20-plan/<slug>/`; running tracks add `30-implement/<slug>/`.

## Reuse principle

Anything produced for one pain point that could plausibly serve another gets surfaced as a shared artifact with its own small spec. The shared folder of a layer earns its keep when at least two pursuits use the same artifact — promote eagerly but not prematurely.

## Start

Read the framework. Validate candidate pain points (broad before deep). Admit those that meet the real-pain bar. For each admitted pain point, plan in layer 20, execute in layer 30, interpret back in layer 20. Surface reusable artifacts as they emerge.
