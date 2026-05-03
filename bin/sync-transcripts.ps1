# Sync raw JSONL transcripts from ~/.claude/projects/<project>/ into ./transcripts/.
# Two transcript kinds, both copied:
#   1. Main-agent orchestration: <project>/<session>.jsonl
#      Captures the orchestrator's tool calls — Agent spawns, SendMessage
#      between teammates, hooks, and result stitching. Copied as
#      session_<session>.jsonl.
#   2. Subagent internals: <project>/<session>/subagents/agent-<agentId>.jsonl
#      Each spawned subagent's own transcript. Copied as
#      <session>_agent-<agentId>.jsonl.
# Idempotent. New files only. Existing files are refreshed if the source
# has grown (the active session's main jsonl appends as the session runs).
#
# Usage: pwsh bin/sync-transcripts.ps1
# Wire as git pre-commit hook by running: pwsh bin/install-hooks.ps1

$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$projectKey = "C--Users-zzyy-Desktop-ahbu"
$srcRoot = Join-Path $env:USERPROFILE ".claude\projects\$projectKey"
$dstDir = Join-Path $repoRoot "transcripts"

if (-not (Test-Path $srcRoot)) {
    Write-Host "No transcript source dir found at $srcRoot — nothing to sync."
    exit 0
}
if (-not (Test-Path $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir | Out-Null
}

$copied = 0
$refreshed = 0

# 1. Main-agent orchestration transcripts (top-level <session>.jsonl).
Get-ChildItem -Path $srcRoot -Filter "*.jsonl" -File | ForEach-Object {
    $dstName = "session_$($_.BaseName).jsonl"
    $dstPath = Join-Path $dstDir $dstName
    if (-not (Test-Path $dstPath)) {
        Copy-Item $_.FullName $dstPath
        Write-Host "Copied $dstName"
        $copied++
    } elseif ($_.Length -ne (Get-Item $dstPath).Length) {
        # Active session jsonl grows as the session runs — refresh in place.
        Copy-Item $_.FullName $dstPath -Force
        Write-Host "Refreshed $dstName"
        $refreshed++
    }
}

# 2. Subagent transcripts (<session>/subagents/agent-*.jsonl).
Get-ChildItem -Path $srcRoot -Recurse -Filter "agent-*.jsonl" | ForEach-Object {
    $sessionDir = $_.Directory.Parent.Name
    $dstName = "$sessionDir`_$($_.Name)"
    $dstPath = Join-Path $dstDir $dstName
    if (-not (Test-Path $dstPath)) {
        Copy-Item $_.FullName $dstPath
        Write-Host "Copied $dstName"
        $copied++
    }
}

if ($copied -eq 0 -and $refreshed -eq 0) {
    Write-Host "All transcripts already synced."
} else {
    Write-Host "Synced $copied new transcript(s); refreshed $refreshed."
    git add $dstDir 2>$null
}
