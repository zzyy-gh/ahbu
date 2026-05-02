# Track layer 30 — Experiments / Implementation

**Mandate.** Execute the methodology for this track. Produce honest results. **May cancel-back to layer 20** if the locked protocol proves infeasible to execute as written (data turns out inaccessible, compute turns out insufficient at run-time, dependency unavailable) — re-design rather than paper over. May cancel-back to layer 10 (retire-cancelled) if no re-design recovers feasibility.

**Knowledge.** Frozen protocol from this track's `20-methodology/protocol-lock.md`, code, compute environment, `shared/` substrate.

**Output.**
- `code/` — reproducible scripts / notebooks. Imports from `shared/` where applicable.
- `runs/` — run logs, metrics, configs. Large artifacts gitignored.
- `results.md` — primary metrics on held-out, ablations, uncertainty estimates, failure-mode characterization.

**Help target.** Track layer 20 (Methodology).

---

## Discipline (per project quality bar — applies to the headline only)

- Held-out partition touched **once** for the headline number. Earlier debugging + pilots use dev split only.
- Every reported headline metric carries an uncertainty estimate (CI, std across seeds, or bootstrap).
- Ablations cover the design choices most likely to be load-bearing.
- Failure cases catalogued, not buried.

## Pilots vs headline

Pilots from `20-methodology/pilots/` may be re-run here at scale to inform design tweaks pre-protocol-lock. Once `protocol-lock.md` exists, only the locked headline runs against the held-out partition. Anything else stays on dev split.

## Promotion to shared/

If a piece of `code/` proves reusable mid-track (plotting helpers, data loaders, calibration wrappers), promote to `shared/` with a small spec rather than copy-pasting between tracks. The track's `code/` then imports from `shared/`.
