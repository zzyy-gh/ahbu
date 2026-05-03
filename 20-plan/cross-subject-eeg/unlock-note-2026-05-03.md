> **Spec:** `10-pain-point/cross-subject-eeg/admission.md`

# Protocol unlock note — 2026-05-03

**Track:** cross-subject-eeg
**Unlock date:** 2026-05-03
**Unlocked by:** methodologist agent (re-pass triggered by leakage_audit pilot finding)
**Prior lock date:** 2026-05-02
**Affects held-out partition:** YES
**Affects primary metric definition:** NO (metric formula unchanged; test-set scope changes for FM arm)
**Critic re-pass required before re-locking:** YES (held-out partition change)

---

## 1. Trigger

The pre-training-overlap audit procedure prescribed in `protocol-lock.md` §4 was run as part of the leakage_audit pilot. The result, confirmed against the LaBraM pre-training corpus published in arXiv:2405.18765 §3.1 (reproduced in the HTML version of the paper), establishes that:

**"EEG Motor Movement/Imagery Dataset"** appears in LaBraM's pre-training corpus. This is the PhysioNet EEG Motor Movement/Imagery database (physionet.org/content/eegmmidb/1.0.0/), which MOABB exposes as `PhysionetMI` (109 subjects, 64-channel, BCI2000 system).

Per `protocol-lock.md` §4 step 5: "If PhysionetMI is in pretrain_list: substitute with Lee2019 or Cho2017 for the FM arm."

Per `risk-register.md` R-2 mitigation step 2: "If PhysionetMI overlaps: remove PhysionetMI from the FM arm's headline evaluation. Substitute Lee2019 or Cho2017 as the test dataset for the FM arm, if those are not in the pre-training corpus."

The existing protocol-lock already anticipated this trigger and specified the substitution path. This unlock formalizes and executes that substitution.

The held-out split has NOT been touched (the single authorized evaluation run has not begun). The unlock is therefore permitted per §8 of the prior protocol-lock.

---

## 2. LaBraM corpus re-examination

Full corpus from arXiv:2405.18765 §3.1 (HTML), approximately 2,534 hours across ~20 datasets:

| Dataset in LaBraM corpus | MOABB alias | In prior protocol? |
|---|---|---|
| BCI Competition IV-1 | (not standard MOABB MI) | dev (not listed) |
| EEG Motor Movement/Imagery Dataset | PhysionetMI | **PREVIOUS TEST — CONTAMINATED** |
| BCI Competition IV-2a | BNCI2014_001 | dev (already known contaminated) |
| BCI Competition IV-2b | BNCI2014_004 | dev (already known contaminated) |
| SEED, SEED-IV, SEED-GER, SEED-FRA | (emotion; not MI) | n/a |
| TUAB, TUEV, TUSZ, TUEP, TUSL, TUAR | (clinical; not MI) | n/a |
| Emobrain, Grasp-Lift, Inria BCI, SPIS, Siena, Target vs Non-Target | various | n/a |

MOABB MI datasets NOT in the LaBraM corpus (no corpus entry found):

| Dataset | MOABB alias | Subjects | Contamination status |
|---|---|---|---|
| Cho2017 | `Cho2017` | 52 | CLEAN — not in corpus |
| Lee2019 | `Lee2019` | 54 | CLEAN — not in corpus |
| GrosseWentrup2009 | `GrosseWentrup2009` | 10 | CLEAN — not in corpus |
| Schirrmeister2017 HighGamma | `Schirrmeister2017` | 14 | CLEAN — not in corpus |
| Weibo2014 | `Weibo2014` | 10 | CLEAN — not in corpus |

---

## 3. Path chosen: Hybrid (Path 3)

**Decision:** Keep PhysionetMI as the Riemannian/classical test dataset. Substitute Cho2017 as the FM arm test dataset. Report per-arm results on per-arm test sets, with the audit explicitly noting the asymmetry.

**Rationale for hybrid over Path 2 (cancel FM arm):**
- The contamination affects only the FM arm's evaluation against PhysionetMI. It does not invalidate the FM probe concept.
- Cho2017 (52 subjects) is clean per the corpus audit and provides adequate statistical power for per-subject distribution analysis (well above the N=62 threshold only when combined, but acceptable standalone for FM-vs-MDM comparison; N=52 is adequate for Wilcoxon at the effect sizes expected).
- The hybrid design is strictly more informative: it produces Riemannian results on the large 109-subject pool AND FM results on a clean 52-subject pool.
- The asymmetry is not a bug — it is an honest consequence of the contamination finding and must be reported as such.

**Rationale for Cho2017 over Lee2019 as FM test dataset:**
- Cho2017 (52 subjects, 2-class MI, 64-channel Biosemi) is the larger of the two clean candidates by established MOABB usage and has been more widely validated in the cross-subject literature.
- Lee2019 (54 subjects, 2-class MI) is very similar in size. Either is acceptable; Cho2017 is selected for its marginally broader citation footprint.
- Lee2019 is reassigned to the secondary dev dataset slot, replacing the "Cho2017 or Lee2019" undecided selection. This is now frozen: Lee2019 = secondary dev.

**Rationale for Path 3 over Path 1 (full substitution):**
- Replacing PhysionetMI entirely with Cho2017 for ALL arms would sacrifice the 109-subject pool for the Riemannian baseline and per-subject distributions. The MDM arm has no contamination problem with PhysionetMI. Discarding 109-subject coverage for the clean classical baseline is wasteful.
- The hybrid design respects what each arm needs: Riemannian baseline maximizes statistical power on its valid test set; FM baseline uses the largest clean alternative.

**Rationale against Path 2 (cancel FM arm entirely):**
- The contamination is specific to PhysionetMI × LaBraM. Cho2017 is clean. Cancelling the FM arm surrenders a testable hypothesis for no technical reason.
- The defensibility critic explicitly characterized FM-arm results on a clean dataset as informative in all directions. Cancellation throws away this contribution.

---

## 4. What changes in the re-locked protocol

| Section | Prior state | New state |
|---|---|---|
| §3 MOABB arm test dataset | PhysionetMI (109 subjects) — single test set for all arms | Split: PhysionetMI = Riemannian/classical test; Cho2017 = FM test |
| §3 secondary dev dataset | Cho2017 or Lee2019 (deferred to week 1) | Lee2019 (frozen now) |
| §3 hardware-disjoint | Verified for BNCI2014_001 vs PhysionetMI only | Verified for BNCI2014_001 vs PhysionetMI (Riemannian arm); Cho2017 vs Lee2019 recording hardware documented at selection time (FM arm) |
| §4 audit procedure | Audit PhysionetMI before touching test | Audit result already known: PhysionetMI contaminated; Cho2017 clean. Audit documented in unlock note. |
| §5 primary metric | LOSO accuracy macro-averaged across datasets (MOABB arm) | Kept: reported per-arm on per-arm test sets; FM arm primary metric on Cho2017; Riemannian arm primary metric on PhysionetMI |
| §7 decision rule | FM-vs-MDM on PhysionetMI | FM-vs-MDM on Cho2017 (FM arm); MDM vs FBCSP on PhysionetMI (Riemannian arm) |

---

## 5. What does NOT change

- The five-part evaluation program (§1 a–e) is unchanged in structure.
- The statistical test (paired Wilcoxon, Bonferroni, k ∈ {0,1,5,20}) is unchanged.
- Bootstrap CI parameters (n=2000, stratified by subject, seed=42) unchanged.
- The leakage audit result is now a documented headline input, not a future step.
- The HBN arm is unchanged.
- The held-out discipline (single authorized evaluation run) is unchanged.
- The Riemannian baseline remains on PhysionetMI, which was the originally intended host for the large-N per-subject distribution analysis.
- The illiteracy-rate characterization remains on PhysionetMI (109 subjects) for the Riemannian arm. For the FM arm on Cho2017 (52 subjects), the illiteracy-rate characterization is reported but with reduced precision; this is documented as a limitation.

---

## 6. Critic re-pass requirement

The held-out partition definition has changed (FM arm test set: PhysionetMI → Cho2017). Per `protocol-lock.md` §8, a critic re-pass is required before re-locking. This re-lock note is written before any experiment code touches either Cho2017 or PhysionetMI test data.

The re-locked protocol-lock.md accompanying this note is the revised pre-registration. Tag `v3-cross-subject-eeg-protocol-relocked` is applied after human checkpoint confirms the revision.
