# Candidate: Automated Sleep Staging & Sleep-Event Detection

## 1. Pain point statement

Sleep staging — the assignment of 30-second epochs to Wake / N1 / N2 / N3 / REM — is the foundation of every sleep study, every consumer sleep tracker, and most sleep research. Two facts are in tension. (a) Manual scoring by certified technologists takes ~1.5–2 hours per night and is itself only ~76% reliable across raters (Cohen's kappa 0.76 overall, but only 0.24 for N1) — i.e., the "ground truth" the field chases has a built-in ceiling. (b) Automated PSG stagers (U-Sleep, DeepSleepNet, SleepTransformer) have approximately closed the gap to that ceiling on healthy adults, yet performance still degrades meaningfully on apnea patients, children under 2, the elderly, ICU patients, and anyone whose EEG morphology departs from textbook. Meanwhile consumer wearables (Oura, Whoop, Fitbit, Apple Watch) ship "REM / Deep / Light" labels to tens of millions of users with stage-level accuracies in the 38–56% range, and users notice. The pain is *not* "we need a better classifier on Sleep-EDF" — that benchmark is saturated. The pain is the *gap between the saturated lab number and the operational reality* in clinical edge populations and in EEG-less wearable contexts, plus the unresolved question of what "ground truth" even means when human raters disagree this much.

## 2. Constituency

- **Sleep technologists / scoring services** doing 1–2 hours of manual scoring per study at $23–$72/hr ([ZipRecruiter listing](https://www.ziprecruiter.com/Jobs/Remote-Sleep-Study-Scoring); [SleepScoringSolution](https://www.sleepscoringsolution.com/)).
- **Sleep clinicians** dealing with AASM v3 (2023) hypopnea-rule changes that create insurance-driven scoring inconsistency ([Rosen & Auckley, JCSM 2024](https://jcsm.aasm.org/doi/10.5664/jcsm.10944)).
- **Pediatric and geriatric sleep researchers** whose populations are systematically under-served by adult-trained models ([van Gorp et al., Sleep Med Rev 2023](https://www.sciencedirect.com/science/article/pii/S1389945723001260)).
- **Wearable users / clinicians fielding their questions** — millions of consumers with Oura/Whoop/Fitbit/Apple Watch stage data of unclear validity ([forum threads cited below](#3-evidence-of-pain)).
- **Open-science maintainers** (U-Sleep, MNE-Python sleep tutorial, PhysioNet Sleep-EDF, NSRR/SHHS, MASS) handling user issues about edge cases.
- **Apple, Oura, Whoop, Fitbit** themselves — ongoing FDA-clearance and validation literature shows the industry is actively trying to close gaps ([Apple Watch sleep apnea 510(k) K240929](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K240929)).

## 3. Evidence of pain

### 3a. Inter-rater ceiling — the moving target

- **Lee et al., JCSM 2022, "Interrater reliability of sleep stage scoring: a meta-analysis"** ([PMC8807917](https://pmc.ncbi.nlm.nih.gov/articles/PMC8807917/), [DOI 10.5664/jcsm.9538](https://jcsm.aasm.org/doi/10.5664/jcsm.9538)). Pooled Cohen's kappa = **0.76** overall (95% CI 0.71–0.81). Per-stage: W 0.70, **N1 0.24**, N2 0.57, N3 0.57, R 0.69. AASM kappa 0.76 vs older R&K 0.68.
- **Danker-Hopfe et al., J Sleep Res 2009**, original AASM-vs-R&K comparison ([PMID 19250176](https://pubmed.ncbi.nlm.nih.gov/19250176/)).
- **Inter-institutional drift:** Magalang et al. and follow-ups show inter-center agreement drops from ~80% within an institute toward ~60% across countries (referenced in [Lee meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC8807917/) and [Sino-American AASM comparison, Sleep Breath 2019](https://link.springer.com/article/10.1007/s11325-019-01801-x)).
- **ICU sleep:** manual scoring of ICU PSG shows substantially lower agreement again ([BMC Res Notes 2025](https://bmcresnotes.biomedcentral.com/articles/10.1186/s13104-025-07198-z)).

### 3b. State-of-the-art automated stagers — gap to humans

- **Perslev et al., U-Sleep, npj Digital Medicine 2021** ([PMC8050216](https://pmc.ncbi.nlm.nih.gov/articles/PMC8050216/)). Trained on 15,660 PSGs across 16 studies. Mean F1: W 0.90, **N1 0.53**, N2 0.85, N3 0.76, REM 0.90. Authors state U-Sleep "performs as accurately as the best of the human experts."
- **Supratak et al., DeepSleepNet, IEEE TNSRE 2017** ([arXiv 1703.04046](https://arxiv.org/abs/1703.04046)). 86.2% / macro-F1 81.7 on MASS; 82.0% / 76.9 on Sleep-EDF.
- **Phan et al., SleepTransformer, IEEE TBME 2022** ([PMC10827185](https://pmc.ncbi.nlm.nih.gov/articles/PMC10827185/)) — interpretability and uncertainty, on-par accuracy.
- **U-Sleep resilience to AASM rules, npj Digit Med 2023** ([article](https://www.nature.com/articles/s41746-023-00784-0)) — explicitly motivated by inter-rule variability as a clinical pain point.
- **N1 remains the universally weak class** across DL models — F1 ~0.40–0.53 — mirroring the human kappa-0.24 floor ([Frontiers 2018](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2018.00781/full); [ZleepAnlystNet 2024](https://www.nature.com/articles/s41598-024-60796-y)).

### 3c. Clinical-population degradation

- **Korkalainen et al., IEEE J Biomed Health Inform 2020** ([PMID 31869808](https://pubmed.ncbi.nlm.nih.gov/31869808/)). Single-channel accuracy drops from 84.5% (κ=0.79) for non-OSA to **76.5% (κ=0.68) for severe OSA**.
- **U-Sleep pediatric evaluation, medRxiv 2024** ([article](https://www.medrxiv.org/content/10.1101/2024.08.18.24312174v1.full); [SLEEP commentary](https://academic.oup.com/sleep/article/48/7/zsaf067/8079083)). Median κ vs clinical scoring = 0.69. **κ drops 0.07–0.15 in children <2 yr** and those with comorbidities, 0.10 with sleep-disordered breathing.
- **van Gorp et al., Sleep Med Rev 2023, "Automatic sleep staging for the young and the old — Evaluating age bias"** ([article](https://www.sciencedirect.com/science/article/pii/S1389945723001260)). Pediatric PSG by adult-only model: 78.9% acc vs 88.9% with pediatric training.
- **Pediatric epilepsy**: 5-class accuracy 84.7% (κ=0.79) without epilepsy → **80.8% (κ=0.73) for drug-resistant epilepsy** ([Frontiers Neurology 2024](https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2024.1390465/full)).

### 3d. AASM revision pain

- **AASM v3, Feb 2023** ([summary PDF](https://aasm.org/wp-content/uploads/2024/02/SummaryofChanges_Document_3-1.pdf)). Mandatory by Dec 2023.
- **Rosen & Auckley, "The ethics of hypopnea scoring," JCSM 2024** ([DOI 10.5664/jcsm.10944](https://jcsm.aasm.org/doi/10.5664/jcsm.10944)). Argues v3's 1A/1B dual-criteria requirement creates an "ethical dilemma" because Medicare/Medicaid still requires 1B (4% desat) while v3 mandates 1A (3% or arousal), producing **insurance-stratified diagnoses for the same physiology**. Direct clinician-voiced pain.
- **AASM v3 OSA commentary, JCSM 2024** ([PMC11063699](https://pmc.ncbi.nlm.nih.gov/articles/PMC11063699/)).
- **EnsoData webinar on v3 implementation** ([link](https://www.ensodata.com/webinar/5-main-takeaways-from-the-aasm-scoring-manual-updates/)).

### 3e. Wearable-without-EEG: claims-vs-evidence gaps

- **Chee et al., Sleep Med 2024 / Oura Gen3 + OSSA 2.0 multi-night PSG study, n=96, 421k epochs** ([PMID 38382312](https://pubmed.ncbi.nlm.nih.gov/38382312/)). Stage accuracies 75.5% (light) – 90.6% (REM); REM sensitivity 76%.
- **Oura systematic review/meta-analysis, 2025** ([PMC12602993](https://pmc.ncbi.nlm.nih.gov/articles/PMC12602993/)).
- **Stone et al., Sleep 2021, "Performance of seven consumer sleep-tracking devices vs PSG"** ([PMC8120339](https://pmc.ncbi.nlm.nih.gov/articles/PMC8120339/)). Most devices misclassify 30–50% of REM and deep sleep.
- **Multicenter validation of 11 trackers, JMIR mHealth 2023** ([PMC10654909](https://pmc.ncbi.nlm.nih.gov/articles/PMC10654909/)). Best macro-F1 0.69, worst 0.26 across 349,114 epochs.
- **Six wrist-worn wearables stage scoring, Sleep Adv 2025** ([article](https://academic.oup.com/sleepadvances/article/6/2/zpaf021/8090472)). Systematic underestimation of wake (11.8–39.6 min).
- **Three-device validation, MDPI Sensors 2024** ([PMC11511193](https://pmc.ncbi.nlm.nih.gov/articles/PMC11511193/)).
- **Apple Watch sleep-apnea FDA 510(k) K240929, Sept 2024** ([FDA record](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K240929); [Apple whitepaper](https://www.apple.com/health/pdf/sleep-apnea/Sleep_Apnea_Notifications_on_Apple_Watch_September_2024.pdf)). FDA explicitly: "not intended to diagnose."

### 3f. REM specifically

- Modern PSG DL: REM F1 ≈ 0.90 (U-Sleep) — REM is no longer the hardest stage; **N1 is**.
- Wearables: REM remains hard. Fitbit REM sensitivity 67% ([PMC11511193](https://pmc.ncbi.nlm.nih.gov/articles/PMC11511193/)); SleepScore underestimates REM ([Stone 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8120339/)). Most devices significantly overestimate REM latency.

### 3g. Forum / practitioner signals

- **Garmin forum, "Sleep tracking — REM classified as awake?"** ([thread](https://forums.garmin.com/outdoor-recreation/outdoor-recreation/f/fenix-7-series/381113/sleep-tracking---rem-classified-as-awake)).
- **Garmin forum, "FR955 high awake, low REM"** ([thread](https://forums.garmin.com/sports-fitness/running-multisport/f/forerunner-955-series/307404/forerunner-955---sleep-tracking-high-awake-time-low-rem)).
- **Apple Community, sleep tracking accuracy iOS 16** ([thread](https://discussions.apple.com/thread/254195954)).
- **Garmin FR265 "Sleep Tracking not Accurate"** ([thread](https://forums.garmin.com/sports-fitness/running-multisport/f/forerunner-265-series/431097/sleep-tracking-not-accurate)).
- **Frontiers Comp Sci 2024 autoethnography "The sleep data looks way better than I feel"** ([article](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1258289/full)) — qualitative phenomenology of user mistrust.

### 3h. Scoring-time burden

- **42.7 s autoscore vs 4,243 s manual scoring** (Bakker et al., Sleep 2023, [JCSM 2020](https://jcsm.aasm.org/doi/full/10.5664/jcsm.8278)).
- ~1.5–2 h per study standard ([SleepScoringSolution](https://www.sleepscoringsolution.com/services/sleep-scoring-service/); [AXG Sleep Diagnostics](https://axgsleepdiagnostics.com/sleep-blog-2/sleep-study-scoring/)).
- **"Emerging challenges in the transition from manual to automated sleep scoring," SLEEP 2025** ([article](https://academic.oup.com/sleep/article/48/10/zsaf202/8209742)) — explicit position piece on this transition.

### 3i. Open-dataset caveats

- **Sleep-EDF**: only 20–78 subjects in v13, all healthy 21–35 yr Caucasian; severe class imbalance (N1 ~3%); 2 EEG channels only ([PhysioNet Sleep-EDFx](https://physionet.org/physiobank/database/sleep-edfx/)).
- **MASS** (PMID 23691200) — heterogeneous montage / channels.
- **SHHS** is older subjects, R&K-era scoring partially.

## 4. Counterfactual

If resolved, the world looks like this. (i) A clinician runs a portable HSAT or PSG, gets stage labels in seconds with calibrated uncertainty per epoch, and a flagged-for-review subset that consumes 5–10 minutes instead of 90. (ii) A pediatric sleep lab gets a stager that doesn't silently degrade on a 13-month-old. (iii) A consumer with an Oura ring sees a "we have low confidence in the stage labels last night because your HRV was abnormal" instead of a green REM bar. (iv) Researchers studying REM-fragmentation in PD or apnea no longer have stage-error variance dominate their downstream effect. The constituency cost today is real: tech-hours scoring, mis-triaged patients in pediatric and severe-OSA cases, and a population-scale epistemic-trust problem in wearables.

## 5. Feasibility sketch

- **Public datasets that bear on this**: Sleep-EDF (PhysioNet, free, small, biased), SHHS (NSRR DUA, large, older adults), MESA (NSRR DUA, multi-ethnic, includes PPG/HRV-derivable signals), MASS (CC license, heterogeneous), Dreem Open Datasets (Dreem-DOD-H/O, healthy + OSA, EEG), CAP Sleep (PhysioNet, includes pathology), HMC PSG (PhysioNet 2018), CinC Challenge 2018 datasets. **MESA + SHHS together** give EEG + ECG + actigraphy in older adults, enabling direct EEG↔cardiorespiratory comparisons.
- **Compute envelope**: GTX 1650 4 GB cannot train U-Sleep from scratch (original used multi-A100). But (a) feature-based + classical ML pipelines fit easily (HRV-spectral + RandomForest/GBM benchmarks), (b) fine-tuning a pre-trained U-Sleep checkpoint on a single subject-cohort is feasible at small batch sizes, (c) lightweight transformer/CNN variants (EfficientSleepNet, SomnoNet) exist explicitly for resource constraints. Inference on a recorded night fits comfortably.
- **Time horizon**: a meaningful experiment (e.g., quantifying calibration of a pretrained stager on a held-out clinical cohort, or comparing HRV-only staging in OSA vs healthy) is 2–8 weeks of focused work.
- **Primary risks**: NSRR DUAs require approval, weeks of admin lag. Sleep-EDF alone is too narrow to make claims about clinical populations. "Ground truth" is itself noisy — any improvement <~3% can be inside the human-rater band and unfalsifiable.

## 6. Quality-bar implications

- Held-out partition must be **subject-disjoint AND cohort-disjoint** — train on Sleep-EDF/SHHS, test on MESA / Dreem / pediatric sets. Cross-cohort generalization is the actual claim.
- Report per-stage F1 and per-stage confusion, not just accuracy — accuracy is dominated by N2 prevalence (~50%).
- Report performance stratified by **AHI band** (none / mild / moderate / severe OSA) and by age decile. Unstratified numbers hide the pain.
- **Calibration matters**: reliability diagrams or ECE per stage. A high-accuracy uncalibrated model is useless for clinical triage.
- Compare against the human-kappa ceiling (0.76 overall, 0.24 N1) explicitly — claiming "exceeds expert" requires multi-rater consensus targets, not a single-scorer label.
- Ablations: which input channels actually carry the signal (EEG-only vs EEG+EOG vs EEG+EOG+EMG vs ECG/PPG-only)? This is itself a research-relevant question.

## 7. Open questions

- Is the *useful* pain the modeling pain or the **deployment pain** (calibration, uncertainty, distribution-shift detection)? They imply different projects.
- Does anyone actually want better N1 detection, or do clinicians functionally collapse N1+N2 → "light"?
- Is consumer-wearable inaccuracy a pain *they* feel, or an academic concern? Forum threads say users feel it; vendor claims say it's solved. Need primary-source clinician interviews to disambiguate.
- Could a small project produce signal — uncertainty quantification, cohort-stratified evaluation, EEG-less staging on MESA — without retraining a foundation model?
- Does AASM v3's hypopnea controversy create demand for *event*-detection improvements rather than *stage* improvements? The two are coupled but distinct.
- How much of the wearable error is algorithmic vs sensor-noise (dry PPG, motion)? Modeling alone can't fix the latter.
