# Layer 30 — Experiments / Implementation

**Mandate.** Execute the methodology. Produce honest results.

**Knowledge.** Frozen protocol from layer 20, code, compute environment.

**Output.**
- `code/` — reproducible scripts / notebooks.
- `runs/` — run logs, metrics, configs (versioned; large artifacts gitignored).
- `results.md` — primary metrics on held-out, ablations, uncertainty estimates, failure-mode characterization.

**Help target.** Layer 20 (Methodology).

---

Empty until methodology locks.

## Discipline

- Held-out partition touched **once** for the headline number. Earlier debugging uses dev split only.
- Every reported metric carries an uncertainty estimate (CI, std across seeds, or bootstrap).
- Ablations cover the design choices most likely to be load-bearing.
- Failure cases catalogued, not buried.
