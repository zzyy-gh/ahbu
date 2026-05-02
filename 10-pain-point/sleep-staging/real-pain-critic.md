> **Spec:** `10-pain-point/sleep-staging/candidate.md` (under review) + `10-pain-point/README.md` (real-pain-only critic-pass scope)

# Critic pass -- sleep-staging candidate.md (inc. Gap-closing 2026-05-02) -- 2026-05-02

## Verdict

pass-with-fixes

The real-pain claim is well-supported across multiple independent evidence classes and clear constituencies. Inter-rater ceiling, automated-stager failure on edge populations, AASM v3 rule inconsistency, wearable misclassification, and scoring-time burden are each backed by multiple sources. The gap-closing section provides additional primary-source quantification that strengthens the admission case. Two citation attribution errors must be corrected before the admission record is finalized; neither error undermines the pain evidence, which survives independently on its other sources.

Scope note: restricted to real-pain dimension per v2 rubric. Feasibility, solution shape, compute envelope, DUA logistics, and defensibility are not gated here.

---

## Findings

- **major** -- Wrong author attribution: Stone et al., Sleep 2021 -- candidate.md section 3e third bullet, section 3f, and gap-closing Sub-gap 2c summary -- The candidate cites PMC8120339 as "Stone et al., Sleep 2021." The paper at PMC8120339 is authored by Chinoy et al. (first author: Evan D Chinoy; no author named Stone among any of the ten listed authors). The journal is Sleep and the volume/issue date is 2021 (Volume 44, Issue 5), so the year is defensible, but the author attribution is wrong. The 30-50% misclassification of REM and deep sleep finding attributed to Stone 2021 is confirmed present in the Chinoy et al. paper (REM sensitivity 0.49-0.69; deep sensitivity 0.53-0.68 across devices), so the evidence itself is accurate. Fix: replace every instance of "Stone et al., Sleep 2021" and "Stone 2021" with "Chinoy et al., Sleep 2021 (PMC8120339)" throughout candidate.md.

- **major** -- Wrong author attribution: Bakker et al. -- candidate.md section 3h first bullet, and gap-closing Sub-gap 2a Finding 1 -- The candidate attributes the 4,243 s / 42.7 s manual-vs-automated PSG timing figures to "Bakker et al. (Frontiers in Neurology 2023, DOI 10.3389/fneur.2023.1123935, PMC9981786)." The paper at that DOI and PMC has first author Bryan Peide Choo; no author named Bakker appears among the ten listed authors. The quantitative findings are confirmed present in the paper, so the data is accurate but the attribution is wrong. Section 3h also appends a parenthetical [JCSM 2020] hyperlink alongside this reference, which does not match the DOI (Frontiers Neurology 2023), suggesting possible conflation with a separate earlier reference. Fix: replace "Bakker et al." with "Choo et al., Frontiers in Neurology 2023 (PMC9981786)" and remove or separately trace the [JCSM 2020] bracket.

- **minor** -- Rosen and Auckley JCSM 2024 not independently verifiable -- candidate.md section 3d first bullet -- The JCSM URL for DOI 10.5664/jcsm.10944 returned a TLS certificate error during this review. The PMC11063699 citation listed as companion in section 3d is a different paper (Malhotra 2024, a letter responding to Skolnik and Attarian, not a Rosen and Auckley paper). The AASM v3 insurance-stratified-diagnosis pain is corroborated by Malhotra PMC11063699 and the AASM v3 summary PDF, so the sub-pain has independent support and is not blocked. Advisory fix: confirm DOI 10.5664/jcsm.10944 is the Rosen and Auckley paper specifically, and that the ethical-dilemma and insurance-stratification framing appear in it, before finalizing the admission record.

- **minor** -- AAST 2023 workforce survey cited with inaccessible primary data -- gap-closing Sub-gap 2a Finding 2 -- The candidate notes the AAST executive summary page returned 404 and only a secondary SleepWorld Magazine summary was accessible. The candidate correctly hedges this as institutional evidence. The Choo et al. timed-observation data and Holm et al. JSR 2026 independently meet the two-source threshold for scoring-burden pain. Fix: qualify the AAST citation as institutional position statement with full data not publicly accessible, or remove it.

---

## What I checked

- Read candidate.md end-to-end: sections 1 through 7 and Gap-closing 2026-05-02 (Gap 1; Gap 2 sub-gaps 2a/2b/2c; summary table; admission impact paragraph).
- Read 10-pain-point/README.md v2 rubric: two-independent-source requirement, constituency reachable in principle, pain statement matches evidence, no invented pain, quote accuracy.
- Fetched PMC8807917 (Lee et al. JCSM 2022 meta-analysis). Verified: overall kappa 0.76 (95% CI 0.71-0.81), N1 0.24, W 0.70, N2 0.57, N3 0.57, REM 0.69. Candidate figures accurate.
- Fetched PMID 31869808 (Korkalainen et al. IEEE JBHI 2020). Verified: 84.5% (kappa 0.79) non-OSA; 76.5% (kappa 0.68) severe OSA. Candidate figures accurate.
- Fetched PMC8120339 to verify Stone et al., Sleep 2021. Result: first author Evan D Chinoy; no author named Stone. Year 2021 (print/volume date); online-first December 2020. REM and deep sensitivity figures confirmed present in the paper. Author attribution is wrong.
- Conducted two independent PubMed searches and one Sleep-journal search for a Stone-authored consumer sleep tracker PSG validation paper from 2021. No such paper found. Confirms Stone is an error, not a pointer to a different paper.
- Fetched PMC9981786 / DOI 10.3389/fneur.2023.1123935 to check Bakker et al. Result: first author Bryan Peide Choo; no Bakker among ten authors. Timing figures 4,243 s and 42.7 s confirmed correct in the paper.
- Fetched PMC8050216 (Perslev et al. U-Sleep, npj Digital Medicine 2021). Verified F1 scores: W 0.91, N1 0.53, N2 0.86, N3 0.77, REM 0.90. Candidate uses W 0.90, N2 0.85, N3 0.76 -- rounding within 0.01, acceptable. Human-expert-parity quote confirmed verbatim.
- Fetched PMC11789265 (Kevat et al. JCSM 2025, U-Sleep pediatric). Verified kappa by age: 3m-1yr 0.50, 1-2yr 0.59, 5-12yr 0.73, overall 0.69. Candidate figures accurate.
- Fetched PMC11063699 to identify the companion AASM v3 citation. Confirmed it is Malhotra 2024 letter -- different author and paper from Rosen and Auckley. Direct fetch of DOI 10.5664/jcsm.10944 failed (TLS error).
- Fetched PMC5263088 (Baron et al. JCSM 2017, orthosomnia). Confirmed both patient quotes verbatim. Accurate.
- Fetched PMC10654909 (Lee and Cho et al. JMIR mHealth 2023, 11 wearables). Verified macro-F1 best 0.69 / worst 0.26, 349,114 epochs. Candidate figures accurate.
- Fetched PMC10140398 (Somaskandhan et al. Frontiers Neurology 2023, preadolescent children). Confirmed kappa 0.57-0.63 statement and EEG-age-variability quote. Note: the 0.57-0.63 range in this paper describes the low end of inter-center adult agreement; the candidate uses it in pediatric context, which is directionally defensible given the paper is about pediatric staging.
- Counted independent evidence sources per sub-pain. Inter-rater ceiling: Lee 2022, Danker-Hopfe 2009, Holm 2026 (3 sources). Automated-stager population degradation: Korkalainen 2020, Kevat/JCSM 2025, van Gorp 2023, Frontiers epilepsy 2024 (4 sources). AASM v3 rule conflict: Malhotra/PMC11063699, AASM v3 summary PDF, EnsoData webinar (3 sources; Rosen/Auckley unverified but sub-pain survives without it). Wearable misclassification: Chinoy 2021, Lee/JMIR 2023, Sleep Adv 2025, MDPI Sensors 2024 (4 sources). Scoring burden: Choo 2023, Holm 2026 (2 independent timed observations). Consumer/clinician pain: Baron 2017 verbatim case series, Mak/Wong AASM 2025 named-clinician statement, Addison/Baron JCSM 2023 provider survey n=176 (3 sources). All sub-pains meet the two-source minimum.
- Confirmed constituency reachability: sleep technologists (AAST, SleepScoringSolution contact pages); clinicians (JCSM authors contactable via journal, AASM commentary authors named); pediatric researchers (van Gorp and Kevat corresponding authors on published papers); wearable users (Garmin and Apple community forums active and public); open-science maintainers (U-Sleep GitHub, PhysioNet discussion boards). All reachable in principle.
- Confirmed no invented pain: all five sub-pains grounded in current empirical literature, published clinical position papers, FDA records, or active user forums. No future-work-section hypotheticals.

---

## What I could not check

- Rosen and Auckley JCSM 2024 (DOI 10.5664/jcsm.10944) source text -- TLS error on JCSM site. Ethical-dilemma framing and dual-criteria insurance conflict could not be confirmed verbatim from the paper.
- van Gorp et al. Sleep Med Rev 2023 (ScienceDirect) -- 403 error. The 78.9% vs 88.9% accuracy figures not directly verified; consistent with pattern established by Kevat et al.
- Holm et al. JSR 2026 (PMC12856104) figures (14% inter-scorer disagreement, 34.6% respiratory event disagreement, 66% OSA severity reclassification) -- not independently fetched.
- Frontiers Neurology 2024 pediatric epilepsy paper (DOI 10.3389/fneur.2024.1390465) accuracy figures (84.7% vs 80.8%) -- not independently fetched.
- Addison, Grandner and Baron JCSM 2023 (DOI 10.5664/jcsm.10604) provider survey details -- not independently fetched; 176-provider figure and 36% consumer tech use figure relied on candidate characterization.
- Possible separate Bakker/JCSM 2020 paper that may have been the intended source for the [JCSM 2020] bracket in section 3h -- searched in PubMed, not found. May not exist.
- Zenodo record 15900394 (Dreem-DOD, MIT license) -- not re-fetched during this pass; gap-closing conclusion accepted.
- SleepTransformer (Phan et al. PMC10827185) specific F1 figures -- not independently fetched.
