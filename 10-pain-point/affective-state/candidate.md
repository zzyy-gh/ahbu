# Candidate: Affective / Mental-State Inference from Physiological Signals

Slug: `affective-state`
Date: 2026-05-02
Researcher: pain-point-researcher (broad survey pass)
Confidence: **mixed — pain points exist but are largely "the field is hard", not "a constituency is starved for help"**

## 1. Pain point statement

Models that infer affective or mental states (emotion category, valence/arousal, stress, drowsiness, cognitive load, pain) from physiological signals (EEG, ECG/HRV, EDA, fNIRS, fusion) routinely report 80–98 % accuracy on public benchmarks (DEAP, SEED, WESAD, etc.) but fail to generalize to new subjects, new sessions, new contexts, and new labs. Reported numbers are inflated by trial-level and subject-level data leakage, by within-subject evaluation that masks the hard problem, by cherry-picked features whose reproducibility across datasets is near-zero, and by ground-truth labels (induced-emotion class IDs, stimulus tags) whose validity as labels of the participant's actual internal state is questionable. The downstream consequence is that practitioners (HCI researchers, neuroergonomics teams, fleet-safety vendors, anesthesiologists) who try to deploy these models in field conditions either get unusable results or build elaborate per-subject calibration pipelines that defeat the purpose.

## 2. Constituency

Several distinct groups feel different aspects of this gap. They are **not** all equally pained, and their willingness-to-act differs:

- **Affective-EEG academic researchers** (DEAP/SEED/MAHNOB-HCI users). Feel the cross-subject gap acutely — entire sub-literature exists trying to close it. But pain is mostly internal to the field; not clear an external constituency depends on a fix.
- **Wearable stress-detection vendors and quantified-self users** (WESAD-style). Feel inter-individual variability — "person-specific 98.9 %, generic 83.9 %" gap [Schmidt 2018, follow-ups]. Practitioners cope by per-user calibration.
- **Driver-drowsiness / fleet-safety industry**. Feel the lab-to-road gap; current commercial systems mostly use facial video + steering, not EEG, partly because EEG-based systems are not robust enough to leave the lab.
- **Anesthesiologists using BIS / NoL / ANI**. Feel monitor disagreement and known failure modes (ketamine, EMG, paralysis, neurologic pathology). APSF still does not list depth-of-anesthesia monitoring as a standard of care.
- **Neuroergonomics / training-simulator practitioners** (aviation, driving instruction). Use EEG workload metrics, but mostly as supplementary — not as a sole decision input.
- **HCI / education researchers using fNIRS for cognitive load**. Mostly pre-deployment; field gaps acknowledged in their own discussion sections.

The strongest pain — i.e., constituency that loses real money / safety / care quality from the gap — is in **clinical anesthesia/pain monitoring** and in **fleet-safety**, not in academic emotion recognition.

## 3. Evidence of pain

### Cross-subject / cross-session generalization gap (well-documented)

- Apicella et al. 2024, "Toward cross-subject and cross-session generalization in EEG-based emotion recognition: Systematic review, taxonomy, and methods" (Neurocomputing). Direct framing: "Although methods achieve state-of-the-art performance within-participant, it still remains a challenge to improve performance in cross-participant classification, with accuracy between 50 and 70 % in some leave-one-subject-out validation scenarios." [arXiv:2212.08744](https://arxiv.org/html/2212.08744v3) / [DOI:10.1016/j.neucom.2024.128354](https://www.sciencedirect.com/science/article/pii/S0925231224011251).
- Concrete subject-dep vs subject-indep gaps reported across multiple papers, e.g., 95.7 % within-subject vs 78–84 % across-subject on SEED with the same SVM pipeline (Dewangan & Thakur 2023). [ResearchGate](https://www.researchgate.net/publication/374689940). One concrete dataset, but the pattern is industry-wide.
- WESAD: Schmidt et al. 2018 baseline 93.1 % LDA; follow-up work shows person-specific 98.9 % vs generic 83.9 % Random Forest; calibration moves a hybrid model from 42.5 ± 19.9 % to 95.2 ± 0.5 %. [WESAD paper](https://www.eti.uni-siegen.de/ubicomp/papers/ubi_icmi2018.pdf), [Cross-domain framework on WESAD/DREAMER PMC12685819](https://pmc.ncbi.nlm.nih.gov/articles/PMC12685819/), [Improved subject-independent stress arXiv:2203.09663](https://arxiv.org/pdf/2203.09663).

### Data leakage in published benchmarks (strong, recent, and damning)

- Brookshire et al. 2024, "Data leakage in deep learning studies of translational EEG" (Frontiers in Neuroscience). Quote: "Most published DNN-EEG studies may dramatically overestimate their classification performance on new subjects." [PMC11099244](https://pmc.ncbi.nlm.nih.gov/articles/PMC11099244/) / [Frontiers DOI](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2024.1373515/full).
- "Impact of Trial-wise and Test Data Leakage on EEG-Based Emotion Classification" CEUR-WS. Demonstrates trial-level leakage specifically on emotion-recognition benchmarks. [CEUR-WS Vol-4115 paper7](https://ceur-ws.org/Vol-4115/paper7.pdf).
- LibEER 2024 benchmark library motivates itself by noting that prior emotion-EEG papers use inconsistent and often-leaky evaluation. [arXiv:2410.09767](https://arxiv.org/html/2410.09767v1).
- "Evaluation in EEG Emotion Recognition: State-of-the-Art Review and Unified Framework" arXiv 2025. [arXiv:2505.18175](https://arxiv.org/pdf/2505.18175).

### Reproducibility of physiological features

- "Reproducible Physiological Features in Affective Computing: A Preliminary Analysis on Arousal Modeling" 2025. Out of **164** features tested across cardiac and electrodermal signals, only **2 EDA features** showed reproducible, statistically significant association with arousal across studies. [arXiv:2508.10561](https://arxiv.org/html/2508.10561). This is a near-total failure of feature stability.

### Theoretical / construct-validity critique

- Lindquist, Wager, Kober, Bliss-Moreau, Barrett 2012 "The brain basis of emotion: a meta-analytic review" (BBS). Found "little evidence that discrete emotion categories can be consistently and specifically localized to distinct brain regions." [PhilPapers](https://philpapers.org/rec/LINTBB) / hosted PDF [BC IR](https://ur.bc.edu/system/files/2025-04/bc-ir101745.pdf).
- Barrett's broader meta-analytic work on autonomic specificity: discrete-emotion ANS fingerprints not reliably found across >20 000 subjects. [Lisa Feldman Barrett papers](https://lisafeldmanbarrett.com/academic-papers/). If discrete emotions don't have specific physiological fingerprints, then high cross-subject DEAP/SEED accuracy is a priori suspicious — it's classifying *something*, but probably the stimulus rather than the felt emotion.
- Emotion-elicitation validity: DEAP labels are stimulus-class labels, not participant-reported labels — i.e., the "ground truth" is what video clip was playing, not what the participant felt. [Evaluation in EEG Emotion Recognition arXiv:2505.18175](https://arxiv.org/html/2505.18175v1).

### Deployment evidence — where the rubber meets the road

- **Anesthesia.** Shanker et al., "Five commercial 'depth of anaesthesia' monitors provide discordant clinical recommendations in response to identical emergence-like EEG signals" BJA 2023. [BJA](https://www.bjanaesthesia.org.uk/article/S0007-0912(23)00026-0/fulltext). Hajat et al. 2017, "The role and limitations of EEG-based depth of anaesthesia monitoring." [Anaesthesia DOI:10.1111/anae.13739](https://associationofanaesthetists-publications.onlinelibrary.wiley.com/doi/full/10.1111/anae.13739). APSF: "Depth of Anesthesia Monitoring — Why Not a Standard of Care?" [APSF article](https://www.apsf.org/article/depth-of-anesthesia-monitoring-why-not-a-standard-of-care/).
- **Nociception (pain) monitors.** Ledowski 2019 "Objective monitoring of nociception: a review of current commercial solutions" BJA: "there is currently no firm evidence for any clinically relevant influence of such devices on patient outcome." [PMC6676047](https://pmc.ncbi.nlm.nih.gov/articles/PMC6676047/). Recent ASRA newsletter 2024 on validity / usefulness reaches similar cautious conclusions. [ASRA News 2024](https://asra.com/news-publications/asra-newsletter/newsletter-item/asra-news/2024/08/08/nociception-monitors-in-2024-validity-and-usefulness-for-clinical-practice-in-anesthesia).
- **Drowsiness.** Multiple reviews note that "physiological signal-based methods like EEG are well-suited for laboratory conditions but are not very practical in real-world driving scenarios" — current commercial DMS systems use cameras, not EEG. [Sensors 21:3786](https://www.mdpi.com/1424-8220/21/11/3786), [PMC8840041](https://pmc.ncbi.nlm.nih.gov/articles/PMC8840041/).
- **Regulation.** EU AI Act Article 5(1)(f), in force Feb 2 2025, prohibits emotion-recognition AI in workplace and education contexts on the grounds it has unacceptable error and rights risk — a *regulator* concluding the technology doesn't work well enough to deploy. [EU AI Act Article 5](https://artificialintelligenceact.eu/article/5/), [Wolters Kluwer commentary](https://legalblogs.wolterskluwer.com/global-workplace-law-and-policy/the-prohibition-of-ai-emotion-recognition-technologies-in-the-workplace-under-the-ai-act/).

### Standardization tooling exists (sign that the community feels the pain)

- MOABB (Chevallier et al. 2024) explicitly motivates itself by reproducibility concerns: "Due to non-standardized evaluation protocols, conducting meta-analyses in the field of BCI has proven to be challenging." [arXiv:2404.15319](https://arxiv.org/abs/2404.15319). MOABB focuses on motor imagery / P300 / SSVEP, not affective tasks — leaving affective benchmarking comparatively under-tooled.

## 4. Counterfactual

If resolved well, the world would have:

- **Honest, leakage-free benchmarks** for affective-state inference with mandatory subject-/session-/dataset-disjoint splits, where reported accuracies *match* deployment accuracies within a few points.
- **Calibration-cost transparency**: every published model would report (a) zero-shot cross-subject performance and (b) how much per-user calibration data closes the gap.
- For clinical and safety constituencies: a clearer signal about which signals genuinely carry the construct (probably arousal / sympathetic activation) vs which are folk-psychological constructs the signals don't actually encode (e.g., discrete emotions).

For the AHBU project specifically, the **most actionable counterfactual** is *not* "build a better emotion recognizer" but "rigorously expose the gap on a public benchmark, and produce honest baselines." That is feasible at GTX-1650 scale and contributes to the field without needing to outperform massive deep-learning leaderboards.

## 5. Feasibility sketch

- **Datasets** (public, open license-ish): DEAP (32 subj, EEG+peripheral), SEED / SEED-IV (15 subj, EEG, music/film clips), MAHNOB-HCI (27 subj, EEG+ECG+EDA), WESAD (15 subj, ECG/EDA/EMG/RESP/ACC, stress vs amusement vs baseline), DREAMER (23 subj), AMIGOS, Stress-Predict.
- **Compute envelope.** Classical ML (SVM, RF, Riemannian on covariance), shallow CNN on band-power features, pretrained-feature extractors (e.g., LaBraM-style if licensed). All fit GTX 1650 4 GB. Heavy transformer pretraining does not — but is also not necessary for the *demonstration-of-gap* contribution.
- **Time horizon.** Honest re-evaluation of 3–4 datasets with proper splits + leakage diagnostics: weeks-to-months. Cross-dataset transfer evaluation: additional weeks.
- **Risks.** (a) The "gap exposure" contribution is well-established already — risk of redundancy with Apicella 2024 review and Brookshire 2024 leakage paper. (b) Findings may be too negative to motivate downstream layers; need to surface a constructive angle. (c) Construct-validity critique (Barrett) suggests the gap may be partly *not closeable* with current datasets at all — the labels themselves are weak.

## 6. Quality-bar implications

If selected, evaluation MUST:

- **Subject-disjoint splits** as the headline metric. Within-subject reported only as a secondary number, with a clear flag that it is not deployment-relevant.
- **Cross-session and cross-dataset** as further tiers when possible.
- **Trial-level vs window-level care.** No window from a trial may straddle train and test. Document this explicitly per Brookshire 2024.
- **Hyperparameter selection on a held-out subject set, never the test set.**
- **Calibration-curve reporting**: accuracy as a function of N labeled examples from the target subject.
- **Ablation against trivial baselines**: stimulus-period detector (no physiology), per-subject majority class, simple per-subject z-scored band power. Many "deep" affective papers don't beat these honestly.
- **Confound checks**: does the model still work after removing the stimulus-onset artifact, line noise, EOG?

## 7. Open questions

- Is there a constituency willing to *adopt* better evaluation, or is the field's incentive structure (high-accuracy claims = publication) strong enough that honest baselines get ignored? Need ≥1 named practitioner / lab confirming they would use such results.
- Is there a sub-area (e.g., **stress detection from HRV+EDA only**, or **drowsiness from EEG**) where the construct is more physiologically grounded than discrete-emotion classification, and where honest evaluation actually advances deployment? Drowsiness and sympathetic-arousal stress are the most credible.
- Could AHBU usefully reframe as **"physiological arousal decoding done honestly"** rather than "emotion recognition done honestly," dodging the Barrett critique?
- Is the clinical pain-monitoring constituency reachable? They have real pain (no validated outcome benefit per BJA review) but the regulatory and dataset-access barriers may exceed AHBU's scope.
- Counterfactual to the candidate: what if the best contribution is *not* in this domain but in arrhythmia or sleep, where labels are less contested? Defer to other candidates and the layer's selection step.

## Candor note on the subfield

Affective-state inference from physiological signals is one of the **less epistemically healthy** corners of biosignal ML. Surface symptoms — high reported accuracy, many papers, active leaderboards — disguise multiple deep problems: contested constructs (Barrett), weak labels (DEAP uses stimulus-class as ground truth), benchmark leakage that the field has only recently begun naming explicitly, near-zero feature reproducibility across studies (2 of 164), and a regulator (EU) that has now banned a major application class. There is real pain here, but a meaningful fraction of it is **the field's pain at confronting that its claims were oversold**, not a constituency starving for the next model. AHBU should engage this domain only if its contribution is "honest evaluation / leakage diagnostic" rather than "new SOTA." Otherwise, candidates rooted in arrhythmia detection, sleep staging, or seizure prediction — where labels are clinically grounded and the gap is more clearly engineering rather than construct — are likely to be stronger choices.
