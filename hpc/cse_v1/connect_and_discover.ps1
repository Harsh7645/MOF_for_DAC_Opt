# Interactive first-use enrollment authorized by user; no credential capture.
# Run in a visible user terminal. Never transcript this session.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $projectRoot
Write-Host 'CSE cluster: 23BT10034@10.5.18.100. No compute job will be submitted.'
Write-Host 'First-use trust: review the SSH host-key prompt here. A changed key remains blocked.'
Write-Host 'Enter yes only if you choose to trust this first connection. Enter passwords only at SSH prompts.'
Write-Host 'The first connection performs only true, then closes. Discovery may ask for your password again.'
& ssh -t -p 22 -o StrictHostKeyChecking=ask -o ConnectTimeout=15 23BT10034@10.5.18.100 true
if ($LASTEXITCODE -ne 0) { throw 'First login failed; discovery was not started. No key-check bypass.' }
$evidence = Join-Path $projectRoot 'artifacts/phase3/cse_preparation_20261007'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$publicKeyFile = Join-Path $evidence "user_accepted_host_key_$stamp.txt"
& ssh-keygen -F 10.5.18.100 | Set-Content -LiteralPath $publicKeyFile -Encoding ascii
if ($LASTEXITCODE -ne 0) { throw 'No saved public key after login; stop before discovery.' }
Write-Host 'Saved host key reflects your first-use acceptance, not independent institutional verification.'
& (Join-Path $PSScriptRoot 'discover.ps1') -OutputFile (Join-Path $evidence "discovery_$stamp.txt")
Write-Host 'Read-only discovery finished. Return to chat. No jobs submitted or remote directories created.'
