[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$GateFile,
    [Parameter(Mandatory=$true)][string]$GateReceipt,
    [Parameter(Mandatory=$true)][string]$OutputRoot
)
$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Users\omigr\omi-w1-face'
$taskPython = 'C:\Users\omigr\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskPrivate = 'C:\tmp\feature_panel_v1'
$taskOut = [System.IO.Path]::GetFullPath($OutputRoot)
if (-not $taskOut.StartsWith('C:\tmp\', [StringComparison]::OrdinalIgnoreCase)) { throw 'PRIVATE_OUTPUT_MUST_BE_UNDER_C_TMP' }
if (-not (Test-Path -LiteralPath $GateFile) -or -not (Test-Path -LiteralPath $GateReceipt)) { throw 'VERIFIED_GATE_INPUTS_REQUIRED' }
if (-not (Test-Path -LiteralPath $taskOut)) { New-Item -ItemType Directory -Path $taskOut | Out-Null }
$taskLock = [System.IO.File]::Open((Join-Path $taskOut 'SCREEN_QUEUE.lock'),'OpenOrCreate','ReadWrite','None')
try {
    foreach ($taskCategory in @('ATP_MAIN','ATP_CHALL')) {
        foreach ($taskPass in @('pass1','pass2')) {
            $taskDestination = Join-Path (Join-Path $taskOut $taskPass) $taskCategory
            if (Test-Path -LiteralPath $taskDestination) { throw ('REFUSE_EXISTING_SCREEN_OUTPUT ' + $taskDestination) }
            $taskArguments = @('-B','arb-executor/analysis/feature_panel_inventory_atlas_run.py',
                '--root',$taskRoot,'--sources',(Join-Path $taskPrivate 'FEATURE_SOURCES.jsonl.gz'),
                '--witnesses',(Join-Path $taskPrivate 'POSITIVE_PRINT_WITNESSES.jsonl.gz'),
                '--supplemental',(Join-Path $taskPrivate 'SUPPLEMENTAL_AVAILABILITY.jsonl.gz'),
                '--source-receipt',(Join-Path $taskPrivate 'FEATURE_EXTRACT_RECEIPT.json'),
                '--supplemental-receipt',(Join-Path $taskPrivate 'SUPPLEMENTAL_AVAILABILITY_RECEIPT.json'),
                '--core-extractor','arb-executor/analysis/feature_panel_v1/source/feature_panel_extract.24bfeb8f.py',
                '--odds-audit-receipt','C:\tmp\odds_coverage_20260908\ODDS_COVERAGE_RECEIPT.json',
                '--category',$taskCategory,'--out',$taskDestination,'--inventory-gates',$GateFile,
                '--inventory-receipt',$GateReceipt,'--cache-budget-mib','512','--state-cache-mib','128',
                '--batch-size','16','--workers','1')
            $taskPrefix = Join-Path $taskOut ($taskCategory + '_' + $taskPass)
            $taskChild = Start-Process $taskPython -ArgumentList $taskArguments -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput ($taskPrefix+'.log') -RedirectStandardError ($taskPrefix+'.err') -PassThru
            $null = $taskChild.Handle
            Write-Output ('SCREEN_START ' + $taskCategory + ' ' + $taskPass + ' pid=' + $taskChild.Id)
            $taskChild.WaitForExit()
            $taskChild.Refresh()
            [System.IO.File]::WriteAllText(($taskPrefix+'.exit'),[string]$taskChild.ExitCode)
            if ($taskChild.ExitCode -ne 0) { throw ('SCREEN_FAILED ' + $taskCategory + ' ' + $taskPass) }
            if (-not (Test-Path -LiteralPath (Join-Path $taskDestination 'ATLAS_SCREEN_RESULTS.json'))) { throw 'SCREEN_RESULT_MISSING' }
            Write-Output ('SCREEN_PASS_COMPLETE ' + $taskCategory + ' ' + $taskPass)
        }
    }
    Write-Output 'SCREENS_FINISHED_REQUIRES_DETERMINISM_FIRST_PARITY_AND_PUBLICATION_REVIEW'
    [System.IO.File]::WriteAllText((Join-Path $taskOut 'SCREEN_QUEUE.exit'),'0')
} catch {
    [System.IO.File]::WriteAllText((Join-Path $taskOut 'SCREEN_QUEUE.exit'),'1')
    throw
} finally {
    $taskLock.Dispose()
}
