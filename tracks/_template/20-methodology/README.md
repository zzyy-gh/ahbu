# Track layer 20 — Methodology

**Mandate.** Translate this track's admitted pain point into a concrete, feasible technical approach.

**Knowledge.** Track's admission record (`layers/10-pain-point-validation/admission/<slug>.md`), public datasets, OSS biosignal stacks (MNE-Python, NeuroKit2, BioSPPy, sklearn, PyTorch, HuggingFace), recent literature, **`shared/` substrate**.

**Output.**
- `approach.md` — chosen approach: data, preprocessing, model family, evaluation protocol, ablations, uncertainty reporting plan, **shared-substrate dependencies + contributions**.
- `risk-register.md` — known risks, mitigations, kill criteria.
- `protocol-lock.md` — frozen evaluation protocol (held-out split, metrics) — locked **before** running experiments.

**Help target.** Layer 10 admission record for this track.

---

## Reuse-first design

Before drafting `approach.md`:

1. Read `shared/README.md` and survey `shared/eval/`, `shared/data/`, `shared/models/`.
2. Identify components reusable as-is, components that need extension, and gaps.
3. Decide what this track will **consume** from `shared/`, what it will **promote** to `shared/`, and what is genuinely track-specific.

Document these decisions in `approach.md` under a **Shared substrate** section. The methodologist agent (`.claude/agents/methodologist.md`) is responsible for this scan.

## Critic gate

Critic pass before `protocol-lock.md` is committed. Locked protocol must not be modified silently — changes require an explicit unlock note with critic re-pass.
