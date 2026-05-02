# Track layer 30 — Experiments / Implementation

**Mandate.** Execute the methodology for this track. Produce honest results.

**Knowledge.** Frozen protocol from this track's `20-methodology/protocol-lock.md`, code, compute environment, `shared/` substrate.

**Output.**
- `code/` — reproducible scripts / notebooks. Imports from `shared/` where applicable.
- `runs/` — run logs, metrics, configs. Large artifacts gitignored.
- `results.md` — primary metrics on held-out, ablations, uncertainty estimates, failure-mode characterization.

**Help target.** Track layer 20 (Methodology).

---

## Discipline (per project quality bar)

- Held-out partition touched **once** for the headline number. Earlier debugging uses dev split only.
- Every reported metric carries an uncertainty estimate (CI, std across seeds, or bootstrap).
- Ablations cover the design choices most likely to be load-bearing.
- Failure cases catalogued, not buried.

## Promotion to shared/

If a piece of `code/` proves reusable mid-track (plotting helpers, data loaders, calibration wrappers), promote to `shared/` with a small spec rather than copy-pasting between tracks. The track's `code/` then imports from `shared/`.
