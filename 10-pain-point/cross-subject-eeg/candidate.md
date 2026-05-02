# Candidate: Cross-Subject Generalization in EEG-Based Decoding

*Investigated 2026-05-02 by `pain-point-researcher`. Broad-exploration phase: surfacing evidence, not arguing for adoption.*

## 1. Pain-point statement

EEG-based decoders (motor imagery, P300, SSVEP, affective state, sleep staging, cognitive load) generalize poorly across subjects. A model trained on N participants typically loses substantial accuracy when applied to a new participant without per-user calibration data, and a non-trivial fraction of users ("BCI illiterate") cannot be calibrated to acceptable accuracy at all. Practitioners therefore pay a recurring tax: 20–30 minutes of subject-specific data collection per new user per session, fragile to electrode replacement, hair, mood, and time of day. Recent self-supervised "foundation" models claim to narrow the gap but independent benchmark and review work suggests the universality has not been convincingly demonstrated.

## 2. Constituency

Concretely (not "the field"):

- **Academic BCI labs** running motor-imagery / P300 / SSVEP studies who must schedule a calibration block at the top of every session (e.g., MOABB users, BCI Competition participants, braindecode users).
- **Clinical sleep-staging teams** validating a model trained on Sleep-EDF or SHHS against a new cohort with different montages.
- **Consumer neurotech companies and their users** — Emotiv (training profiles per user), Neurable (their FAQ states the headphones need "a few hours of recorded sessions" to learn a user's brain patterns), OpenBCI hobbyists.
- **EEG-foundation-model authors and downstream users** evaluating LaBraM / BENDR / EEGPT / BIOT on cross-subject transfer.
- **EEG Foundation Challenge 2025 organizers and entrants** — an explicit constituency that has named cross-subject-and-cross-task generalization as the headline target.

## 3. Evidence of pain

### 3a. The calibration burden is real and quantified in the literature

- **Calibration time of 20–30 minutes per new user is the de facto baseline.** Wu et al., *A Review on Signal Processing Approaches to Reduce Calibration Time in EEG-Based Brain–Computer Interface*, Sensors 2021, PMC8417074: "[the] time-consuming calibration process is necessary due to high inter-subject variabilities of EEG signals, which is costly and tedious and hinders the further expansion of MI-based BCIs outside of the laboratory" — and survey work in the area cites calibration of "approximately 20–30 minutes" as standard. https://pmc.ncbi.nlm.nih.gov/articles/PMC8417074/

- **BCI illiteracy: 15–30 % of users cannot reach the standard 70 % control threshold.** Saha & Baumert, *Intra- and Inter-subject Variability in EEG-Based Sensorimotor BCI: A Review*, Frontiers in Computational Neuroscience 2020: "Around 15–30 % users are inherently unable to produce task-specific signature robust enough to control a BCI." A separate review (Zhang et al., *Subject inefficiency phenomenon of motor imagery BCI*, 2020, https://journals.sagepub.com/doi/10.26599/BSA.2020.9050021) reports the inefficient-subject share at 10–50 %, defined as failure to reach >70 % accuracy after sufficient training. https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2019.00087/full

### 3b. Cross-subject vs within-subject performance gap on canonical benchmarks

- **MOABB benchmark (Chevallier et al., arXiv:2404.15319, 2024) deliberately reports only within-session results and explicitly punts on cross-subject** — quote: "this paper focuses on the most common evaluation strategy in the literature, which is within-session evaluation … cross-subject approaches involve complex questions about transfer learning and subject alignment that were outside the scope of this article." The largest open BCI reproducibility study to date sidestepped cross-subject because it is harder and unsettled. https://arxiv.org/abs/2404.15319 and https://moabb.neurotechx.com/docs/paper_results.html

- **BCI Competition IV-2a LOSO numbers cluster well below within-subject ceiling.** Reported recent LOSO accuracies: CTNet 58.64 %, CCST (Compact Conv. Swin Transformer) 68.27 %, EEGCCT 70.12 %, ConvoReleNet 72.22 % rising to 79.44 % only after transfer-learning fine-tuning. Within-subject SOTA for the same dataset commonly reaches 85 %+ (CIACNet 85.15 %, MS-AFM 86.03 %). The practical gap is on the order of 10–25 absolute percentage points. Sources: Nature Sci Reports 2024 https://www.nature.com/articles/s41598-024-73755-4 ; https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1622847/full ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11841462/

- **Sleep staging cross-dataset performance also drops.** Cross-dataset validation between Sleep-EDF and SHHS "displayed lower performance compared to the original condition" until models were retrained on a randomized SHHS dataset, attributed to "different recording equipment, acquisition criteria, and montage variations". https://www.nature.com/articles/s41598-024-60796-y

- **TCPL (Frontiers in Neuroscience 2025) few-shot cross-subject MI results show the calibration cost curve concretely:** 1-shot 65.3 ± 2.4 %, 5-shot 74.8 ± 1.8 %, 10-shot 80.6 ± 1.7 %, 20-shot 83.1 ± 1.5 %. An 18-point spread between 1-shot and 20-shot, on the same model, says calibration data is still load-bearing even in modern few-shot pipelines. https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2025.1689286/full

### 3c. The foundation-model "we solved it" narrative is contested

- **EEG Foundation Models: A Critical Review (arXiv:2507.11783, 2025)** examines BrainBERT, Neuro-GPT, Brant, BIOT, EEGFormer, LaBraM, Mentality, NeuroLM, FoME, BrainWave. Key quotes:
  - "The universality and robustness of EEG-FMs have not been convincingly demonstrated in most studies."
  - "Empirical evidence of scaling in EEG-FMs has been either weak, limited, or inconclusive."
  - "Linear probing performance frequently underperformed supervised baselines."
  - 4 of 10 surveyed models evaluated on data already used during pre-training (pre-training/eval leakage).
  - Despite vastly different pre-training data sizes, TUAB AUC clusters in 0.86–0.92 and TUEV F1 in 0.70–0.83 — adding data does not reliably improve downstream accuracy.
  https://arxiv.org/html/2507.11783v3
- **EEG-FM-Bench (arXiv:2508.17742, 2025)** flags that subject-dependent splits "lead to artificially inflated metrics that do not reflect generalizability" and finds that "compact architectures with domain-specific inductive biases consistently outperform significantly larger models" — i.e., scale alone is not closing the cross-subject gap. https://arxiv.org/abs/2508.17742
- **EEG Foundation Challenge 2025 (arXiv:2506.19141)** explicitly states: "no existing benchmarks or datasets have been developed to address [cross-subject, cross-task] issues" and frames Challenge 1 as "zero-shot generalization across both novel tasks and novel subjects." Independent confirmation that the gap is open. https://arxiv.org/html/2506.19141v1
- **LaBraM (ICLR 2024 spotlight, arXiv:2405.18765)** itself reports cross-subject gains as 8–13 absolute accuracy points over prior encoders on a children's empathy task — a meaningful but moderate improvement, not a closure. https://arxiv.org/abs/2405.18765

### 3d. Industry signals: consumer BCIs require per-user setup or rolling personalization

- **Emotiv** uses per-user "training profiles" tied to EmotivID, separate per headset model. From Emotiv's own docs: "Training data sets for mental commands and facial expressions are stored in training profiles … each headset type with different EEG channels will have different training data sets, then different training profiles." https://emotiv.gitbook.io/emotivbci/training-profiles/your-training-profiles
- **Neurable MW75 Neuro** FAQ: "over the first few hours of use, the algorithm continues to personalize itself based on your unique brain signals … We have found that your age and left vs. right hand preference are the biggest factors that can cause variations in brainwaves … it can take the headphones a few hours of recorded sessions to learn what your brain patterns are like." Even a flagship dry-electrode consumer product builds in a multi-hour personalization tail. https://www.neurable.com/faqs
- **OpenBCI forum** threads document recurring user pain around setup, electrode quality, hair, and reference-electrode reliability, all of which drive subject-to-subject signal-distribution shift before the modeling problem even begins. Examples: "Improving Signal Quality with Dry Electrodes" https://openbci.com/forum/index.php?p=/discussion/2564/improving-signal-quality-with-dry-electrodes ; "Signal Quality Difference between Cyton and Ganglion" https://openbci.com/forum/index.php?p=/discussion/1533/

### 3e. Anatomical / physical floor on how far software alone can close the gap

- Inter-subject variability is not just a learning problem. Skull thickness, scalp-to-cortex distance, tissue conductivity and cortical folding "systematically contribute to inter-subject differences in feature magnitude and topography." See *Inter- and Intra-Subject Variability in EEG: A Systematic Survey*, arXiv:2602.01019. https://arxiv.org/abs/2602.01019 (could not independently verify the publication venue beyond arXiv listing, flagged.)

### 3f. Counter-evidence (the pain may be partly resolved or smaller than commonly stated)

- **Foundation models are improving cross-subject scores even if they have not "closed" the gap.** LaBraM's 8–13 point gains and BENDR's claim that "a single pre-trained model is capable of modeling completely novel raw EEG sequences recorded with differing hardware, and different subjects" both indicate measurable progress. https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.653659/full
- **Riemannian / covariance methods on MOABB are quite robust** without massive subject data, suggesting the perceived crisis in some sub-paradigms (e.g., P300 with Riemannian features) may be overstated relative to motor imagery. (MOABB paper, Chevallier et al. 2024.)
- **Consumer wearables ship.** Muse and Neurable are commercial products with users — the calibration tax has not killed the category, suggesting the pain is felt but tolerable, especially when reframed as "personalization" rather than "calibration."
- **Some sleep-staging models cross-validate adequately** when trained on diverse data (per ZleepAnlystNet). The bottleneck there may be data diversity more than an irreducible inter-subject gap.

## 4. Counterfactual

If cross-subject generalization were genuinely solved at the level of, say, 90 % within-subject parity with zero calibration trials:

- Clinicians could deploy a pre-trained sleep-staging or seizure-detection model to a new patient out-of-the-box, removing per-patient validation friction.
- Consumer BCI products could ship as truly plug-and-play (Muse-style biofeedback, Neurable-style focus tracking, motor-imagery game controllers) — removing the multi-hour personalization tail.
- BCI labs could drop the standard 20–30 min calibration block, multiplying participant throughput and enabling longitudinal / large-N studies that are presently logistically prohibitive.
- The 15–30 % BCI-illiterate population would either shrink (the model finds signal where simpler decoders couldn't) or be cleanly identified up-front so they aren't enrolled in interventions that won't work for them.

What matters to the constituency: throughput (labs), deployability (clinicians and product teams), and the user-facing promise that the device works on day one (consumers).

## 5. Feasibility sketch

- **Public datasets that bear directly on this:**
  - MOABB (14 motor imagery, 15 P300, 7 SSVEP datasets aggregated; LOSO supported). https://github.com/NeuroTechX/moabb
  - BCI Competition IV-2a / 2b (canonical MI benchmark, 9 subjects). https://www.bbci.de/competition/iv/
  - Sleep-EDF, SHHS (sleep staging cross-cohort). https://physionet.org/
  - TUAB / TUEV (clinical EEG, used by every EEG foundation model).
  - EEG Foundation Challenge 2025 dataset (≈3,000 subjects, 6 tasks). https://arxiv.org/html/2506.19141v1
  - LaBraM pre-training corpus (≈2,500 hours, ~20 datasets).
- **Compute envelope:** within reach of a single-GPU lab for fine-tuning / probing existing foundation checkpoints (LaBraM, EEGPT, BENDR, BIOT are all open-weights). Pre-training a new foundation model from scratch is a multi-GPU month-scale endeavor and probably out of scope.
- **Time horizon:** evaluation / honest benchmarking work is weeks-to-months. A genuine architectural / methodological contribution is 6–12 months.
- **Primary risks:**
  1. The gap may be bounded below by anatomy and electrode physics, not algorithm — software wins capped.
  2. Consumer industry may have already absorbed the pain via on-device personalization, reducing market-pull urgency.
  3. Foundation-model space is crowded and moving fast; risk of being scooped or rendered obsolete by a NeurIPS-cycle release.
  4. Evaluation hygiene is genuinely difficult — many published "cross-subject" claims leak via overlapping datasets between pre-training and probe (per arXiv:2507.11783); a contribution that *only* tightens evaluation may be valuable but unglamorous.

## 6. Quality-bar implications (how honest evaluation must work)

- **Held-out partition must be subject-disjoint AND dataset-disjoint AND ideally hardware-disjoint.** Per EEG-FM-Bench, subject-dependent splits inflate metrics. Pre-training corpus must not overlap with downstream evaluation set.
- **Report both zero-shot and 1/5/10/20-shot cross-subject numbers**, not just "best." The TCPL curve shows an 18-pt 1-shot→20-shot spread that gets hidden if you only report a single number.
- **Compare against strong within-subject and Riemannian baselines.** Riemannian methods are MOABB's strongest within-session learners; if your foundation model can't beat covariance + MDM cross-subject, that's load-bearing.
- **Report per-subject distributions, not just means** — the BCI illiteracy phenomenon means a 75 % mean can hide a bimodal distribution where 30 % of users are at chance.
- **Ablations that matter:** subject-adversarial training, electrode-dropout robustness, montage-mismatch robustness, session-gap (test trials recorded weeks after train trials), pre-training-data-overlap audit.

## 7. Open questions

- What is the *anatomical/physical* floor on cross-subject parity? Has any work decomposed the gap into "fixable by software" vs "fixable only by per-user impedance/anatomy modeling"?
- Is the calibration tax actually felt as pain by end users, or have consumer companies (Neurable, Muse) successfully reframed it as benign "personalization"? Need direct user-research evidence — could not find primary-source forum quotes within this pass.
- Does sleep staging share the same problem at the same magnitude as motor imagery, or is it materially easier (longer epochs, slower dynamics, less reliance on user-specific motor cortex topography)?
- Are the foundation-model gains *additive* with classical Riemannian features, or do they cannibalize the same signal? EEG-FM-Bench's "compact + inductive bias beats large" finding suggests the latter.
- How representative are TUAB / TUEV of the cross-subject problem, given they are heavily used and arguably saturated?
- Could not verify: a clean, recent r/BCI thread quote where a practitioner explicitly describes the calibration burden as their #1 frustration. Forum search returned no direct hits via web search; would require manual Reddit browsing to confirm.

---

## Constituency contact-paths (for follow-up validation)

- MOABB maintainers: https://github.com/NeuroTechX/moabb (issues, discussions)
- braindecode maintainers: https://github.com/braindecode/braindecode
- EEG Foundation Challenge 2025 organizers: contacts listed in arXiv:2506.19141
- LaBraM authors: https://github.com/935963004/LaBraM
- OpenBCI forum: https://openbci.com/forum/
- r/BCI subreddit
- Neurable / Emotiv support / FAQ teams (consumer-side perspective)

---

## Gap-closing 2026-05-02

*Authored by `pain-point-researcher`. Addresses the two verification gaps flagged in `critic-shortlist.md` (critical finding: premature deferral on "redundancy" grounds).*

---

### Gap 1 — EEG-FM-Bench scope vs candidate §6

**Research method.** Read the full HTML rendering of arXiv:2508.17742v1 and v2, the GitHub repository (xw1216/EEG-FM-Bench), and a third-party literature review of the paper. Also examined a separate benchmark (Dingkun0817/EEG-FM-Benchmark) that appeared in the same search space. Findings below use v2 as the authoritative version (same conclusions confirmed in v1).

**What EEG-FM-Bench (arXiv:2508.17742) actually does.**

EEG-FM-Bench integrates 14 datasets across 10 paradigms and evaluates 7 EEG foundation models (BIOT, BENDR, LaBraM, EEGPT, CBraMod, plus 2 general time-series models) under standardized fine-tuning protocols. It enforces subject-independent train/validation/test splits for most datasets and reports mean ± standard deviation across 5 independent random-seed runs. It explicitly flags that subject-dependent splits "lead to artificially inflated metrics that do not reflect generalizability." Its main positive finding is that "compact architectures with domain-specific inductive biases consistently outperform significantly larger models."

**Sub-question verdicts.**

**(a) Subject-disjoint AND dataset-disjoint AND hardware-disjoint splits simultaneously?**

OPEN. EEG-FM-Bench enforces subject-independent splits within each dataset. It does not evaluate across datasets in a disjoint manner (each of the 14 datasets is a separate evaluation task, not a hold-out from a cross-dataset pool). Hardware heterogeneity is not mentioned; the dataset table reports paradigm, channels, and epoch duration but not hardware manufacturer or EEG amplifier model. The candidate's §6 requirement — held-out partition simultaneously subject-disjoint AND dataset-disjoint AND hardware-disjoint — is not delivered. Exact paper text: "Datasets are partitioned into three splits using a subject-independent strategy while preserving label distribution. For emotion recognition, a subject-dependent strategy aligns with common protocols." (arXiv:2508.17742v2, Section on data processing.) Note: for SEED, SEED-V, and SEED-VII, a subject-*dependent* strategy is used, which the candidate's §6 specifically warns against.

**(b) 0/1/5/20-shot calibration curves per subject?**

OPEN. No few-shot or k-shot experiments appear anywhere in the paper. The benchmark implements three fine-tuning strategies (frozen backbone, full-parameter single-task, full-parameter multi-task) applied at the level of entire datasets, not per-subject shot counts. The TCPL calibration curve cited in §3b (1-shot 65.3 % → 20-shot 83.1 %) is from an entirely different paper. The candidate's §6 requirement to "report both zero-shot and 1/5/10/20-shot cross-subject numbers" is unaddressed by EEG-FM-Bench.

**(c) Per-subject performance distributions (not averages)?**

OPEN. The paper reports only aggregate mean ± SD across 5 random seeds — not per-subject distributions, not boxplots over subjects, not the tail-end performance of "BCI illiterate" subjects. The candidate's §6 requirement to "report per-subject distributions, not just means" is unaddressed. This matters because (per §3a) 15–30 % of subjects may be at chance, and aggregate averages hide that bimodal structure entirely.

**(d) Pre-training-overlap audit?**

OPEN. EEG-FM-Bench makes no attempt to determine whether any of the 7 evaluated foundation models pre-trained on the downstream datasets. This is precisely the leakage problem that arXiv:2507.11783 (the Critical Review) found in 4 of 10 surveyed models. EEG-FM-Bench inherited this gap rather than closing it. The candidate's §6 requirement for a "pre-training-data-overlap audit" is entirely unaddressed.

**(e) Riemannian / classical-ML baselines under the same splits?**

OPEN. EEG-FM-Bench compares only neural foundation models and general time-series neural models. No classical baselines (SVM, LDA, MDM, FgMDM, TSLDA, or any Riemannian geometry method) are included. The candidate's §6 requirement to "compare against strong within-subject and Riemannian baselines" is unaddressed.

**Note on a second benchmark.** A separate repository (Dingkun0817/EEG-FM-Benchmark, arXiv not identified) evaluates 12 open-source EEG foundation models across 13 datasets / 9 BCI paradigms and does implement within-subject few-shot evaluation ("fine-tuning data volume approximately 1/20 ~ 1/100 of that typically used in LOSO protocols") alongside LOSO cross-subject evaluation. It also claims to include "traditional machine learning, CNN-based, and Transformer-based models trained from scratch" as baselines, but it is unclear whether "traditional ML" includes Riemannian methods specifically. It does not appear to include a pre-training-overlap audit or per-subject distributions. This benchmark partially addresses sub-questions (b) and (e), but is not what the shortlist cited (the shortlist cited arXiv:2508.17742 = xw1216/EEG-FM-Bench), and its classical-ML baseline scope remains ambiguous. Even if it addresses (b) and (e) partially, it does not close (a), (c), or (d).

**Overall verdict — Gap 1: OPEN.**

Of the five sub-requirements in candidate §6 that the critic's deferral assumed "EEG-FM-Bench already partly addressed," the primary cited benchmark (arXiv:2508.17742) addresses zero of them. The benchmark correctly names the subject-dependent-split inflation problem and enforces subject-independent splits — but that is the starting-line requirement the candidate already took as given, not the candidate's distinctive contribution. The shortlist's deferral rested on a conflation of "field has named the gap" with "field has filled the gap." The critic was correct. All five sub-requirements remain open research contributions as of May 2026.

Sources: arXiv:2508.17742v1 https://arxiv.org/html/2508.17742v1 ; arXiv:2508.17742v2 https://arxiv.org/html/2508.17742v2 ; GitHub xw1216/EEG-FM-Bench https://github.com/xw1216/EEG-FM-Bench ; GitHub Dingkun0817/EEG-FM-Benchmark https://github.com/Dingkun0817/EEG-FM-Benchmark ; moonlight.io review https://www.themoonlight.io/en/review/eeg-fm-bench-a-comprehensive-benchmark-for-the-systematic-evaluation-of-eeg-foundation-models

---

### Gap 2 — EEG Foundation Challenge 2025 dataset access

**Clarification on naming.** The candidate file (§2, §3c, §5, §7) refers to the "EEG Foundation Challenge 2025" (arXiv:2506.19141). There is no separate entity named "BCI Foundation Challenge 2025" discoverable via web search; no hits returned for that exact phrase pointing to a distinct competition. The candidate's naming is a minor imprecision; it refers to the NeurIPS 2025 EEG Foundation Challenge.

**What was found.**

*Competition status (as of May 2026).* The competition concluded November 2, 2025, with a workshop session at NeurIPS December 6–7, 2025. The challenge website confirms: "The final results are out!" Winners were the Computational Neuroscience Lab, KU Leuven. 1,183 teams participated with more than 8,000 submissions. Sources: https://eeg2025.github.io/eeg2025.github.io/ ; https://neurips.cc/virtual/2025/competition/127719 ; https://neurips.cc/virtual/2025/136311

*Training and validation data (HBN Releases 1–11, excluding Release 5; validation = Release 5).* Freely available under CC-BY-SA-4.0 license via NEMAR (nemar.org) and Amazon S3 without a formal Data Use Agreement or registration. S3 path: `s3://nmdatasets/NeurIPS2025/`. Direct ZIP download from SCCN download server also available without sign-in. As of the search conducted in May 2026, Releases 1–11 are confirmed on NEMAR with no DUA requirement. Source: https://eeg2025.github.io/data/ ; arXiv:2506.19141v1 §Data ; https://sccn.ucsd.edu/pipermail/eeglablist/2025/018512.html

*Test data (HBN Release 12).* Was not publicly available during the competition phase. The challenge paper states: "will be released publicly in the foreseeable future after the competition." No specific post-competition release date was provided. As of the web search conducted May 2026, NEMAR search results show Releases 1–11 indexed (the most recent indexed release is ds005516 = Release 11, updated March 2025); no Release 12 listing was found. A separate "Not for Commercial Use" variant (nm000103) was published January 2026 but is distinct from Release 12. Release 12 public availability as of May 2026 is unconfirmed and cannot be verified from available sources. Status: PARTIAL — training/validation data open, test set status uncertain.

*Registration friction.* To access the data directly (outside competition), no registration is required — it is openly downloadable. To participate in the Codabench competition phase (now closed), teams needed a Codabench account. For post-competition use of HBN data, no DUA is required for CC-BY-SA-4.0 releases. Friction level: LOW for training/validation data. Source: https://nemar.org ; https://eeg2025.github.io/data/

*License.* CC-BY-SA-4.0 for HBN Releases 1–11. The Not-for-Commercial-Use variant (nm000103) carries a non-commercial restriction. Competition participants were responsible for handling the CC-BY-SA-4.0 terms (attribution, share-alike). For research and non-commercial use, no practical barrier. Source: arXiv:2506.19141v1 ; NEMAR dataset pages.

*Dataset scale and scope relevance.* 3,000+ subjects, ages 5–21, 128-channel EEG, 6 tasks (Resting State, Surround Suppression, Movie Watching, Contrast Change Detection, Sequence Learning, Symbol Search). This is a pediatric / adolescent population (atypical for canonical MI/BCI literature which skews adult) with psychopathology labels rather than motor-imagery labels. Challenge 1 = zero-shot cross-task and cross-subject transfer; Challenge 2 = psychopathology factor prediction. The dataset is relevant to cross-subject generalization but is not a drop-in replacement for MOABB/BCI Competition IV-2a MI benchmarks — it tests a different generalization axis (cross-task transfer of passive/active paradigms rather than cross-subject calibration-free MI decoding).

**Overall verdict — Gap 2: PARTIAL.**

Training and validation data (HBN Releases 1–11) are freely accessible under CC-BY-SA-4.0 with no registration or DUA requirement, via NEMAR and AWS S3 — no friction barrier. Test data (Release 12) was not publicly released as of May 2026; its release is described as forthcoming but no date is confirmed. The candidate can proceed using Releases 1–11 (approximately 2,600 subjects across 11 releases). Whether Release 12 is required depends on whether the AHBU contribution needs the held-out test set specifically. For evaluation-diagnostic work (which is the candidate's proposed scope in §6), Releases 1–11 provide sufficient data; Release 12 would add subjects but is not load-bearing for the research framing. The naming discrepancy ("BCI Foundation Challenge" vs "EEG Foundation Challenge") is a minor cosmetic issue in the candidate file and does not affect the substance.

Sources: arXiv:2506.19141v1 https://arxiv.org/html/2506.19141v1 ; challenge data page https://eeg2025.github.io/data/ ; challenge timeline https://eeg2025.github.io/timeline/ ; NeurIPS competition page https://neurips.cc/virtual/2025/competition/127719 ; NEMAR HBN-EEG listings https://nemar.org ; EEGLABLIST announcement https://sccn.ucsd.edu/pipermail/eeglablist/2025/018512.html

---

### Summary table

| Sub-question | EEG-FM-Bench delivered? | Verdict |
|---|---|---|
| (a) Subject + dataset + hardware disjoint splits simultaneously | No. Subject-independent within each dataset; no cross-dataset or hardware-disjoint axis. | OPEN |
| (b) 0/1/5/20-shot calibration curves per subject | No. No few-shot experiments in the paper. | OPEN |
| (c) Per-subject performance distributions (not averages) | No. Only aggregate mean ± SD across seeds. | OPEN |
| (d) Pre-training-overlap audit | No. Not attempted. Leakage inherited, not audited. | OPEN |
| (e) Riemannian / classical-ML baselines under same splits | No. Neural models only; no MDM, FgMDM, SVM, LDA. | OPEN |
| Challenge dataset — training/validation access | CC-BY-SA-4.0, no DUA, no registration, freely downloadable | CLOSED |
| Challenge dataset — test set (Release 12) access | Unconfirmed as of May 2026; post-competition release promised but not observed | PARTIAL |

### Implication for deferral decision

The critic's finding (premature deferral) is confirmed. EEG-FM-Bench addresses none of the five quality-bar requirements in §6 that represent the candidate's distinctive contribution. The shortlist's deferral reason — "already partly addressed by EEG-FM-Bench" — is factually incorrect. The correct reading of EEG-FM-Bench's role relative to this candidate is: EEG-FM-Bench names the subject-dependent-split problem and enforces subject-independence, which is the *prerequisite* for honest evaluation, not the evaluation itself. The five requirements in §6 are the research gap that remains above that prerequisite. The deferral should be rescinded and the candidate re-entered into the admission-gate process. The dataset access constraint (Gap 2) does not block admission: training/validation data is freely available and sufficient for the proposed scope.
