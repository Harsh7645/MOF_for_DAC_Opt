param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_.-]+$')][string]$UserName,
    [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$Endpoint = '10.5.18.100',
    [ValidateRange(1,65535)][int]$Port = 22
)
# Run in the user's own terminal. No transcript, password variable, or prompt capture.
# For a new host, verify the displayed key via trusted institute information BEFORE yes.
$ErrorActionPreference = 'Stop'
Write-Host 'Passwords/CAPTCHA/2FA belong only in this SSH terminal. No credentials are saved.'
Write-Host 'New host key: compare fingerprint with institute-provided trusted information. If unavailable, stop.'
& ssh -p $Port -o StrictHostKeyChecking=ask -o ConnectTimeout=15 "$UserName@$Endpoint"
if ($LASTEXITCODE -ne 0) { throw "SSH ended with exit $LASTEXITCODE" }
