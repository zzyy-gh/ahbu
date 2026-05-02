# AI-Assisted Heart-Brain Understanding

Autonomous project charter. The organizing philosophy is the Layered Endeavor Framework — read it before doing anything else:

https://raw.githubusercontent.com/zzyy-gh/alibrary/main/inbox/layered-endeavor-framework.md

This README adds only what's specific to this project; the framework covers the rest.

## Vision

Resolve real pain points in AI-assisted heart-brain understanding — the use of physiological signals (heart and brain) to infer body state, mental state, or intent.

## Hard constraints

- **Pain point must be real.** Validate that some constituency (researchers, clinicians, BCI users, wearable developers, end users, model developers, and so on) actually feels the pain. Explore broadly before anchoring on one. No invented problems, no future-work-section hypotheticals. Document the validation. If you can't validate, search for another or escalate.
- **Solution must be feasible.** Public data only, open-source tooling, compute you have access to, time horizon scoped at the start. If a candidate solution requires resources you don't have, it's out of scope.
- **Quality bar is non-negotiable.** Honest held-out testing, ablations where they matter, failure modes characterized, uncertainty reported. No metric gaming, no cherry-picking, no hand-waving.

## Project operations

The framework leaves operations to the project. For this one:

- **Critic at help boundaries.** Before declaring a milestone complete, run a critic pass — a separate agent invocation or a structured self-review — against the spec the layer received. The critic looks for spec drift, unjustified shortcuts, missing validation, premature claims.
- **Human checkpoint at the end of each meaningful complete chunk.** Self-assess; when the chunk is right, hand over for review. Smaller checkpoints are not required. Escalate sooner only when a hard constraint conflicts with the vision, a discovered fact changes the project's premise, or you assess that the project as scoped cannot meet the quality bar.
- **Pain-point validation is a required artifact** on top of what the framework already requires.
- **Use git.** Commit as you go. Tag milestones. Branches encouraged for parallel exploration.

## Start

Read the framework. Establish your resource picture (compute, datasets, time). Validate one or more candidate pain points. Pick one. Design your layer structure. Begin.
