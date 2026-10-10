param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[a-zA-Z0-9_.-]+$')][string]$UserName,
    [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$Endpoint = '10.5.18.100',
    [ValidateRange(1,65535)][int]$Port = 22,
    [Parameter(Mandatory=$true)][string]$OutputFile
)
# Run in the user's own terminal AFTER first-login enrollment and trusted host verification.
# No transcript or stderr capture: authentication prompts stay in the terminal.
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputFile) { throw 'Preserve existing discovery evidence; choose a new path.' }
$body = "echo PARAM_SHAKTI_DISCOVERY_BEGIN`n" + [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'discover.sh'))
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($body.Replace("`r`n","`n")))
$remoteCommand = "printf '%s' '$encoded' | base64 -d | bash -l"
$script:insideDiscovery = $false
& ssh -p $Port -o StrictHostKeyChecking=yes -o ConnectTimeout=15 "$UserName@$Endpoint" $remoteCommand | ForEach-Object {
    if ($_ -eq 'PARAM_SHAKTI_DISCOVERY_BEGIN') { $script:insideDiscovery = $true }
    if ($script:insideDiscovery) {
        $_ | Add-Content -LiteralPath $OutputFile -Encoding UTF8
        Write-Host $_
    }
}
if ($LASTEXITCODE -ne 0) { throw "SSH discovery exit $LASTEXITCODE; keep any partial evidence." }
if (-not $script:insideDiscovery) { throw 'No authenticated discovery marker received.' }
