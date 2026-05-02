> **Spec:** `10-pain-point/affective-state/candidate.md` (under review) + `10-pain-point/README.md` (real-pain-only critic-pass scope)

# Critic pass -- affective-state/candidate.md -- 2026-05-02

## Verdict

**pass-with-fixes**

The candidate demonstrates real pain at the deployment end (anesthesia, fleet-safety, wearable stress) with multiple independent, verified evidence sources. The cross-subject generalization gap and the leakage problem are both well-documented. Two targeted fixes are required before admission: (1) correct the factually wrong characterization of DEAP labels, and (2) substantiate the WESAD person-specific vs generic accuracy figures with a source that actually contains them. These are citation-accuracy issues that fall within the real-pain gate; they do not change the overall verdict because independent evidence for the same pain exists from other sources.

## Findings

### Critical

- **critical -- DEAP labels mischaracterized.** Section 3 "Theoretical / construct-validity critique" third bullet states that DEAP labels are stimulus-class labels, not participant-reported labels -- i.e., the ground truth is what video clip was playing, not what the participant felt. This is factually wrong. DEAP participants provided self-reported valence/arousal/dominance/liking ratings on a 1-9 continuous scale after each video clip; those ratings are the labels, not stimulus identifiers. arXiv:2505.18175, which the candidate itself cites as support for this claim, confirms the opposite: 32 volunteers rated the videos with respect to valence, arousal, familiarity, liking, and dominance. The valid critique of DEAP label quality is real and citable -- retrospective self-report under lab induction, post-hoc binarization thresholds varying arbitrarily across papers, controlled-stimulus ecological validity -- but calling the labels stimulus-class labels is an invented factual claim that a careful reader will immediately refute. **Fix:** replace with accurate description of the actual label-validity problem.

### Major

- **major -- WESAD person-specific vs generic figures: cited source does not contain those numbers.** Section 2 (Constituency) and Section 3 (first sub-section) both attribute person-specific 98.9 % vs generic 83.9 % Random Forest to PMC12685819. Spot-check: PMC12685819 reports 98 % overall accuracy (not person-specific), and attributes a person-specific 95.06 % vs generic approx 67 % figure to a cited external study (Li et al. 2024) -- not to the authors own experiments and not matching the 98.9/83.9 numbers. The specific figures claimed by the candidate do not appear in the cited source. Schmidt et al. 2018 WESAD original PDF and arXiv:2203.09663 are also cited but could not be parsed (binary PDF format); the figures may exist there. The person-specific vs generic gap is real and well-established. **Fix:** identify and cite the actual source that reports exactly these figures, or replace with traceable figures from the cited paper.

### Minor

- **minor -- "2 EDA features" framing slightly imprecise.** Section 3 Reproducibility: arXiv:2508.10561 is confirmed genuine and the finding is correct in direction: 2 electrodermal-derived features out of 164 total features (cardiac + electrodermal combined) showed reproducibility. The candidate phrasing "2 EDA features" is accurate in kind (electrodermal-derived) but omits that the denominator of 164 is the full mixed-modality feature pool. **Fix:** add "(out of 164 cardiac and electrodermal features tested)" for precision.

- **minor -- Strongest-pain constituencies (anesthesia, fleet-safety) are flagged by the candidate itself as potentially beyond AHBU scope.** Section 7 openly acknowledges clinical reachability may exceed AHBU scope. Under the v2 rubric, constituency must be named and reachable in principle. The academic EEG and wearable-stress constituencies (DEAP/SEED community, WESAD follow-ups, MOABB) are clearly reachable. The clinical constituencies are harder. This does not block admission, but the candidate should explicitly state which constituency the track is admitting on, rather than listing six and leaving the operative one implicit.

- **minor -- Lindquist and Barrett 2012 BBS and Hajat 2017 Anaesthesia could not be directly fetched** (403 from paywalled URLs). Both citations are internally consistent with well-known papers; attributions match known publication details. No evidence of error; exact quoted text could not be verified.

- **minor -- Shanker et al. BJA 2023 (five monitors / discordant recommendations) could not be fetched** (403). DOI format is well-formed; claim is consistent with BJA coverage of depth-of-anaesthesia monitor discordance. Cannot independently confirm specific findings.

## What I checked

- Read candidate.md end-to-end.
- Read 10-pain-point/README.md for the v2 rubric and real-pain-only gate scope.
- Read 00-vision/README.md for hard constraints.
- Read 10-pain-point/shared/portfolio.md for current candidate status.
- Read 10-pain-point/shared/critic-shortlist.md and selection-shortlist.md for historical context and prior findings on this candidate.
- Fetched and confirmed arXiv:2212.08744 (Apicella et al. 2024): genuine systematic review, Neurocomputing 2024. Framing matches candidate description. Paraphrased accuracy range (50-70 % in LOSO scenarios) consistent with paper scope.
- Fetched and confirmed PMC11099244 (Brookshire et al. 2024): genuine, Frontiers in Neuroscience 2024. Candidate paraphrase of the central finding is accurate in substance. Paper reports only 27 % of reviewed studies used proper subject-based holdout.
- Fetched and confirmed arXiv:2508.10561: genuine, 2 electrodermal features out of 164 total confirmed. Candidate framing substantively correct; minor precision gap noted.
- Fetched and confirmed PMC6676047 (Ledowski 2019 BJA): genuine. Quote about no firm evidence for clinically relevant influence is accurate verbatim.
- Fetched and confirmed EU AI Act Article 5(1)(f): prohibition on emotion-recognition AI in workplace/education confirmed; in-force date of 2 February 2025 confirmed.
- Fetched arXiv:2404.15319 (MOABB/Chevallier 2024): genuine, reproducibility framing confirmed. Candidate claim that MOABB covers motor imagery/P300/SSVEP (not affective tasks) consistent with paper scope.
- Fetched arXiv:2410.09767 (LibEER 2024): genuine; discusses leakage and inconsistent evaluation protocols as motivation. Candidate characterization is accurate.
- Fetched arXiv:2505.18175 (EEGain 2025): genuine; confirms DEAP uses participant self-reports, directly contradicting the candidate stimulus-class-labels claim.
- Spot-checked PMC12685819 for the 98.9 % / 83.9 % WESAD figures: those exact numbers are not in that source.
- Confirmed EU AI Act scope and entry-into-force date independently.

## What I could not check

- Shanker et al. BJA 2023 (paywall/403). Existence and general topic are plausible; specific claim about five monitors giving discordant recommendations not independently confirmed.
- Lindquist and Barrett 2012 BBS (PhilPapers and hosted PDF both 403). Finding is consistent with widely-reported literature on meta-analytic emotion neuroscience.
- Hajat et al. 2017 Anaesthesia (403). Attribution and DOI format internally consistent.
- APSF Depth-of-Anesthesia Monitoring article (403).
- arXiv:2203.09663 and original WESAD PDF (Schmidt et al. 2018) -- binary PDFs, unreadable. The 98.9 % / 83.9 % figure may exist in one of these; the major finding above is that PMC12685819 does not support those numbers.
- CEUR-WS Vol-4115 paper7 (binary PDF, unreadable): cannot confirm title or trial-level leakage findings.
- Dewangan and Thakur 2023 ResearchGate link (not fetched): 95.7 % vs 78-84 % within-vs-cross-subject gap claim not independently verified.
- Barrett ANS-specificity work (lisafeldmanbarrett.com): not fetched; characterization is consistent with her published meta-analytic body of work.
- Direct constituency outreach: not performed; reachability of academic EEG/wearable community is plausible but not demonstrated.
