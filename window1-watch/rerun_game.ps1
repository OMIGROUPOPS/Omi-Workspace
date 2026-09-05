[CmdletBinding()]
param([Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Event,
      [string]$Custody, [string]$Bench,
      [string]$TapeDir = 'C:\Users\omigr\OMI-Window1-private\fit-local\ticks')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Set-Location -LiteralPath $repoRoot
if ((& git rev-parse --show-toplevel).Trim().Replace('/','\').TrimEnd('\') -ne $repoRoot.TrimEnd('\')) { throw 'Wrong worktree' }
$builderPath = Join-Path $repoRoot 'arb-executor\analysis\build_window1_v54_dual_belief.js'
$osPath = Join-Path $repoRoot 'arb-executor\analysis\window1_v54_dual_belief_os.js'
$receiptDir = $null
$tracePath = $null
if ($Custody) {
  $resolvedCustody = (Resolve-Path -LiteralPath $Custody).Path
  $tracePath = if (Test-Path -LiteralPath $resolvedCustody -PathType Leaf) { $resolvedCustody } else { Join-Path $resolvedCustody 'REPAIR_FOUR_GAME_TRACE.jsonl.gz' }
  if (-not (Test-Path -LiteralPath $tracePath -PathType Leaf)) { throw "No custody trace: $tracePath" }
} else {
  $cachedFace = Join-Path $PSScriptRoot "data\$Event.face.json"
  if (Test-Path -LiteralPath $cachedFace) {
    $cached = Get-Content -Raw -LiteralPath $cachedFace | ConvertFrom-Json
    if ($cached.provenance.trace_path -and (Test-Path -LiteralPath $cached.provenance.trace_path)) { $tracePath = $cached.provenance.trace_path }
  }
  if (-not $tracePath) {
    $candidates = @(Get-ChildItem -LiteralPath 'C:\tmp' -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'v54*' } | ForEach-Object {
      foreach ($relative in @('REPAIR_FOUR_GAME_TRACE.jsonl.gz','KEEP\REPAIR_FOUR_GAME_TRACE.jsonl.gz')) {
        $candidatePath = Join-Path $_.FullName $relative
        if (Test-Path -LiteralPath $candidatePath) { Get-Item -LiteralPath $candidatePath }
      }
    } | Sort-Object LastWriteTime -Descending | ForEach-Object { $_.FullName })
    if ($candidates.Count) {
      $found = & node (Join-Path $PSScriptRoot 'locate_trace.mjs') $Event @candidates
      if ($LASTEXITCODE -eq 0 -and $found) { $tracePath = [string]$found }
    }
  }
}
if (-not $tracePath) {
  $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  $Custody = Join-Path $PSScriptRoot ".runtime\custody_$($Event)_$stamp"
  $receiptDir = Join-Path $Custody 'receipts'
  New-Item -ItemType Directory -Path $receiptDir -Force | Out-Null
  $frozenRepo = 'C:\tmp\omi-v54-four-game-trace-92a4d839-retry-20260901'
  $foundation = Join-Path $frozenRepo '.claude\window1_live_v4_replay\v54_classifier_floor_print_wake_20260826'
  Copy-Item -LiteralPath (Join-Path $frozenRepo '.claude\window1_20260721\SOURCE_COVERAGE_SUMMARY.json') -Destination $receiptDir
  $originalBytes = [IO.File]::ReadAllBytes($builderPath)
  $source = [Text.Encoding]::UTF8.GetString($originalBytes)
  $stories = [regex]::Match($source, '(?s)stories:\s*\[(.*?)\]')
  if (-not $stories.Success) { throw 'TARGETS.stories was not found' }
  $replacement = $source
  if ($stories.Value -notmatch [regex]::Escape('"' + $Event + '"')) {
    # The saved fifth story is the ALTGAS extra. Retain the four bed stories and
    # append the requested extra on that same line, never accumulate a sixth game.
    $bedStories = $stories.Value.Replace(', "KXATPMATCH-26JUL12ALTGAS"','')
    $lastQuote = $bedStories.LastIndexOf('"')
    if ($lastQuote -lt 0) { throw 'No stories line to append to' }
    $newStories = $bedStories.Insert($lastQuote + 1, ', "' + $Event + '"')
    $replacement = $source.Substring(0,$stories.Index) + $newStories + $source.Substring($stories.Index+$stories.Length)
  }
  $osBefore = (Get-FileHash -LiteralPath $osPath -Algorithm SHA256).Hash.ToLowerInvariant()
  # Operator-authorized exception: a same-line stories append, restored byte-for-byte even on failure.
  try {
    if ($replacement -ne $source) { [IO.File]::WriteAllText($builderPath,$replacement,[Text.UTF8Encoding]::new($false)) }
    & node $builderPath --repo $repoRoot --cache 'C:\tmp\v54-corpus-cache-recovered-20260826' `
      --private 'C:\Users\omigr\OMI-Window1-private' `
      --walk 'C:\tmp\omi-v53-understanding-organ-20260819\.claude\window1_live_v4_replay\v54_walk5_repair_v6_20260821' `
      --output $receiptDir --foundation-index (Join-Path $foundation 'FOUNDATION_LIBRARY.jsonl.gz') `
      --foundation-receipt (Join-Path $foundation 'FOUNDATION_LIBRARY_RECEIPT.json') `
      --future-low-index (Join-Path $foundation 'FUTURE_LOW_RETURN_LIBRARY.jsonl.gz') `
      --future-low-receipt (Join-Path $foundation 'FUTURE_LOW_RETURN_LIBRARY_RECEIPT.json') `
      --remote-receipt 'C:\tmp\v54_committed_92a4d839_four_game_trace_retry_20260901\SOURCE_RECEIPTS.json' --custody-output $Custody
    if ($LASTEXITCODE -ne 0) { throw "Builder failed: $LASTEXITCODE" }
  } finally {
    [IO.File]::WriteAllBytes($builderPath,$originalBytes)
    $restored = [IO.File]::ReadAllBytes($builderPath)
    if ([Convert]::ToBase64String($restored) -cne [Convert]::ToBase64String($originalBytes)) { throw 'Builder restoration failed' }
  }
  $tracePath = Join-Path $Custody 'REPAIR_FOUR_GAME_TRACE.jsonl.gz'
  $runProvenance = @{ event=$Event; os_sha256=$osBefore; os_sha256_after=(Get-FileHash -LiteralPath $osPath -Algorithm SHA256).Hash.ToLowerInvariant(); trace_sha256=(Get-FileHash -LiteralPath $tracePath -Algorithm SHA256).Hash.ToLowerInvariant() }
  $runProvenance | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Custody 'FACE_RUN_PROVENANCE.json') -Encoding utf8
}
$dataRoot = Join-Path $PSScriptRoot 'data'
$exportPath = Join-Path $dataRoot "$Event.export.json"
$facePath = Join-Path $dataRoot "$Event.face.json"
& node (Join-Path $PSScriptRoot 'export_watch.mjs') --event $Event --trace $tracePath --tape-dir $TapeDir --manifest-only --out $exportPath
if ($LASTEXITCODE -ne 0) { throw "Exporter failed: $LASTEXITCODE" }
$faceArgs = @('--event',$Event,'--trace',$tracePath,'--tape-dir',$TapeDir,'--out',$facePath)
if ($receiptDir) { $faceArgs += @('--receipt-dir',$receiptDir) }
if ($Bench) { $faceArgs += @('--bench',$Bench) }
& node (Join-Path $PSScriptRoot 'build_face_data.mjs') @faceArgs
if ($LASTEXITCODE -ne 0) { throw "Face builder failed: $LASTEXITCODE" }
& node (Join-Path $PSScriptRoot 'shell\scripts\copy-face-data.mjs')
if ($LASTEXITCODE -ne 0) { throw 'Face data publication failed' }
& node (Join-Path $PSScriptRoot 'verify_game.mjs') $facePath
if ($LASTEXITCODE -ne 0) { throw 'Verification failed' }
