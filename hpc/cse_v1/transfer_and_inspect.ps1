# User terminal only; password prompts never redirected or transcribed.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location -LiteralPath $projectRoot
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$evidence = Join-Path $projectRoot 'artifacts/phase3/cse_preparation_20261007'
$remoteRoot = "/home/others/23BT10034/mof_dac_qe75_v2_$stamp"
$remoteRoot | Set-Content -LiteralPath (Join-Path $evidence "transfer_target_$stamp.txt") -Encoding ascii
$sshOptions = @('-p','22','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=15')
function Invoke-RecordedRemote([string]$Body,[string]$Name) {
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Body.Replace("`r`n","`n")))
    $command = "printf '%s' '$encoded' | base64 -d | bash -l"
    $inside = $false
    & ssh @sshOptions 23BT10034@10.5.18.100 $command | ForEach-Object {
        if ($_ -eq 'CSE_STAGE_BEGIN') { $inside = $true }
        if ($inside) {
            $_ | Add-Content -LiteralPath (Join-Path $evidence "${Name}_$stamp.txt") -Encoding UTF8
            Write-Host $_
        }
    }
    if ($LASTEXITCODE -ne 0 -or -not $inside) { throw "Remote $Name failed; retain all partial files." }
}
$stageSource = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'stage_remote.py')).Replace("`r`n","`n")
$followup = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'discover_followup.sh')).Replace("`r`n","`n")
Write-Host 'CSE staging: read-only discovery plus upload/verification. No compute job or build.'
Write-Host 'SSH/SCP may each prompt for your password here. No passwords are stored.'
Invoke-RecordedRemote -Name 'followup_and_create' -Body "echo CSE_STAGE_BEGIN`n$followup`npython3 - create '$remoteRoot' <<'CSE_PYTHON_END'`n$stageSource`nCSE_PYTHON_END`n"
& scp -P 22 -o StrictHostKeyChecking=yes -r artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json hpc/cse_v1 "23BT10034@10.5.18.100:${remoteRoot}/"
if ($LASTEXITCODE -ne 0) { throw 'SCP failed; remote project retained. No retry or deletion.' }
Invoke-RecordedRemote -Name 'remote_verification' -Body "echo CSE_STAGE_BEGIN`npython3 '$remoteRoot/cse_v1/stage_remote.py' verify '$remoteRoot'`n"
Write-Host 'Staging complete. Return to chat; no jobs submitted. All remote files retained.'
