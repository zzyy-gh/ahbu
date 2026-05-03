> **Spec:** `20-plan/sleep-staging/{approach,risk-register,protocol-lock,pilots-README,unlock-note-2026-05-03}.md` (under review) + `10-pain-point/sleep-staging/admission.md` (the spec layer 20 received)

# Critic pass — sleep-staging methodology (v2, NSRR FAST + HMC OPEN re-pass) — 2026-05-03

## Verdict

**pass-with-fixes**

The design is substantively sound. The two co-primary headline arms are cleanly separated, held-out partitions are pre-specified with frozen seeds, statistical tests and all four/three interpretation cases are pre-registered, and the compute budget table is honest about the MESA 60–100 hr wall-clock cost. Three findings require fixes before layer-30 entry; one is critical (VRAM claim cites a pilot that does not exist), one is major (multiplicity adjustment missing), and three are minor.

---

## Findings

### CRITICAL

**C-1 — VRAM feasibility claim is self-referential: cites P-3 before P-3 has run**

- Severity: critical
- Location: `approach.md` line 347–348: "U-Sleep inference at batch=32 uses < 2 GB VRAM confirmed by P-3 pilot."
- Problem: `30-implement/sleep-staging/runs/` is empty. P-3 has not been run. The claim "confirmed by P-3 pilot" is false at the time of this lock. The compute-budget table also carries this unverified number into scope (a) scheduling. The 4 GB VRAM feasibility of U-Sleep at batch=32 is therefore an assumption, not a fact.
- Risk: If U-Sleep exceeds 3–4 GB at batch=32, the entire inference plan for HEADLINE-A (~1,850 subjects on GTX 1650) falls. The Kaggle fallback exists but is not the default plan and carries its own setup overhead.
- What to do: Change the claim to read "estimated < 2 GB VRAM at batch=32; to be confirmed by P-3 before any full inference run." Gate HEADLINE-A and HEADLINE-B inference on P-3 passing its success criterion (VRAM <= 3 GB at batch=32). Add this gate explicitly to both pre-run checklists in `protocol-lock.md` §6. P-3 is already listed in pilots-README as critical; it just needs to be listed as a blocking gate in both pre-run checklists, and the "confirmed" language in approach.md must be removed until after P-3 runs.

---

### MAJOR

**M-1 — Two co-primary headlines with no multiplicity correction**

- Severity: major
- Location: `protocol-lock.md` §5 (statistical tests) — both scopes declare `alpha = 0.05` with no mention of Bonferroni, Holm-Bonferroni, or any family-wise error rate correction.
- Problem: The design declares two co-primary headline experiments (HEADLINE-A and HEADLINE-B) each with a one-sided Wilcoxon test at `alpha = 0.05`. Under the null, the family-wise probability of at least one false positive across two independent alpha = 0.05 tests is 1 - 0.95^2 = 9.75 %, nearly double the nominal rate. The protocol-lock is silent on this. No correction is proposed and no rationale for not correcting is given.
- Note on independence: The two headlines use different datasets, different models, and different estimands. However, the absence of any multiplicity discussion is a protocol gap that will be raised by any reviewer.
- What to do: Add one explicit sentence in `protocol-lock.md` §5 stating the multiplicity policy. Two defensible options: (a) Bonferroni-correct at alpha = 0.025 per test; (b) declare the two headlines as testing independent estimands on independent datasets and argue that the family-wise correction is not warranted, citing the independence and noting each headline is individually interpretable. Either is acceptable; what is not acceptable is silence. If option (b) is chosen, the argument must appear in the pre-registration so it cannot be characterized as post-hoc.

**M-2 — HMC PSG AHI metadata availability unconfirmed; stratification contingency vague**

- Severity: major
- Location: `approach.md` line 141–142: "AHI metadata availability to be confirmed at implementation start." `protocol-lock.md` §3 line 128: "Stratified by AHI category … if metadata available; else by epoch-count quartile."
- Problem: The stratification fallback ("else by epoch-count quartile") is not pre-specified in enough detail. Epoch-count quartile stratification does not guarantee balanced clinical strata and is not obviously justified. More importantly, if AHI is absent from HMC PSG, the AHI-stratified secondary analysis in scope (b) disappears — this is not noted as a conditional scope reduction. P-1 should explicitly check for AHI metadata availability, but pilots-README P-1 does not list it as a success criterion.
- What to do: (a) Add "confirm AHI metadata field presence in HMC PSG headers" as an explicit success criterion in pilots-README P-1. (b) In protocol-lock.md §3, either pre-specify the fallback stratification variable more precisely (e.g., "sex + age quartile" rather than "epoch-count quartile") or state explicitly: "If AHI metadata is absent, split is stratified by sex and age-decade; AHI-stratified secondary analysis of scope (b) is dropped." A pre-specified conditional is acceptable; an unspecified one is not.

---

### MINOR

**m-1 — datasets.md not populated; registry still shows `_empty_`**

- Severity: minor
- Location: `30-implement/datasets.md` — table row reads `_empty_`; no sleep-staging datasets (HMC PSG, MESA, Sleep-EDF, CAP Sleep, Dreem-DOD) are registered.
- Problem: CLAUDE.md requires tracking public datasets in this registry. Four datasets are now load-bearing (HMC PSG, MESA, Sleep-EDF Cassette, CAP Sleep as substitute). Dreem-DOD is a framing probe. None are entered. This is a bookkeeping gap, not a methodology flaw, but it leaves the project's actual dataset picture untrackable from a single location.
- What to do: Populate `30-implement/datasets.md` with at minimum HMC PSG (CC-BY 4.0, PhysioNet), MESA (NSRR DUA, N=2056), Sleep-EDF Cassette (CC-BY-NC 3.0, PhysioNet), and CAP Sleep (ODC-BY, PhysioNet). Can be done at layer-30 entry, not blocking.

**m-2 — MESA AHI stratum size is an assumption, not a verified count**

- Severity: minor
- Location: `protocol-lock.md` §3, scope (a) power story: "expected AHI-band distribution (none ~40 %, mild ~25 %, moderate ~20 %, severe ~15 %)."
- Problem: These percentages are described as expected but sourced from nowhere. MESA's published AHI distribution figures are available in the published MESA Sleep papers (Dean et al. 2015, JCSM); they should be cited. If the actual severe-OSA fraction is lower (e.g., 10 % rather than 15 %), the smallest test-set stratum drops to ~185 subjects, still above the N~170 power threshold but with less margin. If it is lower still, the power margin disappears. Using the published figure rather than a round-number assumption is trivially achievable.
- What to do: Add a citation (Dean et al. 2015 JCSM or equivalent) for the AHI-band distribution percentages in `protocol-lock.md` §3. Alternatively, note that P-7 will confirm the actual distribution in the MESA sample; if P-7 reveals the severe-OSA fraction is < 10 %, the power story must be revisited before HEADLINE-A runs.

**m-3 — Spec convention missing on unlock-note-2026-05-03.md**

- Severity: minor
- Location: `unlock-note-2026-05-03.md` line 1 — spec declaration reads `> **Spec:** \`10-pain-point/sleep-staging/admission.md\``.
- Problem: The unlock note is a derivative of the protocol-lock.md (it justifies changes to the lock), so its upstream spec should cite the locked protocol it is unlocking, not the original admission. This is a minor traceability issue but the spec convention in CLAUDE.md is explicit that every artifact names the upstream artifact it serves.
- What to do: Change the spec line to: `> **Spec:** \`20-plan/sleep-staging/protocol-lock.md\` (document being unlocked) + \`10-pain-point/sleep-staging/admission.md\` (original mandate)`

**m-4 — Storage estimate inconsistency (165 GB vs 80 MB × 2056)**

- Severity: minor
- Location: `approach.md` line 320 (compute table): "MESA download via NSRR token (~150 GB for EDF files)"; approach.md line 343: "MESA PSG EDF files are approximately 80 MB per subject × 2,056 = ~165 GB"; risk-register.md line 237: "MESA PSG EDF files total approximately 165 GB".
- Problem: The compute table cites ~150 GB; the explanatory text and risk register both cite ~165 GB. This is a rounding inconsistency rather than an error (the true figure depends on actual EDF sizes, which vary), but having two different numbers in the same document (approach.md) for the same quantity is sloppy and undermines the credibility of the compute budget.
- What to do: Harmonize to one number ("~165 GB") throughout, or add a note that the compute table uses a conservative lower-bound estimate and the text gives the upper-bound.

---

## What I checked

- Spec convention: all five files carry a `> **Spec:**` line. Four of five correctly cite `admission.md`; the unlock-note citation is technically imprecise (m-3 above).
- Pilot-vs-headline discipline: pilots-README correctly labels all pilots as dev-only and explicitly states neither held-out partition is touched. Pre-run checklists in protocol-lock.md §6 enumerate the pilot completion requirements for each scope.
- Two-headline multiplicity: scanned `protocol-lock.md` §5 for any family-wise error rate discussion. None found (M-1).
- Held-out partition pre-specification: both scope (a) and scope (b) partition definitions are frozen with seed=42 and stratification column before any code runs. Partition files will be committed as JSON before any training per the pre-run checklist. Partition independence confirmed (different datasets, different seeds, separate JSON files).
- HEADLINE-A power: severe-OSA stratum at N~280 vs N~170 required at 80 % power for 10 pp gap — margin confirmed sufficient under stated AHI distribution assumptions. Citation gap noted (m-2).
- HEADLINE-B power: N=77 paired — the design explicitly acknowledges this is underpowered for the 17 pp gap test (requires ~105) and correctly reframes around CI width as the primary informative quantity. The defensible-null framing is pre-registered across all four cases. This is honest and acceptable.
- VRAM feasibility: approach.md claims "< 2 GB confirmed by P-3 pilot" — runs/ dir is empty; no such pilot has run (C-1).
- R&K-to-AASM mapping (R-12): the mapping rule `{W→W, S1→N1, S2→N2, S3→N3, S4→N3, REM→REM, MT→None}` is explicit in both risk-register.md and pilots-README. The SHHS mapping in approach.md line 216–220 uses the same convention. Consistent.
- Storage feasibility (R-13): 165 GB MESA storage requirement is acknowledged. compute.md does not enumerate local free disk space (RAM probe also failed per compute.md). R-13 mitigation (batch-process-and-delete pipeline) is operationally plausible given that probability arrays are only ~20 KB/subject post-inference.
- Compute envelope: U-Sleep frozen inference (no training) is the operative mode for both scopes. Training is only the RF on 77 dev subjects (CPU, < 5 min). The GTX 1650 4 GB envelope is used only for inference. The 60–100 hr MESA inference estimate is honest and prominently flagged. Kaggle T4 is documented as a fallback in R-5.
- Leakage from MESA AHI strata into model selection: temperature scaling calibration is fit on the MESA dev subset (10 %, ~206 subjects), which is subject-disjoint from the MESA test partition per protocol-lock.md §3. The calibration fitting procedure does not see test subjects. No leakage path found.
- U-Sleep training-data overlap: the pre-run checklist for scope (a) requires a MESA-vs-U-Sleep training corpus overlap audit before touching the test partition. This is the correct gate.
- HMC AHI metadata contingency: stratification fallback is vague (M-2).
- datasets.md registry: empty (m-1).

---

## What I could not check

- **NSRR token actual validity**: the token lives in `.env` (gitignored); I cannot verify it is not expired or that it was obtained under a DUA that covers both SHHS and MESA. The design correctly requires P-7 to confirm this at layer-30 entry. This is not a design flaw; it is an operational dependency correctly gated behind a pilot.
- **MESA actual AHI distribution**: requires downloading the MESA covariates file. Not feasible at this critic stage. The published distribution can be looked up in Dean et al. 2015 JCSM — that citation gap is flagged as m-2 but I could not verify the underlying numbers.
- **U-Sleep checkpoint license and exact pre-training corpus**: the Perslev et al. 2021 supplementary 16-study list and its overlap with HMC PSG / MESA cannot be verified without accessing the full supplementary. The overlap audit is correctly required by the pre-run checklist. I could not independently run it.
- **Actual local disk space**: compute.md notes the RAM probe failed; no disk-space figure is available. R-13 mitigation assumes >= 200 GB free. I cannot verify this holds.
- **HMC PSG actual AHI metadata field**: I cannot parse HMC EDF headers without downloading the files. P-1 is the correct gate for this.
- **CAP Sleep ECG quality per-subject**: not independently verifiable without downloading CAP files. R-3 / P-1b are the correct gates.
