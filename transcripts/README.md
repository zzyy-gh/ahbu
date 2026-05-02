# Subagent transcripts

Raw JSONL transcripts of every sub-agent invocation in this project.

## Source

Claude Code persists each sub-agent's full message history at:
```
~/.claude/projects/<project-key>/<session-id>/subagents/agent-<agentId>.jsonl
```

These are the **true raw** transcripts — every tool call the agent made, every tool result it saw, every assistant message it produced. They are not the same as the `.output` placeholder files under `%TEMP%\claude\.../tasks/` which are 0 bytes on this Windows configuration.

## How they get here

`bin/sync-transcripts.ps1` mirrors any new `agent-*.jsonl` files from the source path above into this folder, prefixed by session id. It is idempotent.

A git `pre-commit` hook installed by `bin/install-hooks.ps1` runs the sync before every commit, so the transcripts that produced the artifacts in a given commit are committed alongside them.

## Naming

- Auto-synced files keep the form `<session-id>_agent-<agentId>.jsonl`.
- Some early files (2026-05-02) were renamed by hand to `<date>_<persona>_<topic>.jsonl` for browsability — see `MANIFEST.md` for the agentId mapping.

## File format

JSONL — one JSON object per line. Each line is a Claude Code session event: user message, assistant message (with tool_use blocks), tool result, system reminder. Read with `jq`, a JSONL viewer, or any text editor.

## Why keep them in git

Framework evaluation. The AHBU project uses a multi-agent + critic-pass setup; whether that setup adds value over a single-agent run is itself an open question. Raw transcripts let us go back and inspect what each agent actually did rather than relying on its self-summary.
