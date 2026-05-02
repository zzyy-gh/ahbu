# Install git pre-commit hook that runs sync-transcripts before every commit.
# Run once after cloning: pwsh bin/install-hooks.ps1

$ErrorActionPreference = "Stop"
$repoRoot = (git rev-parse --show-toplevel).Trim()
$hookPath = Join-Path $repoRoot ".git\hooks\pre-commit"

@'
#!/bin/sh
# Auto-installed by bin/install-hooks.ps1
pwsh -NoProfile -File "$(git rev-parse --show-toplevel)/bin/sync-transcripts.ps1"
'@ | Set-Content -Path $hookPath -Encoding ASCII -NoNewline

Write-Host "Installed pre-commit hook at $hookPath"
