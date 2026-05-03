> **Spec:** `30-implement/ecg-ppg-realworld/results.md` + `20-plan/ecg-ppg-realworld/protocol-lock.md`

# Lessons — ecg-ppg-realworld (post-headline)

What this track contributes to the AHBU substrate, and what we learned
that future tracks should consume rather than re-derive.

---

## 1. Already-promoted shared substrate (validated by this headline)

`30-implement/shared/eval/` — first promotion, originated by P-4 of
this track:

- `selective_classification_curve(confidences, correct, coverages)` —
  monotone-PPV-vs-coverage scaffolding with confidence-correctness
  AUROC summary statistic. **Used by the headline.** Validated on real
  held-out test data (1,650 records); pre-validated on the P-4 dev
  hold-out (3-epoch model, 1,320 records). Two consumers confirmed.
- `ppv_at_coverage(y_true, y_pred, confidences, coverages, ...)` — PPV
  with stratified bootstrap CI. **Used by the headline.** Validated on
  real held-out test data; pre-validated on the P-4 dev hold-out.
  Two consumers confirmed.

Promotion event recorded in
`30-implement/shared/eval/README.md`. Both files are now load-bearing
for at least one published headline; substrate is *real*, not
aspirational.

## 2. Promotion candidates surfaced by this headline

The following code currently lives in
`30-implement/ecg-ppg-realworld/code/headline/headline_ecg_ppg.py`
and is a strong candidate for promotion if a second track adopts the
same pattern. Each candidate's "second-consumer" check is listed.

### 2a. `selective_classification` test runner pattern

Phases: `train → calibrate → write-checklist → test → aggregate`,
with:
- Per-phase argparse + per-phase artifact paths.
- Held-out single-use idempotency guard: refuses to overwrite
  `runs/headline/test_seed{seed}.json` once written.
- Auto-generated pre-run-checklist that inspects expected artifacts
  on disk, refuses to run `test` unless `STATUS:
  ALL_CHECKS_PASSED` is present in the file.
- Robust separation of dev-only (train, calibrate, checklist) and
  held-out (test) phases at the script-flag level.

**Candidate path:** `30-implement/shared/runner/headline_skeleton.py`.

**Plausible second consumer:** affective-state and sleep-staging
HEADLINE-B both have a single-pretrained-model, single-test-touch,
PPV-at-coverage shape. cross-subject-eeg is k-shot LOSO and does NOT
fit this skeleton — it has its own headline runner already.

**Trigger condition for promotion:** sleep-staging or affective-state
adopts >50 % of this skeleton in their headline runner. If they
diverge significantly, do NOT promote (premature abstraction risk).

### 2b. PPV-flavoured McNemar 2×2 builder

Logic in `run_test()` that constructs a 2×2 from the AF-predicted-set
under (no-abstain, abstention) conditions, with **drops counted as
discordant cells by direction-on-PPV** (a no-abstain-TP that abstention
drops contributes to b; a no-abstain-FP that abstention drops
contributes to c). Yields the textbook McNemar p-value via
`statsmodels.stats.contingency_tables.mcnemar(table, exact=False,
correction=True)`.

**Candidate path:**
`30-implement/shared/eval/mcnemar_ppv_flavoured.py`.

**Plausible second consumer:** any track with a precision-flavoured
abstention claim:
- affective-state — abstention on uncertain emotion classifications;
  if framed as "PPV-on-arousal-positive-class".
- sleep-staging — confidence stratification on stage predictions; if
  framed as PPV-of-N1-detection or REM detection (clinically motivated).

**Trigger condition for promotion:** the affective-state headline
adopts this construction. (Pre-emptive promotion is risky because
"drops counted as discordant by direction-on-target-metric" is the
non-trivial bit; we want to see the second use to confirm the
abstraction works.)

### 2c. Pre-run-checklist auto-generation pattern

`write_checklist(args, runs_dir)` inspects expected artifacts on disk
and writes a checklist file whose end-of-file `STATUS` line gates
downstream phases. Logic includes "test_seed*.json absent" =
"not yet touched" and is generic across tracks.

**Candidate path:**
`30-implement/shared/runner/checklist.py`.

**Plausible second consumer:** sleep-staging HEADLINE-B has the same
single-touch held-out discipline; cross-subject-eeg's `run_headline.py`
already implements its own version. Promotion only worthwhile if 2+
tracks converge.

## 3. Methodology lessons (informational, not promotion candidates)

### 3a. P-5 informative-fail predicted the headline calibration story

The P-5 pilot (3-epoch model, T ≈ 1.03, calibration noise-floor)
foreshadowed the headline finding (26-epoch model, T ≈ 0.94, still
near noise-floor). The track lead's reading of P-5 as "informative
fail not headline blocker" (recorded in pilots-README §P-5 result
field) was correct. **Lesson:** when a calibration-pilot fails on
"didn't improve ECE" but the model isn't over-confident, do not
patch — re-run the pilot at the headline checkpoint and report
honestly. This is a within-layer-agile success of the pilot
discipline.

### 3b. Class-weighted CrossEntropy + cosine LR + early stopping
worked well

Out of the box, no hyperparameter search beyond protocol-lock §4.
Best AUROC AF on cal hold-out: 0.948 at epoch 26; early-stop fired
at epoch 36 (patience=10 on dev-AF AUROC). Training time 2.9 hr on
GTX 1650 4 GB at fp32 batch=8. **Lesson:** the protocol-lock
hyperparameters are conservative defaults that work; do not feel a
need to tune. Same defaults are reasonable starting point for
sleep-staging HEADLINE-B 1D-ResNet fallback if R-4 lands on that
path.

### 3c. PPV-flavoured McNemar table semantics need explicit pre-reg

In v1 of the protocol-lock, the McNemar test was specified ambiguously
as "McNemar's test on accuracy". The critic-v2 M-2 fix forced
disambiguation and produced the PPV-flavoured construction reported
here. **Lesson:** when a primary metric is precision-flavoured (PPV)
or otherwise non-accuracy, the inferential test must explicitly
operate on that metric, not on a related-but-different one. Carry
this principle forward to the affective-state and sleep-staging
locks.

### 3d. Achieved abstention rate ≠ target abstention rate

A confidence threshold quantile-fit on dev-train will drift slightly
on test due to within-source distribution shift. This is bounded
(+1.6 pp here, within BASEL window) and pre-reg'd in §4. **Lesson:**
report achieved rate alongside target rate every time. If the drift
is large enough to escape the target window, treat as a finding for
the limitations section, not a quiet correction.

### 3e. Pre-run-checklist refuse-to-run is cheap insurance

The script's refusal to run `test` unless the checklist file ends
with `STATUS: ALL_CHECKS_PASSED` is a 5-line addition with high
benefit. It saved one false-start when the cwd-issue caused the bg
shell to fail before python launched (the failure produced no
held-out touch precisely because the checklist + idempotency guards
were in place to prevent any accidental partial run). **Lesson:**
single-touch held-out tests should always have an idempotency guard
+ a checklist. Carry forward to all four tracks.

## 4. Negative lessons (things NOT to copy)

### 4a. main() must print failure dicts

The original `main()` returned exit code 1 on early failure (e.g.,
missing dep, missing checklist) without printing the failure dict.
Cost: ~10 minutes of "exit 1, no output, log file 0 bytes" debugging
before fixing. **Lesson:** always print the result dict (or a summary)
on both success AND failure paths; do not rely on exit codes alone for
diagnostics.

### 4b. `tee` in a `cd && cmd | tee` bg-shell stanza loses cwd

The bg-shell does not preserve the cwd between top-level Bash tool
calls. Use absolute paths for python.exe, the script, AND the log file
when starting a long-running bg task, otherwise the `cd` may silently
no-op and the python invocation never runs.

## 5. What this track did NOT learn

This track did NOT test:
- Cross-source / cross-device generalization (single CinC 2017 source).
- Patient-disjoint partition (CinC 2017 lacks patient IDs).
- Alternative abstention scores (deep ensembles, MC-dropout, energy,
  ODIN). These are exploratory follow-ups.
- Multi-seed stability (single primary seed; secondary deferred).

These are honest gaps in what this track contributes to the substrate.
Do not retro-fit "what we learned" claims into these areas.
