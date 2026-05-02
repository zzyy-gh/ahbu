# Track: cross-subject-eeg

- **Slug:** `cross-subject-eeg`
- **Admitted:** 2026-05-02 (rubric v2)
- **Admission record:** `layers/10-pain-point-validation/admission/cross-subject-eeg.md`
- **Status:** layer 20 (methodology) — pending start

## Pain summary

EEG-based decoders generalize poorly across subjects. ~15–30 % of users are "BCI illiterate" at the standard calibration budget; the rest pay a 20–30-min per-session calibration tax. Foundation-model claims that this gap has narrowed are not convincingly supported by independent evaluation (EEG-FM-Bench delivers 0/5 of the proposed evaluation-diagnostic program; Saha & Baumert 2020 still represents the state of the literature on illiteracy).

## Working scope (advisory, layer 20 may revise)

Honest evaluation-diagnostic study on cross-subject MI decoding with subject-, dataset-, and ideally hardware-disjoint splits. MOABB benchmarks + foundation-model probe (LaBraM frozen features) vs strong Riemannian baseline (MDM). 0/1/5/20-shot calibration curves, per-subject distributions, pre-training-overlap audit. **No FM pretraining.**

## Layer status

| Layer | State |
|---|---|
| 20-methodology | pending — methodologist agent runs reuse-scan (`shared/` empty), drafts `approach.md`, pre-registers headline in `protocol-lock.md` |
| 30-experiments | not started |
| 40-analysis | not started |

## Cancel-back triggers

- Layer 20: if no methodology fits 4 GB envelope at the proposed scope, retire-cancel with reason.
- Layer 30: if MOABB / LaBraM / pyRiemann setup proves intractable at run-time, attempt re-design at layer 20 first; retire-cancel only if no path recovers.
- Layer 40: if headline result is uninformative beyond a known result (e.g., underpowered to discriminate FM from MDM), retire-cancel — null is fine, uninformative is not.

## Pre-registration requirement

Per defensibility-critic advisory: the five-part evaluation program (subject + dataset + hardware-disjoint splits; 0/1/5/20-shot curves; per-subject distributions; pre-training-overlap audit; Riemannian + classical-ML baselines) must be pre-registered in `20-methodology/protocol-lock.md` before any headline experiment runs.

## Shared substrate

`shared/` is empty at this track's start. This track is the **first promoter** to `shared/`. Promotion targets per reuse sketch:

- `shared/eval/leakage_audit.py` — pre-training overlap audit (highest-novelty cross-track artifact)
- `shared/eval/fewshot_curve.py` — k-shot calibration curve generator
- `shared/eval/partition.py` — subject-disjoint split utility
- `shared/models/riemannian_baseline.py` — MDM wrapper for any EEG-facing track

Promotion happens at the moment ≥1 plausible second consumer exists (per `shared/README.md`).

## Open carry-overs from layer 10 (close in early track life)

- Direct first-person r/BCI / r/neurotechnology practitioner quote on calibration tax
- Pin the 20–30-min figure to a specific protocol citation (Lotte 2018 review or BCI-IV-2a protocol)
- OpenBCI forum thread end-to-end read for specific friction modes
