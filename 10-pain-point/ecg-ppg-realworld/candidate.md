# Candidate: ECG / PPG signal interpretation in real-world settings

Slug: `ecg-ppg-realworld`
Author: pain-point-researcher
Date: 2026-05-02

---

## 1. Pain point statement

Consumer wearables (Apple Watch, Fitbit, Samsung) and clinical patch / Holter
devices push enormous volumes of ECG and PPG data into clinical and personal
decision pipelines, but the gap between signal *detection* and trustworthy
*interpretation* remains large. False alerts (especially for atrial
fibrillation), motion-artifact corruption during exercise, demographic
performance disparities (notably skin-tone effects on PPG), the burden of
physician review of multi-day patch recordings, and over-claimed HRV-derived
"stress / readiness" metrics together produce a recurring pattern: signals
arrive, but interpretations are unreliable, opaque, or both. The cost is
borne by users (anxiety, unnecessary workups), clinicians (alert triage,
interpretation labour), and the broader healthcare system (downstream testing).

## 2. Constituency

Concretely, who feels the pain:

- **Wearable users who receive AFib / irregular-rhythm notifications** — visible
  on Apple Support discussion threads (e.g. "False arterial fibrillation
  readings on my Apple watch", "AFib alerts after watchOS update")
  [[Apple Discussions 255017393](https://discussions.apple.com/thread/255017393),
  [Apple Discussions 256065774](https://discussions.apple.com/thread/256065774)]
  and on Mayo Clinic Connect [[Apple Watch accuracy](https://connect.mayoclinic.org/discussion/apple-watch-accuracy/)].
- **General-practice and outpatient cardiology clinicians** who absorb the
  workup load from wearable-triggered visits
  [[Tandfonline overdiagnosis review](https://www.tandfonline.com/doi/full/10.1080/02813432.2026.2656694)].
- **Cardiac technicians and physicians reviewing Holter / patch recordings**
  who must interpret long recordings; described as "time-consuming and
  requires expertise" [[StatPearls — Ambulatory ECG Monitoring](https://www.ncbi.nlm.nih.gov/books/NBK597374/)].
- **Athletes / fitness users relying on HRV "readiness"** scores whose
  validity is contested
  [[Spannr essay](https://app.spannr.com/articles/hrv-wearables-gaslighting-readiness-scores),
  [JMIR Human Factors](https://humanfactors.jmir.org/2022/3/e33754)].
- **Darker-skinned users of PPG-based devices** whose signal quality is
  degraded by melanin absorption
  [[JMIR meta-analysis](https://www.jmir.org/2024/1/e62769/)].
- **ML researchers** building cardiac classifiers who report ~10% accuracy
  drop on hidden test sets
  [[PhysioNet/CinC 2020](https://iopscience.iop.org/article/10.1088/1361-6579/abc960)].

These constituencies are reachable: forum threads and DOI authors are public.

## 3. Evidence of pain

### 3a. AFib false-positive burden on consumer wearables

- **Apple Heart Study** (Perez et al., NEJM 2019): of 419,297 enrolled, 0.52%
  received irregular-pulse notifications; PPV of an irregular-pulse
  notification was 0.84 (95% CI 0.76–0.92), but only 450 of 2,161 notified
  participants returned ECG patches, so the targeted statistical precision
  for AFib yield was *not met*
  [[NEJM](https://www.nejm.org/doi/full/10.1056/NEJMoa1901183),
  [STAT critique](https://www.statnews.com/2019/03/15/apple-watch-atrial-fibrillation/)].
- **FDA De Novo DEN180042** explicitly identifies "false positive results
  leading to additional unnecessary medical procedures" as a recognised risk
  of the Apple irregular-rhythm notification feature
  [[FDA DEN180042](https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN180042.pdf)].
- **BASEL Wearable Study**: in a real-world cohort, sensitivity / specificity
  varied by device (Apple Watch 6: 85% / 75%; Samsung Galaxy Watch 3: 85% /
  75%; Fitbit Sense: 66% / 79%; Withings Scanwatch: 58% / 75%); 17–21% of
  tracings were *inconclusive*
  [[BASEL Wearable Study, JACC Adv](https://www.sciencedirect.com/science/article/pii/S2405500X22008350)].
- **Fitbit Heart Study** (Lubitz et al., Circulation 2022): PPV of irregular
  rhythm notifications for AF was ~32–34% in confirmatory ECG patch follow-up
  [[Circulation](https://www.ahajournals.org/doi/10.1161/CIRCULATIONAHA.122.060291)].
- **Cardiologist commentary**: "more than 90 percent of irregular rhythm
  alerts in younger and middle aged users will be false alarms"
  [[STAT 2019](https://www.statnews.com/2019/03/15/apple-watch-atrial-fibrillation/)].
- **Multicenter Apple Watch AF accuracy study**: sensitivity 60.0% for AF
  episodes ≥1 h vs implantable monitors
  [[PMC11694482](https://pmc.ncbi.nlm.nih.gov/articles/PMC11694482/)].

### 3b. Motion / noise artifact pain (PPG during exercise, ECG with electrode displacement)

- "PPG signals … are not robust to motion artifacts. The accuracy of PPG
  sensors during exercise is unsatisfactory"
  [[Sensors review, PMC7085621](https://pmc.ncbi.nlm.nih.gov/articles/PMC7085621/)].
- "Motion noise is reflected in the frequency domain and overlaps with the
  frequency range of … heart rate. The wide frequency range of motion
  artifacts with time-varying nature makes it difficult to use traditional
  filtering techniques for artifact removal"
  [[Springer review](https://link.springer.com/article/10.1186/s13634-020-00714-2)].
- "Even in low-motion data, there are sizeable beat-detection errors,
  implying that artifact removal alone may not guarantee accurate inter-beat
  interval and pulse-rate variability estimation"
  [[arXiv 2510.06158](https://arxiv.org/html/2510.06158v1)].

### 3c. Demographic generalization (skin tone, age, comorbidities)

- **Systematic review and meta-analysis** on skin pigmentation in pulse
  oximetry accuracy (Singh et al. 2024): "the accuracy of such devices …
  is often compromised by skin pigmentation, which attenuates the signal
  in individuals with darker skin tones." Pooled mean SpO₂ bias 1.27 %
  (dark, 95 % CI 0.58–1.95) vs 0.70 % (light, 95 % CI 0.17–1.22) — both
  exceed FDA accuracy thresholds for SpO₂ devices. The paper notes the
  difference may not be clinically relevant in typical SpO₂ ranges; the
  pain is real but the magnitude depends on saturation regime
  [[JMIR](https://www.jmir.org/2024/1/e62769/)]. *(Note: an earlier
  draft of this candidate cited specific 60–70 % saturation figures
  (3.56 ± 2.45 % vs 0.37 ± 3.20 %) attributed to this paper. Those
  numbers do not appear in Singh et al. 2024 and have been removed —
  see real-pain-critic.md major finding 2026-05-02. The pain claim
  survives on the pooled-bias figures + the secondary sources below.)*
- "Devices calibrated on individuals with medium skin pigmentation may lead
  to inaccurate readings for both lighter and darker skin pigmentation"
  [[MDPI Sensors review](https://www.mdpi.com/1424-8220/22/9/3402)].
- AFib History feature: FDA notes "performance may be reduced in patients
  who have undergone prior ablation" — a comorbidity gap
  [[FDA MDDT briefing](https://www.fda.gov/media/178230/download)].

### 3d. Holter / patch monitor review burden

- "Interpreting and analyzing extensive ECG data from Holter monitors is
  time-consuming and requires expertise" and "the potential burden on the
  clinician who must be available to review the large amount of data"
  [[StatPearls — Ambulatory ECG Monitoring](https://www.ncbi.nlm.nih.gov/books/NBK597374/)].
- iRhythm Zio's pipeline explicitly relies on a deep-learned algorithm
  *plus* Qualified Cardiac Technicians to deliver reports — implying the
  algorithm alone is not sufficient for physician-ready output, and human
  curation remains in the loop
  [[iRhythm](https://www.irhythmtech.com/us/en/solutions-services/fda-cleared-ai)].
- ICU alarm fatigue context: ventricular-tachycardia alarms are 80–90% false
  positives [[Med-Linket review](https://med-linket-corp.com/blogs/news/heart-rate-alarm-high-low-when-to-worry)] —
  not directly Holter, but evidence that low-PPV alerts in cardiac monitoring
  produce documented clinician-fatigue effects.

### 3e. HRV interpretation pain

- "HRV was weakly, although significantly, associated with perceived stress
  when measured using a wearable in naturalistic settings … of limited use
  in predicting perceived stress in the wild"
  [[JMIR Human Factors](https://humanfactors.jmir.org/2022/3/e33754)].
- "PPG devices, even those advertised and designed for research purposes,
  may pose validity concerns for HRV measurement in conditions other than
  those similar to resting states"
  [[Quality in Question, PMC11794680](https://pmc.ncbi.nlm.nih.gov/articles/PMC11794680/)].
- Critical review of ultra-short-term HRV norms: 17 of 28 reviewed studies
  did not investigate criterion validity; agreement criteria typically
  insufficient
  [[Frontiers Neurosci](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2020.594880/full)].
- "The consumer layer presents daily 'readiness' scores that pretend a
  single metric can summarize your whole body … little transparency into
  what metrics affect each device's own 'Readiness' or 'Recovery Score'"
  [[Spannr](https://app.spannr.com/articles/hrv-wearables-gaslighting-readiness-scores)].

### 3f. Forum / community signals

- Apple Discussions threads on false AFib alerts and post-update spurious
  alerts [[255017393](https://discussions.apple.com/thread/255017393),
  [256065774](https://discussions.apple.com/thread/256065774),
  [255643756](https://discussions.apple.com/thread/255643756)].
- User self-report: Apple Watch reading "10% Afib while 2 weeks on a heart
  monitor showed none" — possibly PACs misclassified as AF
  [[The AFib Clinic blog](https://www.theafibclinic.com/2019/02/my-apple-watch-told-me-i-have-afib/)].
- Mayo Clinic Connect patient discussion of accuracy / discrepancy
  [[Mayo Connect](https://connect.mayoclinic.org/discussion/apple-watch-afib-data-discrepancy/)].
- I could not directly verify specific r/AppleWatch / r/Garmin /
  r/QuantifiedSelf threads via accessible search; this is a verification gap
  (see §7).

### 3g. ML-side pain (PhysioNet / CinC, PTB-XL)

- PhysioNet/CinC 2020: "high-performing algorithms … exhibited significant
  drops (approximately 10%) in performance on hidden test data, highlighting
  a major generalization issue"
  [[CinC 2020 IOPscience](https://iopscience.iop.org/article/10.1088/1361-6579/abc960)].
- Cross-dataset cardiac signal modelling faces "the dual challenges of
  domain shift and insufficient interpretability in clinical applications"
  [[Sci Rep 2025](https://www.nature.com/articles/s41598-025-33057-9)].
- PTB-XL benchmark paper itself explicitly raises hidden stratification and
  model uncertainty concerns
  [[arXiv 2004.13701](https://arxiv.org/abs/2004.13701)].

## 4. Counterfactual

If this pain were resolved, the world looks like:

- Wearable AFib alerts come with calibrated, *user-and-context-specific*
  confidence — and with explanation traceable to morphological evidence in
  the underlying signal — so that alert-recipients and their clinicians can
  triage without a confirmatory ECG patch in most cases.
- Clinicians spend their review time on the small subset of recordings that
  carry diagnostic ambiguity, because automated review either commits with
  high evidence or *abstains explicitly*.
- HRV-derived stress / readiness scores are reported with effect-size
  bounds and known invalidation conditions (motion, short window, comorbid
  arrhythmia) instead of single-number consumer scores.
- Performance is pre-tested across skin-tone strata and reported
  publicly.

For users this means less anxiety from spurious alerts and fewer
unnecessary workups; for clinicians, less low-yield triage; for ML
researchers, a clearer benchmarking discipline.

## 5. Feasibility sketch

- **Public datasets that bear on it**:
  - PTB-XL (21,799 12-lead ECGs, 18,869 patients, public on PhysioNet)
    [[PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/)] — ECG morphology /
    rhythm classification.
  - PhysioNet/CinC 2017 (single-lead AF) and 2020/2021 (12-lead, multi-site)
    challenges — domain-generalization probe.
  - MIMIC-IV-ECG, MIT-BIH Arrhythmia Database — long-standing references.
  - PPG-DaLiA, WESAD, MAUS — PPG with motion / context, useful for HRV
    validity probes.
  - BUT-PPG / DaLiA — quality-annotated PPG for artifact work.
- **Compute envelope**: GTX 1650 4 GB (AHBU project resource constraint).
  Feasible regimes: classical ML on hand-crafted features, small 1-D CNN /
  ResNet-1D variants, pretrained-ECG embeddings (e.g. ECG-FM-style models)
  used as frozen feature extractors. 12-lead end-to-end transformer training
  is *not* feasible at this size; held-out evaluation, calibration, and
  abstention-mechanism work *is*.
- **Time horizon**: a focused contribution (e.g. a held-out evaluation
  protocol with abstention and skin-tone stratification, on PTB-XL plus a
  PPG corpus) is on the order of weeks-to-months for a single researcher.
- **Primary risks**:
  1. Pain is broad — risk of producing a thin pass over many sub-pains
     instead of one credible contribution.
  2. The most painful sub-pain (alert triage in real consumer settings) is
     hardest to ground in public data because the consumer-grade alerting
     pipelines (Apple, Fitbit) are closed.
  3. Skin-tone-stratified evaluation is bottlenecked by the absence of
     skin-tone labels in most public ECG/PPG corpora.

## 6. Quality-bar implications

For honest evaluation of work in this space:

- **Held-out partition** must be patient-disjoint *and* ideally
  site-disjoint (PTB-XL provides site/recording metadata; PhysioNet/CinC
  2020 provides multi-site held-out).
- **Stratified reporting**: by age band, sex, and — where labels exist —
  skin-tone proxy / Fitzpatrick scale; explicit "could-not-stratify" notes
  where labels are missing.
- **Calibration metrics** (Brier score, expected calibration error, PPV at
  fixed alert rate) reported in addition to AUROC, because the consumer
  pain is *PPV at low prevalence*, not raw discrimination.
- **Abstention is a first-class output**: report the rate and behaviour of
  "inconclusive" / refused predictions, mirroring the BASEL inconclusive
  rate of 17–21%.
- **Ablations**:
  - With / without motion / quality gating.
  - With / without per-site domain-adaptation.
  - With / without abstention.
- **Negative results published**: where calibration fails or stratified gap
  is large, that is the contribution.

## 7. Open questions

1. **Forum verification gap**: I could not directly verify specific Reddit
   thread URLs (r/AppleWatch, r/Garmin, r/QuantifiedSelf) within this
   research pass. The pain is plausible from adjacent evidence (Apple
   Discussions, blog posts, clinician commentary) but Reddit-thread
   citations should be confirmed before relying on them.
2. **Magnitude of clinician downstream burden**: the Tandfonline overdiagnosis
   piece and clinician-anecdote sources suggest "one to several
   wearable-related arrhythmia visits per week" but a *quantified* burden
   estimate per practice / per region is missing in what I located.
3. **Skin-tone disparity in ECG (not PPG)**: well-documented for
   pulse-oximetry / PPG; less clearly characterised for ECG morphology
   classifiers. This may not be a pain at all in ECG, or it may be hidden.
   Worth a focused probe before claiming.
4. **Which sub-pain is "the" pain?** False-positive burden, motion-artifact
   in PPG, and HRV over-claim are *related but separable*. A scoping
   decision is required at Layer 00 before this candidate becomes a
   project. I have deliberately not narrowed.
5. **Consumer-pipeline opacity**: the Apple / Fitbit alerting algorithms are
   closed; a contribution that improves them in principle may not be
   adoptable in practice. Need to identify whether the target is
   open-source / clinician-facing / patch-vendor-facing rather than
   consumer-OEM-facing.
6. **NeuroKit2 / OSS issue-tracker pain**: I confirmed NeuroKit2 maintains
   active PPG/ECG quality and artifact code paths, but did *not* directly
   inspect open issues for recurring artifact / quality complaints
   [[NeuroKit2 docs](https://neuropsychology.github.io/NeuroKit/functions/ppg.html)].
   A direct GitHub issue-tracker pass is a follow-up.

---

### What I could not verify in this pass

- Specific Reddit thread URLs and their content for r/AppleWatch, r/Garmin,
  r/QuantifiedSelf.
- Direct cardiologist quotes from clinical interviews (relied on STAT News
  reportage for clinician-voice evidence).
- Quantitative clinician-burden numbers (visits per week, hours per
  recording at scale).
- Open-issue-tracker pain in NeuroKit2 / BioSPPy / py-ecg-detectors —
  documentation reviewed; issues themselves not exhaustively read.

---

## Gap-closing 2026-05-02

*Author: pain-point-researcher (retry pass). Closes three gaps flagged in
critic-shortlist.md.*

---

### Gap 1 — Skin-tone label availability in public PPG/ECG corpora

**Verdict: partial**

Every named corpus in §5 was checked for Fitzpatrick skin-type or equivalent
pigmentation labels. Findings per dataset:

| Dataset | Demographic metadata present | Skin-tone / pigmentation label |
|---|---|---|
| PPG-DaLiA (Reiss et al. 2019) | age range 21–55, sex (8F/7M) | None |
| BUT-PPG (Brno UT, 2021; PMID 34532501) | age range 21–61, sex (6F/6M) | None |
| WESAD (Schmidt et al. 2018; ACM ICMI) | age mean 27.5 ± 2.4 yr, sex (12M/3F) | None |
| MAUS | could not verify published demographic table | Not mentioned in any source found |
| BIDMC PPG & Respiration (PhysioNet) | ICU patients; clinical record fields | No pigmentation field documented |
| MIMIC-PERform-Apnea (PhysioNet) | age, sex from MIMIC-III clinical | No pigmentation field |

One exception exists: **MIMIC PERform Ethnicity** — a purpose-built
sub-corpus derived from the MIMIC-III Waveform Matched Subset by Peter
Charlton's group, containing 200 subjects (100 Black, 100 White adults),
10-minute PPG + ECG + respiration at 125 Hz, available via PhysioNet
[[ppg-beats docs](https://ppg-beats.readthedocs.io/en/stable/datasets/mimic_perform_ethnicity/)].
This is the only public PPG corpus found with a race/ethnicity split that
could proxy for skin-tone-stratified evaluation.

**Critical caveat**: MIMIC PERform Ethnicity uses self-reported race
(Black / White binary from MIMIC-III clinical fields) extracted from ICU
records — not Fitzpatrick scale, ITA melanin index, or any direct pigmentation
measurement. It is a blunt proxy: race is socially assigned, not a
physiological pigmentation measurement, and the binary split excludes Brown,
Asian, and Hispanic populations entirely. Sample size per stratum is 100,
which is marginal for subgroup inference. The dataset is ICU-derived (supine,
controlled lighting) and may not represent ambulatory consumer-wearable
conditions.

**Consequence for scope**: the prior formulation "skin-tone-stratified PPG
eval" in the selection shortlist cannot be delivered at the granularity
implied. What is actually achievable on public data: a Black/White two-group
comparison on MIMIC PERform Ethnicity (ICU PPG only, blunt proxy, n=100/group).
A Fitzpatrick-scale-stratified evaluation would require either (a) prospective
data collection with pigmentation measurement, or (b) a dataset such as the
2025 Garmin study (Frontiers Digital Health, DOI 10.3389/fdgth.2025.1553565)
that explicitly used Fitzpatrick scale on n=21 subjects — too small for a
credible ML benchmark. The shortlist framing must be narrowed or the
infeasibility stated explicitly.

**Sources**: PMID 34532501 (BUT-PPG); ACM ICMI 2018 doi:10.1145/3242969.3242985
(WESAD); UCI ML Repo PPG-DaLiA (archive.ics.uci.edu/dataset/495); ppg-beats
readthedocs (MIMIC PERform Ethnicity); Frontiers Digit Health
doi:10.3389/fdgth.2025.1553565 (Garmin/Fitzpatrick study).

---

### Gap 2 — Selective-classification / abstention novelty on ECG/PPG

**Verdict: partial — the "abstention angle distinctive" claim is partially
refuted; a narrower novelty claim is still defensible.**

The critic was right to flag this. The literature is not empty.

**What already exists:**

1. **Uncertainty estimation for automated 12-lead ECG analysis** — Smole et
   al. (2023, PMC9707930): 526,656 ECGs across three datasets (UMCU-Triage,
   UMCU-Diagnose, CPSC2018); six epistemic/aleatoric methods compared; clinical
   simulation shows accuracy increases as uncertain predictions are referred to
   physicians (excluding 25% of uncertain cases achieves 98% accuracy on
   UMCU-Diagnose). The paper recommends uncertainty estimation as prerequisite
   for clinical deployment. This is a direct predecessor — reject-option for
   ECG classification is *not* novel as a concept.

2. **Cardiac arrhythmia classification with rejection** — Neural Computing and
   Applications 2024 (doi:10.1007/s00521-023-09267-5): Monte Carlo dropout
   on a DNN; predictions above an uncertainty threshold are held for clinician
   review; evaluates on a named arrhythmia ECG corpus. This is explicitly the
   "abstention on ECG" framing.

3. **Uncertainty quantification in multi-label ECG classification** — Barandas
   et al. (Information Fusion 101, 2024, doi:10.1016/j.inffus.2023.101978):
   five UQ methods on the same DNN architecture, evaluated including a
   classification-with-rejection-option experiment, using a multi-label ECG
   dataset. Finds that incorporating uncertainty with rejection improves ability
   to detect dataset shift.

4. **PTB-XL benchmark (Strodthoff et al., arXiv 2004.13701, IEEE JBHI 2021)**:
   explicitly discusses "hidden stratification" and "model uncertainty" as
   connecting points for future research; does not itself implement abstention,
   but names the gap.

5. **UCTECG-Net (arXiv 2602.16216, 2026)**: uncertainty-aware convolution-
   transformer on PTB Diagnostic ECG + MIT-BIH; integrates Monte Carlo
   Dropout, Deep Ensembles, and Ensemble MC Dropout; achieves 99.14% accuracy
   with uncertainty reporting.

**What the literature does NOT yet deliver:**

- No paper found that evaluates calibrated abstention on **PTB-XL specifically**
  with a PPV-at-fixed-alert-rate framing tuned to the consumer-wearable AFib
  false-positive problem. The existing work focuses on accuracy-under-rejection
  curves but not on the clinically motivated metric (PPV at a
  cardiologist-acceptable false-positive rate, or PPV matched to the 17–21%
  BASEL inconclusive rate).
- No work found that combines ECG/PPG abstention with **cross-dataset
  evaluation** (training on PTB-XL, abstaining on PhysioNet/CinC 2020 or
  MIMIC-IV-ECG held-out). The domain-shift dimension of abstention is
  unaddressed.
- Conformal-prediction coverage guarantees on ECG (distribution-free bounds on
  miscoverage) are not yet applied to AFib detection on PTB-XL as of this
  search. The general conformal + selective classification framework (arXiv
  2512.12844) exists but has not been instantiated on cardiac signals.

**Revised novelty claim**: the abstention angle is *not distinctive* as a
generic concept. It is partially distinctive if scoped specifically to:
(a) PTB-XL multi-label AFib classification with PPV-at-fixed-alert-rate as
the primary metric, (b) cross-dataset abstention under distribution shift, or
(c) conformal coverage guarantees on wearable-grade single-lead ECG. Without
at least one of these sharpenings, "calibrated abstention for AFib alerts on
PTB-XL" does not constitute a sufficient novelty claim.

**Sources**: PMC9707930 (Smole et al. 2023); doi:10.1007/s00521-023-09267-5
(NCA 2024 rejection paper); doi:10.1016/j.inffus.2023.101978 (Barandas 2024);
arXiv:2004.13701 (Strodthoff/PTB-XL 2021); arXiv:2602.16216 (UCTECG-Net);
arXiv:2512.12844 (Selective Conformal Risk Control, general).

---

### Gap 3 — Constituency reachability

**Verdict: partial — quantified study found; no direct practitioner interview
obtained.**

**What was found:**

A published retrospective propensity-matched cohort study (JAHA 2024,
doi:10.1161/JAHA.123.033750) directly quantifies the clinical burden of
wearable use on AF patients at an outpatient electrophysiology clinic (n=172
patients; 83 wearable users vs 89 non-users; December 2022 – February 2023):

- AF-specific healthcare use: wearable users mean 4.05 (95% CI 2.91–5.18)
  vs non-users mean 2.70 (95% CI 1.99–3.41); P = 0.04.
- AF-specific outpatient cardiology/primary-care visits: users 2.04 (95% CI
  1.51–2.56) vs non-users 1.33 (95% CI 1.01–1.65); P = 0.02.
- Rhythm-related diagnostic tests and procedures: users 1.84 vs non-users
  1.00; P = 0.004.
- 20% of wearable users reported anxiety and "always contacted their doctors"
  in response to irregular rhythm notifications.

This closes the §7 Q2 gap (quantified burden estimate) that the original
candidate explicitly flagged as missing. The JAHA 2024 study is a primary
source, not secondary citation.

A JMIR Cardio 2023 targeted literature review (doi:10.2196/47292) found:
69% of clinicians expressed concern about data overload from wearable
notifications; 53% manually uploaded wearable recordings to patient records;
15.5% used external platforms — suggesting significant manual processing burden
without automated triage.

**What was not obtained:**

- A direct practitioner quote from a GitHub issue, forum post, or interview in
  this pass. The NeuroKit2 GitHub issue tracker was checked: one open issue
  (#1115, June 2025, marked "wontfix") requests PPG amplitude artifact
  detection with concrete description of systolic and baseline artifacts
  corrupting HRV analysis. This is the only open practitioner complaint found
  in the NeuroKit2 tracker; it confirms the artifact pain is felt by at least
  one practitioner/researcher but is marked as not accepted by maintainers,
  which is itself a signal that the OSS tooling considers it out of scope.
  [[NeuroKit2 issue #1115](https://github.com/neuropsychology/NeuroKit/issues/1115)]
- No py-ecg-detectors or BioSPPy issues with clear practitioner pain quotes
  were found in this pass. Issues found in py-ecg-detectors (issues #3, #13)
  are from 2019–2020 and concern installation bugs, not signal quality.

**Net assessment**: constituency reachability for the *clinician burden*
sub-pain is now supported by a quantified primary study. Reachability for the
*OSS practitioner* constituency is confirmed at minimum (one open NeuroKit2
issue) but a richer signal was not found in this pass.

**Sources**: doi:10.1161/JAHA.123.033750 (JAHA 2024 wearable/AFib visits);
doi:10.2196/47292 (JMIR Cardio 2023 literature review); NeuroKit2 GitHub
issue #1115 (https://github.com/neuropsychology/NeuroKit/issues/1115).

---

### Summary of gap verdicts

| Gap | Verdict | Key implication |
|---|---|---|
| Gap 1 — Skin-tone labels in public PPG/ECG corpora | **partial** | Only MIMIC PERform Ethnicity provides a race proxy (Black/White, n=100/100, ICU); no Fitzpatrick-scale PPG dataset at usable scale exists. The "skin-tone-stratified eval" framing must be narrowed to a Black/White comparison with explicit proxy-label caveat, or dropped as a primary scope. |
| Gap 2 — Selective-classification / abstention novelty | **partial** | Abstention on ECG is not novel generically (3+ papers since 2023). A novelty claim requires specific scoping to PTB-XL + PPV-at-fixed-alert-rate, or cross-dataset abstention under distribution shift, or conformal coverage guarantees on single-lead wearable ECG — none of which has been published. |
| Gap 3 — Constituency reachability | **partial** | JAHA 2024 provides quantified clinician-burden numbers (primary study, P=0.004). NeuroKit2 issue #1115 confirms practitioner artifact pain in OSS tooling. No direct interview or forum thread quote obtained. |
