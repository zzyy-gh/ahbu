> **Historical note (post-rubric-loosening, 2026-05-02):** Written under v1 rubric where defensibility gated admission. Rubric now loosened — defensibility is advisory; layer 40 decides what is publishable. Findings here are still useful as risk-register input for the affected tracks at layer 20.

# Critic pass -- negative-result defensibility -- 2026-05-02

**Scope of this pass.** Pressure-test whether each proposed scope can yield a publishable, actionable, or informative result if the headline finding is null. Addresses selection-shortlist.md Admission debate must bullet 4, which raised the question but did not answer it. Power estimates use a two-sample proportion test (alpha=0.05, power=0.80, two-sided; z_alpha=1.96, z_beta=0.842) unless otherwise noted.

---

## Verdict

| Candidate / scope | Null-defensibility verdict |
|---|---|
| ecg-ppg-realworld (a) -- calibrated abstention for AFib on PTB-XL + PPG corpus | **defensible-null** |
| ecg-ppg-realworld (b) -- skin-tone-stratified PPG eval | **fragile-null** |
| sleep-staging (a) -- clinical-population stratified eval of pretrained stagers | **fragile-null** (DUA-free datasets underpowered for OSA stratification) |
| sleep-staging (b) -- HRV-only EEG-less staging | **defensible-null** |
| cross-subject-eeg -- cross-paradigm diagnostic on MOABB + FM probe under leakage-clean splits | **defensible-null** |
| affective-state -- feature-stability audit (arXiv:2508.10561 sub-scope) | **defensible-null** |

Overall portfolio implication: two scopes require immediate narrowing or dataset-access confirmation before methodology lock (ecg-ppg (b) and sleep-staging (a)). The other four are defensible as stated.

---

## Findings

### 1. ecg-ppg-realworld (a) -- calibrated abstention for AFib on PTB-XL + PPG corpus

**Background.** Fit a classifier for AFib detection on PTB-XL, add an abstention / selective-classification mechanism (conformal prediction, MC-Dropout threshold, or explicit abstain output), and evaluate PPV at a fixed alert rate with and without abstention. A PPG corpus provides the wearable-facing arm.

**Null result scenario.** Headline null = abstention does not improve PPV at clinically relevant alert rates. After calibrated abstention at a 20% abstain rate, PPV remains near the unadjusted baseline.

**Is null informative?** Yes, under three achievable conditions.

(i) Well-powered: PTB-XL carries approximately 1,514 AFIB-labeled records (Strodthoff et al. 2020, Table 1). A 20% held-out split yields ~303 AFIB records. Power calculation for detecting PPV improvement from 0.34 (Fitbit Heart Study baseline in a low-prevalence confirmatory-patch setting) to 0.55 (plausible abstention effect at 20% abstain rate): N required per arm = 87. N available = ~303 AFIB records on held-out. Adequately powered.

(ii) Comprehensive: report the full PPV(abstain_rate) curve across [0%, 30%] abstain budget, not a single operating point. The BASEL inconclusive rate of 17-21% provides a clinically motivated anchor. A flat or declining curve is an informative null -- it establishes the performance ceiling for standard selective-classification under 4 GB compute and advises practitioners that calibration alone does not fix the problem.

(iii) Pre-registered: scope and primary metric (PPV@20%-abstain-rate) locked before touching the held-out split.

**Null risk symmetry.** Asymmetric but not fatally so. A positive result (abstention improves PPV by >=10 pp at 20% abstain) is more actionable for wearable alerting pipelines. A null establishes the ceiling. Both directions are publishable given rigorous evaluation. The null is slightly less novel because CinC 2020 already documents a ~10% generalization drop, but the abstention-specific PPV framing is not in that paper.

**Compute.** PTB-XL inference and feature-based classifiers: trivially feasible on GTX 1650. Conformal prediction or MC-Dropout on a ResNet-1D: feasible within 4 GB. Calibration curve generation requires no GPU.

**Verdict: defensible-null.** A null result on calibrated abstention for AFib on PTB-XL is well-powered, framing-specific, and informative to practitioners and benchmark designers.

---

### 2. ecg-ppg-realworld (b) -- skin-tone-stratified PPG eval

**Background.** Evaluate a PPG-based HR model stratified by Fitzpatrick scale or equivalent skin-tone proxy using a public corpus with labels.

**The data-availability blocker.** The candidate file (section 5 risk 3, section 7 Q3) flags that public ECG/PPG corpora largely lack skin-tone labels. The critic-shortlist.md (critical finding 2) escalated this. Current landscape:

- BUT-PPG (Brno University of Technology): 48 subjects with Fitzpatrick labels. This is the only confirmed public PPG dataset with Fitzpatrick labels at time of writing.
- MIMIC-IV waveforms: ~300,000 ICU waveforms with race/ethnicity self-report as proxy. Self-reported race is a social category, not a skin-tone proxy. The JMIR meta-analysis cited by the candidate uses Fitzpatrick scale to detect the signal-amplitude PPG effect; race is not a valid substitute for the physics mechanism.
- PPG-DaLiA, WESAD, MAUS: no skin-tone labels.

**Power calculation for BUT-PPG (n=48).** Stratified into lighter (Fitzpatrick I-III) vs darker (Fitzpatrick IV-VI): a convenience sample of 48 yields perhaps 25 lighter and 23 darker subjects. Detecting PPV disparity of 0.84 vs 0.65 (the JMIR meta-analysis effect size for SpO2 accuracy at 60-70% saturation) requires N=82 per stratum at 80% power. BUT-PPG is underpowered by a factor of ~3-4x for this effect. For a smaller effect (0.84 vs 0.75): N required per stratum = 315; underpowered by ~13x.

**Null result scenario.** At n=48 total (<=25 in the minority stratum), a null result cannot be distinguished from an underpowered test. The JMIR meta-analysis already established population-level disparity from a larger evidence base. A null on 48 subjects adds no information and will be correctly read as type II error by any reviewer.

**Conditions for recovery.** Two paths exist:
(a) Identify a corpus with >=100 subjects in each Fitzpatrick stratum. A targeted search for PPG + Fitzpatrick datasets is required before methodology lock; no such corpus is confirmed at this time.
(b) Reframe from whether disparity exists (already answered by JMIR meta-analysis) to whether algorithm X closes the gap on whatever corpus exists. Framing (b) is actionable at any n because the goal is algorithm development, not epidemiology. But this is a different scope from what the shortlist proposes and must be stated explicitly.

**Null risk symmetry.** Unfavorably asymmetric. A positive result (disparity confirmed in this corpus) is redundant with JMIR meta-analysis. A null at n=48 is uninformative. Neither direction is strongly valuable at the proposed scale.

**Verdict: fragile-null.** The scope is not defensible in its current framing at publicly available corpus sizes with Fitzpatrick labels. Action required: either identify a larger corpus (MIMIC-IV with melanin-index proxies derivable from signal amplitude ratios may be worth investigating) or reframe to algorithm-correction sub-scope before methodology lock.

---

### 3. sleep-staging (a) -- clinical-population stratified eval of pretrained stagers

**Background.** Evaluate a pretrained stager (U-Sleep or equivalent) on a held-out clinical-population cohort (OSA patients, pediatric, elderly), stratified by AHI band and age decile. Contribution = documenting where the pretrained model degrades and by how much, with calibrated uncertainty.

**DUA-free dataset sizes (the binding constraint).**
- Sleep-EDF extended: 78 subjects, healthy adults 21-35 yr. No OSA or pediatric subgroup.
- Dreem-DOD-O: 55 OSA patients (Zenodo MIT license, confirmed open in gap-closing pass).
- Dreem-DOD-H: 25 healthy adults.
- HMC PSG (PhysioNet 2018 CinC): 151 subjects, mixed pathology.
- CAP Sleep (PhysioNet): ~108 subjects, various pathologies.
Total without DUA: approximately 417 subjects combined. OSA-specific: Dreem-DOD-O gives 55 confirmed OSA patients.

**Power calculation for OSA stratification.** Korkalainen et al. 2020 measured an 8 pp accuracy drop (84.5% non-OSA vs 76.5% severe OSA). N required to detect this effect at 80% power: N=384 per stratum. Dreem-DOD-O: n=55 OSA, underpowered by 7x. Even for a larger assumed effect (84.5% vs 72%, 12pp): N required = 170; still 3x the available n=55.

**Null result scenario.** If the pretrained stager does NOT degrade on OSA patients at n=55, the contribution is: we do not detect degradation at this power level. This is not an informative null. Korkalainen 2020 established degradation at larger N; a null at n=55 contradicts but does not override that finding. A reviewer will correctly attribute the null to insufficient power, not to absence of the effect.

**Conditions for recovery.** The scope is adequately powered only with NSRR data: SHHS (~5,800 subjects with OSA stratification) or MESA (~2,000 multi-ethnic subjects). NSRR DUAs have a documented admin lag of weeks (flagged in candidate file and shortlist). This is a timeline risk, not a technical blocker.

**Mitigation path.** Submit NSRR DUA on day one of methodology phase. Pilot on Dreem-DOD-O and HMC PSG with honest CI widths that make the underpowered status explicit, while DUA processes. This converts fragile-null to defensible-null by the time the headline evaluation runs, but only if the DUA is initiated immediately.

**Null risk symmetry.** Moderately asymmetric. A positive result (degradation documented with confidence intervals) is a clean contribution regardless of N. A null is informative only at NSRR scale. The asymmetry is manageable if the DUA path is treated as a requirement, not a nice-to-have.

**Verdict: fragile-null on DUA-free datasets alone; conditionally defensible-null if NSRR DUA is initiated at methodology-lock.** Write the DUA initiation into the risk register as a kill criterion: if DUA not received in 4 weeks, pivot to scope (b).

---

### 4. sleep-staging (b) -- HRV-only EEG-less staging

**Background.** Train and evaluate a sleep stager using only HRV-derived features (R-R intervals, spectral HRV, SDNN, RMSSD, pNN50, LF/HF) without EEG, on HMC PSG (151 subjects, PhysioNet, no DUA) where ECG is available alongside EEG.

**Power calculation.** Comparing HRV-only to an EEG baseline on a 3-class task (Wake/NREM/REM): expected EEG accuracy ~82%, HRV-only ~65% (published HRV-only staggers). N required to detect this 17pp gap at 80% power = 105 subjects per arm. HMC PSG has 151 subjects: approximately 75 per arm with a 50/50 split. Adequate for a 17pp effect; borderline for a 10pp effect (N required = 357).

**Null result scenario.** Headline null = HRV-only staging performs at EEG-parity. This is a valuable null: it implies EEG is not necessary for sleep staging in this population, directly informing wearable deployment (Oura, Fitbit, devices without EEG). AASM guidelines require EEG for PSG; a null motivates revisiting that requirement for specific use cases.

**Conditions for informative null.**
(i) Well-powered: 105+ subjects with both ECG and EEG available. HMC PSG (151) is acceptable for the large-effect scenario.
(ii) Stratified: report null separately for each subgroup (OSA severity, age). An aggregate null can hide informative per-subgroup differences.
(iii) Per-stage: a null on 3-class accuracy may hide per-stage results (HRV-only may match EEG on W/REM but diverge on N1/N2). Per-stage F1 is required.

**Null risk symmetry.** More symmetric than the other scopes. EEG-parity supports wearable deployment; EEG-superiority confirms EEG necessity and defines the wearable performance ceiling. Both outcomes are directly actionable.

**Compute.** HRV feature extraction (NeuroKit2, hrv-analysis) + RandomForest/GBM: trivially feasible on GTX 1650, CPU-only for the core experiment. Optional LSTM or small transformer on HRV sequences: feasible within 4 GB.

**Verdict: defensible-null.** Even at HMC PSG scale (151 subjects), the 17pp effect is detectable and both directions are informative. Condition: report per-stage and per-stratum results to maximize information content of any outcome.

---

### 5. cross-subject-eeg -- cross-paradigm cross-subject diagnostic on MOABB + FM probe

**Background.** Run the five-part evaluation program from cross-subject-eeg.md section 6 under leakage-clean splits: (a) subject + dataset + hardware-disjoint splits simultaneously, (b) 0/1/5/20-shot calibration curves per subject, (c) per-subject performance distributions, (d) pre-training-overlap audit, (e) Riemannian baselines under same splits. Datasets: MOABB (14 MI datasets), EEG Foundation Challenge HBN Releases 1-11 (~2,600 subjects, CC-BY-SA-4.0, no DUA, confirmed in gap-closing pass).

**Null result scenarios and their value.**

Null A: Foundation models do NOT outperform Riemannian baselines under leakage-clean splits. This is arguably the most likely outcome given EEG-FM-Bench finding that compact architectures with domain-specific inductive biases consistently outperform significantly larger models. A null here IS the contribution: it quantifies the performance ceiling of large EEG-FMs for cross-subject transfer under honest conditions -- exactly what the EEG Foundation Models Critical Review (arXiv:2507.11783) calls for but does not deliver.

Null B: Pre-training-overlap audit finds no overlap between evaluation sets and pre-training corpora. This null is also informative: it clears the evaluated FMs of data-contamination suspicion and makes their cross-subject numbers trustworthy.

Null C: No bimodal per-subject distribution (BCI illiteracy rate lower than the 15-30% prior under modern FMs). This would update the field on whether the illiteracy problem persists under large pretrained models.

**Power for per-subject distribution characterization.** Detecting BCI illiteracy rate 30% vs null baseline 10% at 80% power requires N=62 subjects. MOABB aggregated across datasets has hundreds of subjects; PhysionetMI alone has 109. Adequate for aggregate analysis. BCI-IV-2a (9 subjects) is trivially underpowered alone and must not be the sole dataset.

**Power for leakage-inflated vs clean-split comparison.** If published leakage-inflated accuracy is ~72% and clean-split accuracy is ~58% (14pp gap per the EEG-FM-Bench finding pattern): N required = 182 subjects. MOABB aggregation clears this.

**Pre-registration requirement.** The five-part evaluation program must be pre-registered before running any experiment: which FM checkpoints, which datasets, which split procedure, what constitutes overlap in the pre-training audit. Without pre-registration, the contribution risks being read as post-hoc cherry-picking of evaluation conditions.

**Compute.** Riemannian baselines (pyRiemann): CPU-only, trivial. FM inference as frozen feature extractor: feasible within 4 GB for LaBraM / BENDR / BIOT. Full FM fine-tuning is out of scope and not needed for a diagnostic contribution.

**Null risk symmetry.** Highly symmetric. FM wins, FM loses, overlap found, overlap absent, bimodal distribution confirmed or disconfirmed -- all are informative. The contribution is the diagnostic infrastructure and leakage-clean numbers, not a particular performance level. This is the most null-symmetric scope in the portfolio.

**Verdict: defensible-null.** All plausible outcomes are informative. Power is adequate at MOABB aggregation scale. Pre-registration is the one non-negotiable condition.

---

### 6. affective-state -- feature-stability audit sub-scope (arXiv:2508.10561)

**Background.** Replicate and extend the finding from arXiv:2508.10561 that only 2 of 164 EDA features show reproducible, statistically significant association with arousal across studies. The AHBU contribution: independent replication applied to cardiac features (HRV, ECG-derived) on a new combination of public datasets (DEAP, WESAD, MAHNOB-HCI).

**Clarifying the unit of analysis.** This is a feature-level cross-dataset reproducibility study. N=164 features is the sample size for the binomial test. Confirming the 2/164 finding is statistically robust: P(X<=2 | n=164, p=0.05 expected base rate) = 0.0104; P(X<=2 | n=164, p=0.10) = 5.8e-06; P(X<=2 | n=164, p=0.20) = 1.1e-13. Even at a generous 5% expected base reproducibility rate, observing only 2/164 is significant at p=0.01. The finding is well-powered as a binomial test at N=164.

**Null result scenario.** Headline null for AHBU = when cardiac features (HRV, ECG power-spectral features) are tested across DEAP/WESAD/MAHNOB on arousal, MORE than 2% show reproducibility. This null is informative: it establishes that cardiac features have higher cross-study stability than EDA, supporting the arousal-reframing angle and motivating a cardiac-arousal-decoding-done-honestly sub-scope.

**Non-redundancy.** arXiv:2508.10561 focused on EDA features. Brookshire 2024 focused on DNN-EEG leakage. Apicella 2024 reviewed cross-subject methods. None tested cardiac feature reproducibility across studies in this way. The AHBU contribution is non-redundant if extended to cardiac features.

**Conditions for informative null.**
(i) Feature list specified before running analysis (pre-registered). Reporting only the features that turn out reproducible post-hoc recapitulates the original paper trivially. The contribution requires testing a NEW feature set on NEW dataset combinations.
(ii) Datasets listed and justified before analysis. DEAP uses stimulus-class labels, not self-report; WESAD has strong within-session structure that can inflate reproducibility if sessions are not disjoint across studies. Both hazards must be documented.
(iii) Arousal operationalization consistent across datasets. DEAP uses 2-level arousal from stimulus rating; WESAD uses 3-class affect condition. Harmonization must be stated and justified before feature testing begins.

**Compute.** Feature extraction from HRV/ECG on DEAP/WESAD/MAHNOB: CPU-only, trivial. Statistical testing with FDR correction: no GPU. The scope fits the 4 GB constraint with room to spare.

**Null risk symmetry.** Symmetric. High cardiac reproducibility motivates the cardiac-arousal sub-scope. Low cardiac reproducibility confirms field-wide feature instability and motivates do-not-use-these-features-until-stability-is-established. Both outcomes are publishable.

**Verdict: defensible-null.** Both directions informative, adequately powered as a feature-count binomial test, non-redundant with the EDA-focused source paper. Three conditions must be pre-registered: feature list, datasets, arousal operationalization. Failure to pre-register converts this to a near-null.

---

## Synthesis: what must change before methodology lock

| Scope | Required action before methodology lock |
|---|---|
| ecg-ppg (a) abstention | Pre-register primary metric (PPV@20%-abstain on PTB-XL held-out). Name the operative PPG corpus and confirm it has HR/rhythm labels. |
| ecg-ppg (b) skin-tone | Identify a corpus with >=100 subjects per Fitzpatrick stratum, OR reframe to algorithm-correction scope with honest caveat on disparity-detection power. Current framing is blocked. |
| sleep-staging (a) OSA eval | Submit NSRR DUA on day one of methodology phase. Add kill criterion: DUA not received in 4 weeks means pivot to scope (b). Pilot on Dreem-DOD-O (n=55) with explicit CI widths. |
| sleep-staging (b) HRV-only | Name the operative dataset (HMC PSG for DUA-free start; MESA if DUA granted). Pre-register 3-class per-stage F1 as primary metric. |
| cross-subject-eeg | Pre-register the five-part evaluation program before running any experiment. Specify FM checkpoints and overlap-audit procedure. |
| affective-state feature audit | Pre-register feature list, datasets, and arousal operationalization before running any feature extraction. Extend arXiv:2508.10561 to cardiac features specifically. |

---

## What I checked

- Read all four candidate files end-to-end, including gap-closing appendices.
- Read selection-shortlist.md and critic-shortlist.md in full.
- Read 00-vision/README.md hard constraints and 10-pain-point/README.md validation rubric.
- Read 30-implement/compute.md for the GTX 1650 4 GB binding constraint.
- Ran two-sample proportion power analysis for each scope (alpha=0.05, power=0.80, two-sided). Key results: skin-tone at BUT-PPG n=48 is underpowered 3-13x; OSA eval at Dreem-DOD-O n=55 is underpowered 3-7x; HRV-only vs EEG at HMC PSG n=151 is adequately powered for 17pp effect; abstention on PTB-XL held-out ~303 AFIB records is adequately powered for 21pp PPV improvement; MOABB aggregation clears N=62 for BCI illiteracy rate detection.
- Ran binomial test for affective-state feature reproducibility claim: P(X<=2 | n=164, p=0.05) = 0.0104; P(X<=2 | n=164, p=0.10) = 5.8e-06.
- Checked dataset sizes: PTB-XL AFIB ~1,514 records (Strodthoff 2020 Table 1), BUT-PPG 48 subjects with Fitzpatrick labels, Dreem-DOD-O 55 OSA (MIT license confirmed), HMC PSG 151 subjects, BCI-IV-2a 9 subjects, HBN Releases 1-11 ~2,600 subjects (CC-BY-SA-4.0 confirmed).
- Cross-checked the Korkalainen 2020 8pp OSA accuracy degradation figure against the sleep-staging candidate.
- Verified Dreem-DOD-O and EEG Foundation Challenge data access status from the gap-closing appendices in the candidate files.
- Checked that arXiv:2508.10561 targets EDA features and that cardiac features are outside its scope (confirmed from candidate affective-state.md section 3 reproducibility sub-section).

## What I could not check

- Did not independently verify the PTB-XL AFIB record count by querying the dataset. The ~1,514 figure comes from Strodthoff et al. 2020 Table 1.
- Did not verify whether a PPG corpus larger than BUT-PPG (n=48) with Fitzpatrick labels exists. A targeted search for PPG + Fitzpatrick datasets was not performed; such a corpus may exist in recent clinical releases. The skin-tone scope should be blocked pending this search.
- Did not sum per-dataset subject counts across all 14 MOABB MI datasets. The aggregate almost certainly clears N=62 but the exact total is unverified.
- Did not verify whether arXiv:2508.10561 has been peer-reviewed. If preprint only, AHBU gains an additional independent-replication motive for the feature audit.
- Did not check whether MIMIC-IV PPG amplitude ratios could serve as melanin-index proxies for skin-tone stratification. If such a proxy is extractable at scale, the skin-tone scope may be recoverable without Fitzpatrick labels.
- Did not survey the conformal-prediction-on-ECG literature to establish how novel the abstention scope is. This was flagged as open in critic-shortlist.md major finding 2 and remains open.
