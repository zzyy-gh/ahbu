# Critic pass — cross-subject-eeg.md (inc. Gap-closing 2026-05-02) — 2026-05-02

## Verdict

pass-with-fixes

The real-pain claim is firmly established by multiple independent evidence sources across distinct evidence classes. The constituency is named with concrete, reachable contact paths. The pain statement accurately reflects the evidence. Counter-evidence is present and honest. One citation has compounded attribution errors that must be corrected before the admission record is finalized; those errors do not undermine the pain evidence, which survives on its other sources.

Scope note: this pass is restricted to the real-pain dimension per the v2 admission rubric. Feasibility, solution shape, and defensibility are not gated here.

## Findings

- major — Citation attribution errors on §3a first bullet — candidates/cross-subject-eeg.md §3a, first bullet — The paper at PMC8417074 is authored by Huang et al. (lead: Xin Huang), published in Frontiers in Neuroscience, Volume 13, 2021. The candidate states "Wu et al., Sensors 2021" — two errors: wrong lead-author surname (Wu vs Huang), wrong journal (Sensors vs Frontiers in Neuroscience). The paper title is correct. The bracketed quote ("time-consuming calibration process is necessary due to high inter-subject variabilities … costly and tedious … hinders the further expansion of MI-based BCIs outside of the laboratory") is a paraphrase, not verbatim; the actual text states "each subject usually spends long and tedious calibration time" due to "high inter-subject/session variability." The specific "approximately 20–30 minutes" figure does not appear in this paper; it is attributed vaguely to "survey work in the area" with no specific citation. Fix: (a) correct author to Huang et al., (b) correct journal to Frontiers in Neuroscience, (c) mark quote as paraphrase or replace with verbatim text, (d) add a specific citation for the 20–30 minute figure. The calibration-burden pain is independently confirmed by §3b (BCI Competition IV-2a LOSO vs within-subject gap), §3a second bullet (Saha & Baumert 2020 illiteracy rates), §3b (TCPL few-shot curve), and §3d (Neurable FAQ) — correcting this citation does not change the verdict.

- minor — OpenBCI forum thread characterization slightly over-states content — §3d third bullet — The candidate describes the thread at /discussion/2564/ as documenting user pain around "setup, electrode quality, hair, and reference-electrode reliability." The thread exists and addresses electrode impedance and noise-to-signal challenges with dry electrodes. "Hair" and "reference-electrode reliability" are not specifically the focus of the retrieved content. The characterization is directionally accurate but slightly over-states thread specifics. Fix: read the thread directly before finalizing §3d, or narrow the description to impedance/noise/signal-quality challenges.

- minor — r/BCI first-person practitioner quote gap remains open — §7, last bullet — The researcher self-flags: "Could not verify: a clean, recent r/BCI thread quote where a practitioner explicitly describes the calibration burden as their #1 frustration." This is a genuine gap for that one constituency channel. It is acceptable at admission because five other concrete reachable paths exist (MOABB GitHub, braindecode GitHub, EEG Foundation Challenge organizers via arXiv:2506.19141, LaBraM authors GitHub, OpenBCI forum). The reachability requirement is met without Reddit. No block; worth closing in the track's early life to ground any consumer-frustration narrative.

## What I checked

- Read the full candidate file end-to-end: §1–§7, constituency contact-paths, and Gap-closing 2026-05-02 (§§Gap 1, Gap 2, summary table, implication).
- Read 10-pain-point/README.md v2 admission rubric: ≥2 independent sources, constituency reachable in principle, pain statement matches evidence, no invented pain, quote accuracy.
- Fetched PMC8417074 directly to verify author names, journal, and quote accuracy. Result: authors are Huang et al. (not Wu et al.), journal is Frontiers in Neuroscience (not Sensors), verbatim text differs from the candidate's bracketed quote, "20-30 minutes" not found in the paper.
- Fetched the Saha & Baumert URL (fncom.2019.00087) to verify the "15–30%" BCI illiteracy quote, authorship, and year. Confirmed: Saha & Baumert, published January 21, 2020, Frontiers in Computational Neuroscience Vol. 13. Quote accurate. The "2019" in the DOI path reflects submission year; formal publication is 2020, consistent with the candidate's label.
- Fetched arXiv:2507.11783v3 to verify three quoted findings. All three confirmed.
- Fetched the Neurable FAQ to verify three quoted statements in §2 and §3d. All three confirmed verbatim.
- Fetched the OpenBCI forum thread /discussion/2564/ to verify existence and characterization. Thread exists and addresses dry-electrode signal quality; "hair" and "reference-electrode reliability" were not in the retrieved content.
- Fetched arXiv:2404.15319 abstract to confirm Chevallier et al. authorship. Confirmed.
- Counted independent evidence classes: (1) calibration-reduction literature review (PMC8417074 / Huang et al.), (2) BCI illiteracy reviews (Saha & Baumert 2020; Zhang et al. 2020), (3) benchmark performance gap (BCI Competition IV-2a LOSO vs within-subject from multiple independent papers), (4) EEG foundation-model critical review (arXiv:2507.11783), (5) EEG Foundation Challenge 2025 organizers (arXiv:2506.19141), (6) consumer industry documentation (Neurable FAQ, Emotiv docs). Five-plus independent source classes; the ≥2 threshold is met without relying on the misattributed PMC8417074 citation.
- Confirmed constituency reachability: MOABB (GitHub issues/discussions), braindecode (GitHub), EEG Foundation Challenge organizers (arXiv contact), LaBraM authors (GitHub), OpenBCI forum, r/BCI. All reachable in principle.
- Confirmed §3f counter-evidence section is present and substantive.
- Confirmed no invented pain: calibration burden, BCI illiteracy, LOSO accuracy gap, foundation-model leakage, and consumer personalization requirement are all documented in real literature and real products.

## What I could not check

- I did not independently trace the "20–30 minutes" calibration figure to any specific primary source beyond confirming it is absent from PMC8417074. The claim may be accurate but the source is unverified.
- I did not fetch the Emotiv training-profile documentation to verify the exact quote in §3d; I relied on the candidate's attribution.
- I did not independently browse r/BCI for first-person practitioner calibration-burden complaints; the researcher already flagged this as unresolved.
- I did not verify the BCI Competition IV-2a LOSO accuracy numbers in §3b (CTNet 58.64%, CCST 68.27%, etc.) against the source papers.
- I did not verify the TCPL few-shot calibration curve numbers in §3b against the source paper.
- I did not independently verify the EEG Foundation Challenge dataset access claims in Gap 2; I relied on the gap-closing section's sourced narrative.
- I did not verify arXiv:2602.01019 venue beyond confirming the arXiv listing exists; the candidate already self-flagged this in §3e.
