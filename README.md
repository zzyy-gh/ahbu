# AI-Assisted Heart-Brain Understanding

Autonomous project charter. The organizing philosophy is the Layered Endeavor Framework — read it before doing anything else:

https://raw.githubusercontent.com/zzyy-gh/alibrary/main/inbox/layered-endeavor-framework.md

This README adds only what's specific to this project; the framework covers the rest.

## Vision

Resolve real pain points in AI-assisted heart-brain understanding — the use of physiological signals (heart and brain) to infer body state, mental state, or intent.

This is a **portfolio**, not a single-shot project. Multiple pain points may be explored — sequentially or in parallel — and what is developed or learned on one (datasets, evaluation harnesses, baselines, calibration utilities, leakage diagnostics, modelling tricks) is expected to be reusable on others. Reuse is a first-class outcome, not a side-effect.

The portfolio is bounded by the quality bar, not by count. Better to carry one rigorously-validated pain point than five hand-wavy ones.

## Hard constraints (per pain point)

Three constraints, no exceptions, no "we'll fix it later":

- **Pain point must be real.** Some constituency genuinely feels it; we have evidence. No invented problems, no future-work-section hypotheticals.
- **Solution must be feasible.** Public data, OSS tooling, available compute, scoped time horizon.
- **Quality bar is non-negotiable.** Honest held-out testing, ablations where they matter, failure modes characterized, uncertainty reported. No metric gaming, no cherry-picking, no hand-waving.

A pain point that fails any constraint exits the portfolio with a documented reason. Lessons captured regardless.

## Stance

- **Novelty welcome.** Creative, out-of-box, or unconventional framings are first-class outputs of this project, not deviations from it.
- **Honest exits.** Cancelling a pursuit cleanly when a constraint fails is a real outcome, not a project failure.
- **Efficiency over ceremony.** Maximise (new output − risk). Iterate fast where the cost of wrong is low; gate carefully where the cost of wrong is high.

## Reuse principle

Anything produced for one pain point that could plausibly serve another gets surfaced as a shared artifact with its own small spec. Examples: a leakage-clean evaluation harness, a domain-shift diagnostic, a calibrated-abstention wrapper, a per-cohort stratifier, a baseline implementation. The shared layer earns its keep when at least two pursuits use the same artifact — promote eagerly but not prematurely.

## Start

Read the framework. Validate candidate pain points (broad before deep). Admit those that meet the constraints. For each admitted pain point, do the work under the quality bar. Surface reusable artifacts as they emerge.

Implementation details — repo layout, layer-by-layer enforcement of constraints, cancel-back protocol, pilot-vs-headline mechanics, agent personas, kickoff sequence, milestone tags — live in `CLAUDE.md`.
