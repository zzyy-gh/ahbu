# AI-Assisted Heart-Brain Understanding

Autonomous project charter. The organizing philosophy is the Layered Endeavor Framework — read it before doing anything else:

https://raw.githubusercontent.com/zzyy-gh/alibrary/main/inbox/layered-endeavor-framework.md

This README adds only what's specific to this project; the framework covers the rest.

## Vision

Resolve real pain points in AI-assisted heart-brain understanding — the use of physiological signals (heart and brain) to infer body state, mental state, or intent.

This is a **portfolio**, not a single-shot project. Multiple pain points may be explored — sequentially or in parallel — and what is developed or learned on one (datasets, evaluation harnesses, baselines, calibration utilities, leakage diagnostics, modelling tricks) is expected to be reusable on others. Reuse is a first-class outcome, not a side-effect.

The portfolio is bounded by the quality bar, not by count. Better to carry one rigorously-validated pain point than five hand-wavy ones.

## Hard constraints (per pain point)

Three constraints, each enforced at the layer that can actually verify it. No "fix it later" within a layer's responsibility, but layers may cancel-back to the portfolio when their constraint fails — that is a normal outcome, not a failure of discipline.

- **Pain point must be real.** *Enforced at layer 10 (admission gate).* Validate that some constituency genuinely feels the pain. No invented problems, no future-work-section hypotheticals. Document the validation. If you can't validate, drop the candidate or escalate.
- **Solution must be feasible.** *Enforced at layer 20 (methodology).* Public data, OSS tooling, available compute, scoped time horizon. Layer 20 may cancel a track that turns out infeasible at our envelope — *not pre-judged at admission time*, because pre-judging filters out creative or novel framings before they get a real look.
- **Quality bar is non-negotiable.** *Enforced at layers 20 / 30 / 40.* Honest held-out testing, ablations where they matter, failure modes characterized, uncertainty reported. No metric gaming, no cherry-picking, no hand-waving.

A track exits the portfolio either by completing its analysis layer (`retire-completed`) or by being cancelled from a downstream layer with a documented reason (`retire-cancelled`). Both are valid; both produce lessons.

## Stance

- **Novelty welcome.** Creative, out-of-box, or unconventional framings are first-class. The admission gate does not pre-filter on "we don't know how to build this" — that is precisely what layer 20 explores.
- **Pilot vs headline.** Within a track, fast exploratory pilots inform methodology without pre-registration. Only the headline experiment is pre-registered and protocol-locked.
- **Cancel-back is healthy.** A clean cancel from layer 20 / 30 / 40 with documented reason is a portfolio update, not a project failure. Lessons captured either way.
- **Within-layer agile, cross-layer gated.** Each layer iterates fast internally; layer boundaries hold a critic-pass + human-checkpoint gate. Goal: maximise (new output − risk).

## Reuse principle

Anything produced for one pain point that could plausibly serve another gets surfaced as a shared artifact with its own small spec. Examples: a leakage-clean evaluation harness, a domain-shift diagnostic, a calibrated-abstention wrapper, a per-cohort stratifier, a baseline implementation. Tracks consume from the shared layer and contribute back to it. The shared layer earns its keep when at least two tracks use the same artifact — promote eagerly but not prematurely.

## Project operations

The framework leaves operations to the project. For this one:

- **Critic at help boundaries.** Before declaring a milestone complete, run a critic pass — a separate agent invocation or structured self-review — against the spec the layer received. Looks for spec drift, unjustified shortcuts, missing validation, premature claims.
- **Human checkpoint at the end of each meaningful complete chunk.** Self-assess; when the chunk is right, hand over for review. Escalate sooner only when a hard constraint conflicts with the vision, a discovered fact changes the project's premise, or the chunk as scoped cannot meet the quality bar.
- **Pain-point validation is a required artifact** for every portfolio admission.
- **Portfolio discipline.** A registry of candidate · admitted · deferred · retired pain points is maintained, with reasons. Admission requires critic-pass + human checkpoint.
- **Use git.** Commit as you go. Tag milestones. Branches encouraged for parallel track work.

## Start

Read the framework. Establish your resource picture. Validate candidate pain points (broad before deep). Admit one or more to the portfolio. For each admitted pain point, run methodology → experiments → analysis under the quality bar. Surface reusable artifacts as they emerge.

Implementation details (repo layout, agent personas, kickoff sequence, milestone tags) live in `CLAUDE.md`.
