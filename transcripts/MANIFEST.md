# Manifest — agentId → description

Two transcript kinds are auto-synced into this dir by `bin/sync-transcripts.ps1`:

- `session_<sessionId>.jsonl` — main-agent **orchestration** transcript: Agent spawns, SendMessage between teammates, hooks, result stitching. The active session's file is refreshed each sync (it grows mid-session).
- `<sessionId>_agent-<agentId>.jsonl` — each spawned **subagent's** internal transcript.

The table below maps subagent agentIds → persona/task. The orchestration file for the same session is the one to read for *how* those subagents were dispatched and stitched.

## Session 0db0e24d-08f6-4bde-8559-cb2cdb16c070 — 2026-05-02 — admission gap-closing

| agentId | Persona | Task | Status | Cost |
|---|---|---|---|---|
| a6dd95db8598de9e2 | methodologist | Pre-admission reuse sketches × 4 candidates | OK | 53k tok / 3 min / 22 tools |
| a714e096e66161d08 | pain-point-researcher | Close gaps: EEG-FM-Bench scope, BCI Foundation Challenge access | OK | 69k tok / 7 min / 47 tools |
| a922da489462eacf1 | pain-point-researcher | Close gaps: Dreem-DOD friction, sleep-staging constituency primary sources | OK | 80 tools / 9.7 min |
| a85391f00ee660ddb | pain-point-researcher | Close gaps: skin-tone labels, abstention novelty, ecg-ppg constituency | FAILED — Anthropic rate limit hit before final write | 67 tools / 9 min |
| a855d759b002d2fe3 | critic | Pressure-test negative-result defensibility per candidate scope | FAILED — stalled writing report (heredoc loop) | watchdog killed at 600s |

## Session ca361725-3bee-4d0c-96d1-dab8c77e534a — earlier — broad survey + initial critic

Prior session that produced the 4 candidates and critic-shortlist. Auto-synced retroactively. To map agentId → candidate, read first ~500 chars of each `agent-<id>.jsonl` (the user prompt names the candidate slug).

| agentId | Persona | Task (inferred from opening prompt) |
|---|---|---|
| a187184cc0e1e2f15 | pain-point-researcher | broad-survey candidate |
| a209c3deb24f0b9a5 | critic | critic-shortlist pass on selection-shortlist |
| a8bfbe6b23991e861 | pain-point-researcher | broad-survey candidate |
| a94f958237788842c | (general) | what is CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS — meta lookup |
| aa3a25402b3a9197d | pain-point-researcher | broad-survey candidate |
| ac393d1f1cf8ebbef | pain-point-researcher | broad-survey candidate |
