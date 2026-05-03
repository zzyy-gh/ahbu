# Public dataset registry

Discovered datasets bearing on heart-brain understanding. Populate as candidates emerge.

| Slug | Modality | Size | License | Use cases | Notes |
|------|----------|------|---------|-----------|-------|
| HMC PSG | EEG (4ch) + EOG + EMG + ECG | 154 subjects, ~2 GB | CC-BY 4.0 (PhysioNet) | sleep-staging scope (b) primary; HRV-vs-EEG paired headline | https://physionet.org/content/hmc-sleep-staging/1.0.0/ — open access, no DUA. |
| MESA | PSG (single-channel U-Sleep input) | 2,056 subjects, ~165 GB EDF | NSRR DUA approved (token in `.env`) | sleep-staging scope (a) primary; AHI-stratified headline | https://sleepdata.org/datasets/mesa — token-gated, validated by P-7 at layer-30 entry. |
| Sleep-EDF Cassette | EEG/EOG PSG | ~1 GB | CC-BY-NC 3.0 (PhysioNet) | sleep-staging dev / U-Sleep training corpus reference | https://physionet.org/content/sleep-edfx/1.0.0/ — non-commercial license. |
| CAP Sleep | PSG inc. ECG | 108 subjects | ODC-BY (PhysioNet) | sleep-staging scope (b) substitute if HMC PSG inaccessible | R&K labels, mapping per protocol-lock §3. |
| Dreem-DOD-O / DOD-H | EEG + consensus labels | 80 subjects total | open access (Dreem) | sleep-staging P-6 framing probe | inter-scorer disagreement reference for the headline framing. |
| PhysionetMI | EEG (64ch) MI | 109 subjects | open (PhysioNet) | cross-subject-eeg classical/Riemannian arm test | LaBraM-contaminated — CANNOT be used for FM arm test. |
| Cho2017 | EEG (64ch) MI | 52 subjects | open (MOABB) | cross-subject-eeg FM arm test (LaBraM-clean) | substituted in v2 unlock per LaBraM corpus audit. |
| BNCI2014_001 | EEG (22ch) MI | 9 subjects | open (MOABB) | cross-subject-eeg dev (P-2 / P-4 pilots) | small, fast for VRAM/speed probes. |
| Lee2019 | EEG MI | 54 subjects | open (MOABB) | cross-subject-eeg FM arm augmentation if Cho2017 N<62 | per protocol-lock R-5 mitigation. |
| CinC 2017 | single-lead ECG | 8,528 records | ODC-BY (PhysioNet/CinC) | ecg-ppg-realworld primary (post-PTB-XL pivot) | 771 AF records; 80/20 stratified split per protocol-lock. |
| WESAD | ECG + EDA + RESP | 15 subjects | open (Siegen sciebo) | affective-state primary | downloaded; P-3 PASS. |
| DEAP | EEG + ECG + EDA | 32 subjects | request form | affective-state secondary | access pending (R-1). |
| MAHNOB-HCI | EEG + ECG | 27 subjects | request form | affective-state secondary | access pending (R-1). |
| DREAMER | EEG + ECG | 23 subjects | request form | affective-state backup (P-5) | contingency only. |

Populate this table as the pain-point validation layer surfaces concrete candidates.

Common starting points (to be vetted before listing):

- **PhysioNet** — large catalogue: MIT-BIH (ECG), Sleep-EDF (PSG), CHB-MIT (EEG seizure), etc.
- **OpenNeuro** — open neuroimaging datasets including EEG.
- **MOABB** — Mother Of All BCI Benchmarks; standardized BCI EEG datasets + evaluation.
- **TUH EEG** — large clinical EEG corpus (registration required).
- **HBN (Healthy Brain Network)** — child/adolescent EEG + multimodal.
- **DEAP / SEED / MAHNOB-HCI** — affective EEG.
- **WESAD** — wearable stress detection (ECG, EDA, etc.).
- **PTB-XL** — large 12-lead ECG dataset.
- **DREAMER** — EEG + ECG affective.
- **PASE / CinC challenges** — competition datasets across cardiac problems.
