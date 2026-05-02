# AHBU project — agent operating notes

This is the AI-Assisted Heart-Brain Understanding endeavor. See `README.md` for the charter and `layers/00-vision/README.md` for the vision and hard constraints.

## How this repo is structured

The repo follows the **Layered Endeavor Framework** (see README link). Layers:

- `layers/00-vision/` — root. Vision, hard constraints.
- `layers/10-pain-point-validation/` — identify and validate one real pain point.
- `layers/20-methodology/` — design the technical approach (locked protocol).
- `layers/30-experiments/` — execute, produce honest results.
- `layers/40-analysis/` — interpret, write up, name limitations.

Each layer's `README.md` declares its **mandate, knowledge, output, help target**. Don't reach across layers. Pass information through the help relation (with explicit handoffs, e.g., `selection.md` from layer 10 to layer 20).

## Operating discipline

- **Critic pass** required at each help-boundary milestone. Use the `critic` agent (`.claude/agents/critic.md`) or a structured self-review against the spec the layer received.
- **Human checkpoint** at the end of each meaningful chunk. Don't barrel through pain-point selection → methodology → experiments without checking in.
- **Pain-point validation = required artifact**. No methodology work until layer 10 has a `selection.md` with critic pass notes.
- **Hard constraints** (from vision, non-negotiable): real validated pain point · feasible solution · honest evaluation.
- **Use git.** Commit as you go. Tag milestones (`v0-vision`, `v1-pain-point-locked`, `v2-protocol-locked`, `v3-results`). Branches encouraged for parallel candidate exploration.

## Agent team

- `pain-point-researcher` — surveys constituencies + literature for evidence of real pain.
- `critic` — adversarial review at help boundaries.
- `methodologist` — designs concrete approach after pain point selected.

Spawn additional agents (data-plumber, baseline-builder, ablation-runner, writer, etc.) when the work calls for it. Document new agents alongside existing ones.

## Resource picture

`resources/compute.md`. Binding constraint: 4 GB VRAM. Plan accordingly.

## Quality bar (cross-cutting)

- Honest held-out testing. Held-out touched once for the headline.
- Uncertainty reported on every metric.
- Ablations on load-bearing design choices.
- Failure modes characterized, not buried.
- No metric gaming, no cherry-picking, no hand-waving.

If meeting the quality bar with the chosen approach is impossible, that is itself a finding — surface it, don't paper over.
