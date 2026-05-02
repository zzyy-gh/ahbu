# Layer 10 — Pain-Point Validation & Portfolio Management

**Mandate.** Maintain the project's portfolio of pain points: validate candidates, admit those that pass the hard constraints, defer those that don't, retire those that are completed. Never admit on caveats.

**Knowledge.** Domain literature, dataset issue trackers, practitioner forums (r/BCI, r/neuroscience, OpenBCI forum, Sleep-EDF / PhysioNet discussions), benchmark leaderboards, clinician/patient narratives, and the project's accumulated learnings from earlier admitted tracks.

**Outputs.**
- `candidates/<slug>.md` — one file per investigated candidate (admitted or not).
- `validation-log.md` — chronological log of validation activities.
- `portfolio.md` — registry: candidate · admitted · deferred · retired, with reasons and dates.
- `admission/<slug>.md` — admission record per admitted track: critic-pass notes + human-checkpoint approval. Triggers track instantiation in `tracks/<slug>/`.

**Help target.** Layer 00 (Vision).

---

## Candidate spec (template)

Each candidate file must contain:

1. **Pain point statement** — one paragraph, plain language.
2. **Constituency** — who feels it. Concretely. Not "the field".
3. **Evidence of pain** — citations, quotes, links. Multiple independent sources.
4. **Counterfactual** — what does the world look like if it's resolved? Why does that matter to the constituency?
5. **Feasibility sketch** — public dataset(s), compute envelope, time horizon, primary risks.
6. **Quality-bar implications** — how would honest evaluation work? Held-out partition? Ablations?
7. **Open questions** — what could kill the candidate.
8. **Reuse expectations** — what artifacts produced for this track plausibly serve other tracks (eval harness, calibration utility, dataset loader, baseline). Promote candidates that contribute to `shared/` over candidates that are isolated.

## Validation rubric (admission gate)

A candidate is admitted to the portfolio when:

- ≥ 2 independent evidence sources for the pain (not the same paper restated).
- Constituency named **and reachable in principle** — verified, not asserted (forum, paper authors, dataset maintainers, or at least one outreach attempt logged).
- Feasibility passes initial check: dataset exists, compute fits, scope fits.
- Quality-bar plan is concrete: held-out partition, primary metric, ablations, uncertainty protocol.
- Critic pass returns `pass` or `pass-with-fixes` (with fixes applied), not `block`.
- Human checkpoint approves admission.

## Portfolio operations

- **Sequencing.** Tracks may run in parallel when their compute / time / data demands don't collide, or sequential when one's output is upstream of another's. Default to sequential first track to establish substrate; subsequent tracks can run parallel once `shared/` is meaningful.
- **Defer, don't downgrade.** If a candidate fails any hard constraint, mark deferred with reason and conditions for re-evaluation. Do not admit "with caveats".
- **Retire on completion.** A track moves to retired when its analysis layer is signed off. Lessons learned go to `shared/` or to a per-track `lessons.md`.
- **Cross-track reuse.** Before a new track designs methodology, it surveys `shared/` for components that already address parts of its plan. The methodologist agent is responsible for this scan.

## Critic pass

A separate agent invocation reviews each admission against the candidate spec, the hard constraints, and any reuse expectations. Critic notes recorded in `admission/<slug>.md`.
