# Critic pass — cross-subject-eeg methodology (layer 20 → layer 30 gate) — 2026-05-02

> Tooling note: this critic agent's toolset (Read, Grep, Glob, WebFetch, Bash) does not include Write. Bash heredoc was blocked per the brief's "use Write tool" instruction. The critic produced the full report as text returned to lead; lead transcribed it to this file. This is a process gap to fix in `.claude/agents/critic.md` (add Write to allowed tools) — captured separately.

## Verdict

**pass-with-fixes**

Methodology is substantially sound and does not need redesign. Two major findings + five minor findings require documented fixes before layer 30 begins. None are fatal. `protocol-lock.md` is the strongest pre-registration document this project has produced — all defensibility-advisory requirements are met.

## Findings

### Critical

None.

### Major

**M-1 — Compute envelope expansion is undocumented in `30-implement/compute.md`.**
Location: `risk-register.md` R-3 mitigation step 3 + kill criterion; `approach.md` §Compute budget table footnote "local / Kaggle"; `approach.md` §Model family LaBraM-Base paragraph. The methodology silently expands the binding compute resource from GTX 1650 4 GB (the only hardware documented in `30-implement/compute.md` as binding) to include Kaggle T4 (16 GB, 9 hr/week) as a named fallback for FM feature extraction. `30-implement/compute.md` lists Kaggle generically under "free / public compute that may be in scope" but gives no track-specific opt-in, no acknowledged data-egress cost, no recognition that Kaggle is now a load-bearing fallback. Not fatal — methodology limits Kaggle use to FM feature extraction only when local GPU is insufficient (R-3); Riemannian headline remains local-only — but the admission record + layer-20 template both anchor feasibility to "4 GB envelope," and the defensibility critic used the same anchor. Fix: add a track-specific note to `30-implement/compute.md` documenting the fallback explicitly. Confirm Kaggle account + quota at week-1 environment setup.

**M-2 — Additional dev dataset selection is deferred past protocol-lock without leakage-audit coverage.**
Location: `protocol-lock.md` §3 MOABB arm — "Dev datasets: BNCI2014_001 + one additional dataset, chosen as either Cho2017 or Lee2019." Held-out test (PhysionetMI) is frozen; secondary dev is not. Leakage audit in §4 audits only test datasets for FM pre-training overlap, not dev-dataset candidates. LaBraM pre-training corpus is documented to include BCICIV_2a / BCICIV_2b (already known dev datasets). Cho2017 / Lee2019 not yet audited. If either is in the corpus and selected as secondary dev, FM dev-split accuracy is contaminated. Headline (PhysionetMI) is unaffected, but pilot P-4 estimates and dev-split ablations become uninterpretable. Ablation 2 (overlap-removed FM) handles dev-set contamination but only if first detected. Fix: add one sentence to `protocol-lock.md` §4 — "Dev dataset candidates (Cho2017, Lee2019) are also audited for LaBraM pre-training overlap before any FM evaluation on the dev split begins. Result logged in `30-implement/cross-subject-eeg/runs/leakage_audit_result.json` alongside the test-split audit."

### Minor

**m-1 — k=0 protocol asymmetry between FM and MDM is undisclosed.**
Location: `approach.md` §Evaluation protocol §Shot-level evaluation (k=0); §Model family Model A. At k=0, LaBraM uses nearest-centroid in embedding space with one centroid per class from dev-set subjects; MDM uses LOSO with covariance geometry from dev-set training subjects. Both zero-target-subject, but information types differ. A reader may attribute performance gap to structural asymmetry rather than model quality. Fix: add one sentence to `approach.md` §Shot-level evaluation clarifying both conditions are zero-target-subject in the same sense.

**m-2 — "Hardware-disjoint" claim is verified for one dev-test pair only but stated as a general property.**
Location: `approach.md` §Dataset §Held-out partition; `protocol-lock.md` §3. PhysionetMI (BCI2000 / 64-channel) vs BNCI2014_001 (g.USBamp 22-channel) verified hardware-distinct. Cho2017 / Lee2019 hardware not yet verified. If selected secondary dev used a BCI2000 system, the blanket claim weakens. Fix: narrow the claim in `protocol-lock.md` §3 to the primary pair; add a note that secondary dev hardware will be documented at selection time.

**m-3 — BCI-illiteracy threshold definition contains a factual error and an inconsistency across documents.**
Location: `approach.md` §Per-subject distributions — "70 % on 4-class MI is chance-level; threshold = 25 % for 4-class, 50 % for 2-class." Chance on balanced 4-class is 25 %, NOT 70 %. The 70 % is a common usability threshold; subjects below 70 % are often labelled BCI-illiterate. Both documents define the operative threshold as 25 % (true chance), which means the protocol classifies only truly chance-performing subjects as illiterate. Saha & Baumert 2020 (cited admission evidence) uses a criterion above chance; literature commonly uses 70 % on 4-class. Using 25 % will produce a lower measured illiteracy rate than cited figures. Fix: harmonize. Either (a) use 25 % and label "fraction at or below chance," noting it differs from the 70 %-threshold convention; or (b) use 70 % per Saha & Baumert / BCI-IV-2a protocol and report both. Option (b) more informative and directly comparable. Either way, fix the erroneous "70 % is chance-level" clause.

**m-4 — Ablation 2 (overlap-removed FM) trigger is near-certain on dev set; its elevated status is not pre-registered.**
Location: `approach.md` §Ablations Ablation 2; `protocol-lock.md` §1(d). LaBraM pre-training corpus includes BCICIV_2a / BCICIV_2b — both dev datasets here — so the trigger condition is near-certain. When triggered, the overlap-removed FM result is a primary sub-result (measures contamination inflation directly), not a secondary curiosity. Currently pre-registered as conditional / optional — understates likely importance. Fix: add note to `protocol-lock.md` §1(d) — "Given LaBraM pre-training corpus is documented to include BCICIV_2a / BCICIV_2b (both dev-set datasets), Ablation 2 is expected to trigger on the dev set. When triggered, the overlap-removed FM result is elevated to a required headline component and reported in the main results table alongside the pre-training-overlap audit."

**m-5 — Novelty sub-claim over-states scope.**
Location: `approach.md` §Novelty notes, third bullet — "per-subject distributions with explicit illiteracy-rate characterization are not reported in any existing benchmark." Universal negative not supported by cited sources. MOABB produces per-subject result tables; several LOSO EEG papers report per-subject distributions. Defensible claim is narrower: not reported in EEG-FM-Bench or the TCPL benchmark paper (the two cited comparison points). The genuine novelty is the COMBINATION of all five components simultaneously under leakage-clean splits. Fix: replace "not reported in any existing benchmark" with "not reported in EEG-FM-Bench or the TCPL benchmark paper, which provide the direct comparison points."

## What I checked

- All four spec docs in full (admission record, defensibility critic §5, track README, layer-20 template).
- All four artifacts in full (`approach.md` 640 lines, `risk-register.md` 357 lines, `protocol-lock.md` 268 lines, `pilots/README.md` 165 lines).
- `30-implement/compute.md` and `portfolio.md`.
- Spec drift: all five components of the §6 evaluation-diagnostic program addressed explicitly.
- Pre-registration completeness against defensibility checklist: held-out partition, primary metric, statistical test, headline-positive vs headline-null definition, FM checkpoint, pre-training corpus list — all present.
- Compute-envelope coherence: found M-1.
- Kill criteria across 10 risks: all numeric / yes-no / named-substitution. None hand-wavy.
- Held-out discipline: defined operationally; pre-run checklist required; pilots barred from test split.
- Pre-training-overlap audit + Riemannian baseline pre-registered as headline components, not demoted to ablations.
- 5 pilot probes stay on dev only; all result fields "[FILL AFTER RUN]".
- Shared promotion targets match reuse sketch: 4 artifacts, second consumers named.
- Novelty claims vs cited evidence: found m-5.
- k=0 symmetry: found m-1.
- Illiteracy threshold consistency: found m-3.
- Dev-dataset leakage-audit coverage: found M-2.
- Ablation 2 trigger probability vs pre-reg status: found m-4.

## What I could not check

- LaBraM-Base loads + runs within 3 GB on GTX 1650 at batch=1 float32 — pilot P-1 will check.
- PhysionetMI absent from LaBraM pre-training corpus — taken at face value; leakage_audit.py is authoritative.
- MOABB 1.1.x processes all 109 PhysionetMI subjects without quality issues — pilot P-2.
- LaBraM published pre-training corpus list completeness — risk register flags this; if incomplete, audit result is a lower bound.
- Cho2017 / Lee2019 LaBraM-corpus membership — gap M-2.
- Kaggle account availability + T4 quota — operational risk behind M-1.
- Cho2017 / Lee2019 recording hardware — relevant to m-2.
- Did not re-read arXiv:2405.18765 to enumerate complete LaBraM pre-training corpus.
