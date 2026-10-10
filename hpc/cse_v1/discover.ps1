param(
    [ValidatePattern('^[a-zA-Z0-9_.-]+$')][string]$UserName = '23BT10034',
    [string]$KnownHostsFile,
    [Parameter(Mandatory=$true)][string]$OutputFile
)
# Run in user's interactive PowerShell. Never transcript or capture authentication stderr.
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $OutputFile) { throw 'Preserve prior evidence; choose a new output path.' }
$sshOptions = @('-p', '22', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=15')
if ($KnownHostsFile) {
    $trustedFile = (Resolve-Path -LiteralPath $KnownHostsFile).Path.Replace('\','/')
    $sshOptions += @('-o', ('UserKnownHostsFile="{0}"' -f $trustedFile))
}
$body = "echo CSE_DISCOVERY_BEGIN`n" + [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'discover.sh'))
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($body.Replace("`r`n","`n")))
$remoteCommand = "printf '%s' '$encoded' | base64 -d | bash -l"
$script:insideDiscovery = $false
& ssh @sshOptions "$UserName@10.5.18.100" $remoteCommand | ForEach-Object {
    if ($_ -eq 'CSE_DISCOVERY_BEGIN') { $script:insideDiscovery = $true }
    if ($script:insideDiscovery) {
        $_ | Add-Content -LiteralPath $OutputFile -Encoding UTF8
        Write-Host $_
    }
}
if ($LASTEXITCODE -ne 0) { throw "SSH discovery exit $LASTEXITCODE; preserve partial evidence." }
if (-not $script:insideDiscovery) { throw 'No authenticated discovery marker received.' }
