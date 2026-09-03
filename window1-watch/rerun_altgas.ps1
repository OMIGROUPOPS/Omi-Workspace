[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-File([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    throw "Required file is missing: $Path"
  }
}

function Require-Directory([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
    throw "Required directory is missing: $Path"
  }
}

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
Set-Location -LiteralPath $repoRoot
$gitRoot = (& git rev-parse --show-toplevel).Trim()
$normalizedGitRoot = $gitRoot.Replace("/", "\").TrimEnd("\")
if ($LASTEXITCODE -ne 0 -or -not [string]::Equals($normalizedGitRoot, $repoRoot.TrimEnd("\"), [StringComparison]::OrdinalIgnoreCase)) {
  throw "git rev-parse did not resolve to $repoRoot (got: $gitRoot)"
}

$eventId = "KXATPMATCH-26JUL12ALTGAS"
$watchRoot = Join-Path $repoRoot "window1-watch"
$builderPath = Join-Path $repoRoot "arb-executor\analysis\build_window1_v54_dual_belief.js"
$osPath = Join-Path $repoRoot "arb-executor\analysis\window1_v54_dual_belief_os.js"
$exporterPath = Join-Path $watchRoot "export_watch.mjs"
$faceBuilderPath = Join-Path $watchRoot "build_face_data.mjs"
$indexPath = Join-Path $watchRoot "index.html"
$facePath = Join-Path $watchRoot "data\altgas.face.json"
$fieldsPath = Join-Path $watchRoot "FIELDS.md"

# Frozen inputs from the September 2 ALTGAS extra run.
$frozenRepo = "C:\tmp\omi-v54-four-game-trace-92a4d839-retry-20260901"
$cachePath = "C:\tmp\v54-corpus-cache-recovered-20260826"
$privateRoot = "C:\Users\omigr\OMI-Window1-private"
$tapeDir = Join-Path $privateRoot "fit-local\ticks"
$walkPath = "C:\tmp\omi-v53-understanding-organ-20260819\.claude\window1_live_v4_replay\v54_walk5_repair_v6_20260821"
$foundationRoot = Join-Path $frozenRepo ".claude\window1_live_v4_replay\v54_classifier_floor_print_wake_20260826"
$foundationIndex = Join-Path $foundationRoot "FOUNDATION_LIBRARY.jsonl.gz"
$foundationReceipt = Join-Path $foundationRoot "FOUNDATION_LIBRARY_RECEIPT.json"
$futureLowIndex = Join-Path $foundationRoot "FUTURE_LOW_RETURN_LIBRARY.jsonl.gz"
$futureLowReceipt = Join-Path $foundationRoot "FUTURE_LOW_RETURN_LIBRARY_RECEIPT.json"
$remoteReceipt = "C:\tmp\v54_committed_92a4d839_four_game_trace_retry_20260901\SOURCE_RECEIPTS.json"
$sourceCoverage = Join-Path $frozenRepo ".claude\window1_20260721\SOURCE_COVERAGE_SUMMARY.json"

@(
  $builderPath,
  $osPath,
  $exporterPath,
  $faceBuilderPath,
  $indexPath,
  $fieldsPath,
  $foundationIndex,
  $foundationReceipt,
  $futureLowIndex,
  $futureLowReceipt,
  $remoteReceipt,
  $sourceCoverage
) | ForEach-Object { Require-File $_ }
@($cachePath, $privateRoot, $tapeDir, $walkPath) | ForEach-Object { Require-Directory $_ }
$indexSource = Get-Content -Raw -LiteralPath $indexPath
if ($indexSource -notmatch 'data/altgas\.face\.json') {
  throw "Face-data hook prerequisite is missing from $indexPath"
}

# The real builder must carry the five-story target set. This script deliberately
# does not rewrite, copy, or compile a modified builder in memory.
$builderSource = Get-Content -Raw -LiteralPath $builderPath
$targetsMatch = [regex]::Match($builderSource, '(?s)const TARGETS = Object\.freeze\(\{.*?\r?\n\}\);')
if (-not $targetsMatch.Success) {
  throw "TARGETS block not found in the real builder: $builderPath"
}
$requiredStories = @(
  "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
  "KXATPCHALLENGERMATCH-26JUL14URSPAL",
  "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
  "KXATPMATCH-26JUL18DANPRA",
  $eventId
)
$missingStories = @($requiredStories | Where-Object { $targetsMatch.Value -notmatch [regex]::Escape($_) })
if ($missingStories.Count -gt 0) {
  throw "The real builder TARGETS.stories is missing: $($missingStories -join ', '). Refusing to recreate or modify the builder."
}

$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$custodyDir = "C:\tmp\v54_altgas_face_$stamp"
$receiptDir = "${custodyDir}_receipts"
if ((Test-Path -LiteralPath $custodyDir) -or (Test-Path -LiteralPath $receiptDir)) {
  throw "Fresh run path already exists for this minute: $custodyDir"
}

New-Item -ItemType Directory -Path $custodyDir | Out-Null
New-Item -ItemType Directory -Path $receiptDir | Out-Null
Copy-Item -LiteralPath $sourceCoverage -Destination (Join-Path $receiptDir "SOURCE_COVERAGE_SUMMARY.json")

$osSha256 = (Get-FileHash -LiteralPath $osPath -Algorithm SHA256).Hash.ToLowerInvariant()

& node $builderPath `
  --repo $repoRoot `
  --cache $cachePath `
  --private $privateRoot `
  --walk $walkPath `
  --output $receiptDir `
  --foundation-index $foundationIndex `
  --foundation-receipt $foundationReceipt `
  --future-low-index $futureLowIndex `
  --future-low-receipt $futureLowReceipt `
  --remote-receipt $remoteReceipt `
  --custody-output $custodyDir
if ($LASTEXITCODE -ne 0) { throw "ALTGAS builder exited with code $LASTEXITCODE" }

$tracePath = Join-Path $custodyDir "REPAIR_FOUR_GAME_TRACE.jsonl.gz"
Require-File $tracePath

& node $exporterPath --event $eventId --trace $tracePath --tape-dir $tapeDir --out (Join-Path $watchRoot "data\altgas.json")
if ($LASTEXITCODE -ne 0) { throw "export_watch.mjs exited with code $LASTEXITCODE" }

& node $faceBuilderPath
if ($LASTEXITCODE -ne 0) { throw "build_face_data.mjs exited with code $LASTEXITCODE" }
Require-File $facePath

$traceSha256 = (Get-FileHash -LiteralPath $tracePath -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "OS_SHA256 $osSha256"
Write-Output "TRACE_SHA256 $traceSha256"
Write-Output "CUSTODY_DIR $custodyDir"

$verification = @'
const fs = require("fs");
const facePath = process.argv[1];
const fieldsPath = process.argv[2];
const face = JSON.parse(fs.readFileSync(facePath, "utf8"));
const perLeg = (row) => row?.legs ?? row?.per_leg ?? row;
const os = Array.isArray(face.os) ? face.os : [];
const altRestRow = os.find((row) => perLeg(row)?.ALT?.rest != null);
if (!altRestRow) throw new Error("No ALT rest in altgas.face.json");
const alt = perLeg(altRestRow).ALT;
const sentence = alt.sentence ?? {};
console.log("FIRST_ALT_REST " + JSON.stringify({
  t: altRestRow.t,
  cents: alt.rest.cents,
  lane: alt.rest.lane,
  P: sentence.P,
  Q: sentence.Q,
  X: sentence.X,
}));

let fillEntry = null;
for (const row of os) {
  for (const leg of ["ALT", "GAS"]) {
    const fill = perLeg(row)?.[leg]?.fill;
    if (fill != null) {
      fillEntry = { leg, t: row.t, cents: fill.cents };
      break;
    }
  }
  if (fillEntry) break;
}
if (!fillEntry) throw new Error("No fill in altgas.face.json");
console.log("FILL " + JSON.stringify(fillEntry));

const altTape = Array.isArray(face.tape?.ALT) ? face.tape.ALT : [];
const gasTape = Array.isArray(face.tape?.GAS) ? face.tape.GAS : [];
console.log(`TAPE_ROWS ALT=${altTape.length} GAS=${gasTape.length} FACE_BYTES=${fs.statSync(facePath).size}`);

const bellHours = typeof face.bell === "number"
  ? face.bell
  : face.bell?.t ?? face.bell?.hours ?? face.bell?.hours_from_first_stage ?? face.bell?.hours_to_truth_bell_at_first_stage;
if (!Number.isFinite(bellHours)) throw new Error("No finite bell hour in altgas.face.json");
const lastBeforeBell = (rows) => rows.filter((row) => row.t <= bellHours && row.last != null).at(-1)?.last ?? null;
console.log(`LAST_BEFORE_BELL ALT=${lastBeforeBell(altTape)} GAS=${lastBeforeBell(gasTape)}`);

console.log("FIELDS.md");
process.stdout.write(fs.readFileSync(fieldsPath, "utf8").trimEnd() + "\n");
'@

& node -e $verification -- $facePath $fieldsPath
if ($LASTEXITCODE -ne 0) { throw "Verification report exited with code $LASTEXITCODE" }
