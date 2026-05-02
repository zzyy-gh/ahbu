# Layer 10 — Pain-Point Validation

**Mandate.** Identify one real, validated pain point in AI-assisted heart-brain understanding that this project will resolve.

**Knowledge.** Domain literature, dataset issue trackers, practitioner forums (r/BCI, r/neuroscience, OpenBCI forum, Sleep-EDF / PhysioNet discussions), benchmark leaderboards, clinician/patient narratives where accessible.

**Output.**
- `candidates/<slug>.md` — one file per candidate pain point with the spec below.
- `validation-log.md` — chronological log of validation activities and evidence.
- `selection.md` — chosen pain point + justification + critic pass notes.

**Help target.** Layer 00 (Vision).

---

## Candidate spec (template)

Each candidate file must contain:

1. **Pain point statement** — one paragraph, plain language.
2. **Constituency** — who feels it. Concretely. Not "the field".
3. **Evidence of pain** — citations, quotes, links to issues / forum threads / paper limitation sections / clinician interviews / dataset README caveats. Multiple independent sources preferred.
4. **Counterfactual** — what does the world look like if it's resolved? Why does that matter to the constituency?
5. **Feasibility sketch** — public dataset(s) that bear on it, compute envelope, time horizon estimate, primary risks.
6. **Quality-bar implications** — how would honest evaluation work? What's the held-out partition? What ablations matter?
7. **Open questions** — what we don't yet know that could kill the candidate.

## Validation rubric

A candidate is *validated* when:

- ≥ 2 independent evidence sources for the pain (not the same paper restated).
- Constituency is named and reachable in principle (forum, paper authors, dataset maintainers).
- Feasibility passes initial check: dataset exists, compute fits, scope fits.
- Critic pass finds no fatal objection.

## Critic pass

A separate agent invocation (or structured self-review using the `critic` agent in `.claude/agents/`) reviews the selection against:

- Spec drift from vision.
- Pain invented vs. observed.
- Evidence cherry-picked vs. representative.
- Feasibility hand-waved.
- Premature anchoring on one candidate before exploring breadth.

Critic notes recorded in `selection.md`.
