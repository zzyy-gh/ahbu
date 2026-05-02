# Sync raw subagent JSONL transcripts from ~/.claude/projects/<project>/<session>/subagents/
# into ./transcripts/ in this repo. Idempotent. New files only.
#
# Usage: pwsh bin/sync-transcripts.ps1
# Wire as git pre-commit hook by running: pwsh bin/install-hooks.ps1

$ErrorActionPreference = "Stop"

$repoRoot = (git rev-parse --show-toplevel).Trim()
$projectKey = "C--Users-zzyy-Desktop-ahbu"
$srcRoot = Join-Path $env:USERPROFILE ".claude\projects\$projectKey"
$dstDir = Join-Path $repoRoot "transcripts"

if (-not (Test-Path $srcRoot)) {
    Write-Host "No subagent source dir found at $srcRoot — nothing to sync."
    exit 0
}
if (-not (Test-Path $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir | Out-Null
}

$copied = 0
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

if ($copied -eq 0) {
    Write-Host "All subagent transcripts already synced."
} else {
    Write-Host "Synced $copied new transcript(s)."
    git add $dstDir 2>$null
}
