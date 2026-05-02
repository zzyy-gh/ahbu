> **Spec:** `10-pain-point/ecg-ppg-realworld/candidate.md` (under review) + `10-pain-point/README.md` (real-pain-only critic-pass scope)

# Critic pass -- ecg-ppg-realworld real-pain claim -- 2026-05-02

## Verdict

**pass-with-fixes**

The real pain is genuine and multi-sourced. No blocking deficiency on independence, constituency, or plain-language dimensions. One major finding must be corrected before admission: a quantitative claim in section 3c is materially misattributed to the JMIR 2024 meta-analysis -- the specific numbers cited do not appear in that paper. Fixing this does not invalidate the skin-tone pain evidence (other cited evidence survives), but the erroneous numbers must be removed or replaced with accurate figures.

---

## Findings

### Critical

None.

---

### Major

**MAJOR -- Misattributed numbers in section 3c** -- candidate.md section 3c, line citing JMIR meta-analysis.

The candidate states: "at 60-70% saturation, darker pigmentation produced average overestimation of 3.56 +/- 2.45% vs 0.37 +/- 3.20% for lighter tones" attributing this to JMIR 2024 (https://www.jmir.org/2024/1/e62769/).

Verified against the actual paper (Singh et al. 2024, systematic review and meta-analysis): the values 3.56, 2.45, 0.37, and 3.20 do not appear anywhere in the paper. The paper explicitly states it did not examine oxygen saturation level as a moderating variable. It reports pooled mean biases of 1.27% (dark, 95% CI 0.58-1.95%) vs 0.70% (light, 95% CI 0.17-1.22%), not sub-group figures at 60-70% saturation. There is no 60-70% saturation stratum in this study.

The skin-tone disparity pain is real and survives: the same JMIR paper confirms dark skin produces greater SpO2 overestimation than light skin, and the MDPI Sensors review also cited in section 3c supports the calibration-gap claim. The pain argument is weakened but not eliminated by using accurate figures. The paper notes the difference may not be clinically relevant in typical ranges, which is itself a finding that should be accurately characterised rather than overstated with wrong statistics.

What to do: Remove the 3.56 +/- 2.45% vs 0.37 +/- 3.20% at 60-70% saturation sentence. Replace with actual Singh et al. 2024 pooled biases (dark 1.27%, light 0.70%; both exceed FDA accuracy thresholds for SpO2 devices). Note the paper does not stratify by saturation range. If the 3.56/0.37 figures came from a different source (e.g. Sjoding et al. NEJM 2020 on ICU pulse oximetry), identify and cite that source explicitly.

---

### Minor

**MINOR -- BASEL Wearable Study venue possibly misidentified** -- candidate.md section 3a.

The candidate cites the BASEL Wearable Study via a ScienceDirect URL with prefix S2405500X22008350 and labels it JACC Adv (JACC Advances). PubMed records identify the study as Mannhart et al. 2023 in JACC Clinical Electrophysiology 9(2):232-242. The S2405500X publisher prefix corresponds to JACC Advances, not JACC Clinical Electrophysiology. The full text was inaccessible (HTTP 403) so the device-specific accuracy figures (Apple Watch 6: 85%/75%, Samsung Galaxy Watch 3: 85%/75%, Fitbit Sense: 66%/79%, Withings Scanwatch: 58%/75%) and the 17-21% inconclusive rate could not be independently verified. The numbers are plausible and consistent with the broader literature.

What to do: Confirm the DOI and journal. If the URL is wrong, replace with the correct citation for Mannhart et al. JACC Clin Electrophysiol 2023. Confirm device-level figures against the actual results table.

**MINOR -- PMC7085621 quotation marks around non-verbatim text** -- candidate.md section 3b.

The candidate uses block-quote formatting for: PPG signals ... are not robust to motion artifacts. The accuracy of PPG sensors during exercise is unsatisfactory. The actual paper (PMC7085621) says devices are only used for general wellness purposes because they are accurate only in limited conditions such as resting or walking slowly. The pain point is accurately captured; the quotation marks imply verbatim reproduction but the phrasing differs.

What to do: Remove quotation marks and present as a paraphrase, or find a paper that uses the exact words.

**MINOR -- Cardiologist false-alarm quote is expert opinion in news, not a research finding** -- candidate.md section 3a.

The Dr. Venkatesh Murthy quote was verified as accurately attributed in STAT News 2019. It is correctly used as clinician-voice constituency evidence. Noting for completeness: it is one expert opinion in a news article, not a controlled finding. No action required.


---

## Independence assessment -- passes

The candidate fields at least six structurally independent evidence threads:

1. Prospective clinical study: Apple Heart Study (NEJM 2019) -- independent from regulatory documents.
2. Regulatory document: FDA De Novo DEN180042 -- independent regulatory risk assessment.
3. Comparative wearable accuracy study: BASEL Wearable Study (Mannhart et al. 2023) -- multi-device academic study.
4. Retrospective propensity-matched cohort: JAHA 2024 (doi:10.1161/JAHA.123.033750) -- quantified clinician-burden primary study, independent of device manufacturers.
5. HRV validity study: JMIR Human Factors 2022 -- verified; HRV explains ~1% of variance in naturalistic stress.
6. Systematic review / meta-analysis: JMIR 2024 (Singh et al.) -- verified; confirmed skin-tone disparity in SpO2.
7. ML benchmark analysis: PhysioNet/CinC 2020 (IOP) -- verified; performance drops on hidden test data confirmed.

This exceeds the >=2 independent source threshold comfortably. Sources span regulatory documents, clinical studies, comparative device studies, academic validity research, and ML benchmarks.

---

## Constituency reachability -- passes

All six named constituencies are reachable in principle:

- Wearable users: Apple Discussions threads at public URLs; Mayo Clinic Connect discussion accessible.
- Clinicians: JAHA 2024 and JMIR Cardio 2023 have named authors at contactable institutions. JMIR Cardio 2023 numbers (69% data-overload concern, 53% manual upload) verified as matching the paper.
- Cardiac technicians: StatPearls is public; iRhythm public documentation cited.
- Athletes / HRV users: JMIR Human Factors paper has named authors; Spannr essay is public.
- Darker-skinned PPG users: researchers reachable via JMIR 2024 and MDPI Sensors review DOIs.
- ML researchers: PhysioNet/CinC challenge organizers publicly listed.

No direct interview was conducted. The v2 rubric requires reachability in principle, which is met.

---

## Plain-language pain statement -- passes

Section 1 accurately reflects the cited evidence. The four named pain threads (AFib false positives, motion artifact, demographic performance gap, HRV over-claim) are each independently supported. The cost characterisation (user anxiety, unnecessary workups, clinician triage burden) is quantified by JAHA 2024 and JMIR Cardio 2023. The plain-language summary matches the evidence base.

---

## What I checked

- Independence of evidence sources across sections 3a-3g: counted structurally distinct sources; checked for cross-restatement.
- Accuracy of key quantitative claims by fetching accessible source papers:
  - JMIR 2024 Singh et al. skin-tone meta-analysis: major finding reported above; 3.56/0.37 values confirmed absent from the paper.
  - JMIR Human Factors 2022: ~1% variance explained for HRV/stress confirmed.
  - PMC9707930 Smole et al.: ECG uncertainty; 25% rejection leading to 98% accuracy confirmed.
  - StatPearls NBK597374: Holter burden quote verified.
  - PMC11794680: PPG HRV validity in non-resting conditions verified.
  - PMC11694482: Apple Watch 60% sensitivity for AF >=1 h vs implantable monitors verified.
  - JMIR Cardio 2023 doi:10.2196/47292: 69% clinician concern, 53% manual upload verified.
  - NeuroKit2 issue #1115: existence and wontfix status verified.
  - Frontiers Neurosci 2020: 17 of 28 studies without criterion validity verified.
  - PPG-beats readthedocs: MIMIC PERform Ethnicity (200 subjects, 100 Black/100 White, ICU, 125 Hz, PhysioNet) verified.
  - STAT News 2019: Dr. Murthy quote verified as accurately attributed.
  - CinC 2020 IOP paper: <=10% drops on hidden test data verified.
- Constituency reachability: all six groups confirmed accessible.
- Plain-language pain statement vs evidence: alignment confirmed.
- Gap-closing section: three gap verdicts checked against source material.

---

## What I could not check

- JAHA 2024 full text (HTTP 403). Specific numbers (4.05 vs 2.70 AF healthcare use P=0.04; 1.84 vs 1.00 rhythm tests P=0.004; 20% anxiety) not verified against full text. Numbers are internally consistent and plausible.
- BASEL Wearable Study full text (HTTP 403). Device-specific figures and 17-21% inconclusive rate not independently verified.
- Fitbit Heart Study (Circulation 2022, HTTP 403). PPV of 32-34% not independently confirmed.
- Apple Heart Study (NEJM 2019, HTTP 403). PPV 0.84 and 450/2161 return rate not verified.
- Tandfonline 2026 overdiagnosis review (HTTP 403). Clinician-burden characterisation unverified.
- FDA DEN180042 PDF (HTTP 404). False-positive risk language not verified in the original document. The document is publicly known; the quote is widely reproduced in secondary literature; the URL appears to have changed.
- Alternative source for the 3.56/0.37 values: confirmed absent from JMIR 2024. No alternative source identified in this pass.
- Apple Discussions thread content (255017393, 256065774, 255643756): accessible in principle but not fetched.
