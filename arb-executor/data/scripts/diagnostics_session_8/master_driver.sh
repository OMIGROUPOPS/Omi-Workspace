#!/bin/bash
# Master driver for Session 8 overnight diagnostic chain.
# Runs 9 self-contained category scripts in priority order.
# Each category writes ASCII report + sha256 digest to data/durable/diagnostics_session_8/.
# Failure of any single category does NOT abort the chain; master logs and continues.
# Final summary written to summary.txt with per-category status.

export TZ='America/New_York'
cd ~/Omi-Workspace/arb-executor

SCRIPTS_DIR=~/Omi-Workspace/arb-executor/data/scripts/diagnostics_session_8
OUTPUT_DIR=~/Omi-Workspace/arb-executor/data/durable/diagnostics_session_8
LOG=$OUTPUT_DIR/master.log
SUMMARY=$OUTPUT_DIR/summary.txt

mkdir -p "$OUTPUT_DIR"

START_TS=$(date '+%Y-%m-%d %H:%M:%S %Z')
echo "=== Master driver start: $START_TS ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# Order: Cat 5, 2, 9, 7, 10, 8, 6, 1, 3
declare -a CATEGORIES=(
    "05:alpha_discovery:Layer B alpha ranking"
    "02:fee_table:Empirical fee table"
    "09:distortion_events:Combined-price distortion events"
    "07:oi_reconstruction:Per-minute OI reconstruction"
    "10:oi_asymmetry:Per-side OI asymmetry"
    "08:formation_gate:Formation gate distribution"
    "06:trajectory_width:Premarket trajectory width"
    "01:within_band:Within-band heterogeneity"
    "03:formation_contam:Formation contamination"
)

declare -a STATUSES=()
declare -a RUNTIMES=()
declare -a SHA256S=()

for entry in "${CATEGORIES[@]}"; do
    IFS=':' read -r CAT_NUM CAT_NAME CAT_LABEL <<< "$entry"
    SCRIPT="$SCRIPTS_DIR/cat_${CAT_NUM}_${CAT_NAME}.py"
    OUTPUT="$OUTPUT_DIR/cat_${CAT_NUM}_${CAT_NAME}.txt"
    SHA="$OUTPUT_DIR/cat_${CAT_NUM}_${CAT_NAME}.sha256"

    CAT_START=$(date '+%Y-%m-%d %H:%M:%S %Z')
    CAT_START_EPOCH=$(date +%s)
    echo "--- [$CAT_START] Cat $CAT_NUM ($CAT_LABEL) START ---" | tee -a "$LOG"

    if nice -n 10 python3 "$SCRIPT" > "$OUTPUT" 2>&1; then
        sha256sum "$OUTPUT" | cut -d ' ' -f 1 > "$SHA"
        SHA_VAL=$(cat "$SHA")
        CAT_END_EPOCH=$(date +%s)
        ELAPSED=$((CAT_END_EPOCH - CAT_START_EPOCH))
        STATUSES+=("OK")
        RUNTIMES+=("$ELAPSED")
        SHA256S+=("$SHA_VAL")
        echo "    Cat $CAT_NUM OK in ${ELAPSED}s (sha256: ${SHA_VAL:0:16}...)" | tee -a "$LOG"
    else
        EXIT_CODE=$?
        CAT_END_EPOCH=$(date +%s)
        ELAPSED=$((CAT_END_EPOCH - CAT_START_EPOCH))
        STATUSES+=("FAIL_EXIT_$EXIT_CODE")
        RUNTIMES+=("$ELAPSED")
        SHA256S+=("(no output)")
        echo "    Cat $CAT_NUM FAIL (exit $EXIT_CODE) after ${ELAPSED}s — chain continues" | tee -a "$LOG"
        echo "    Last 20 lines of output:" | tee -a "$LOG"
        tail -20 "$OUTPUT" 2>/dev/null | sed 's/^/      /' | tee -a "$LOG"
    fi
    echo "" | tee -a "$LOG"
done

END_TS=$(date '+%Y-%m-%d %H:%M:%S %Z')
echo "=== Master driver end: $END_TS ===" | tee -a "$LOG"

# === Summary ===
{
    echo "Diagnostic chain summary"
    echo "Start: $START_TS"
    echo "End:   $END_TS"
    echo ""
    echo "Per-category results:"
    printf '%s\n' "${CATEGORIES[@]}" | while IFS=':' read -r CAT_NUM CAT_NAME CAT_LABEL; do
        idx=$((10#$CAT_NUM - 1))
        # Adjust: CATEGORIES is in order 05,02,09,07,10,08,06,01,03 — so use a counter not raw num
        :
    done
    echo ""
    echo "Order  Cat  Name                     Status              Runtime    SHA256(first 16)"
    echo "---------------------------------------------------------------------------------"
    for i in "${!CATEGORIES[@]}"; do
        IFS=':' read -r CAT_NUM CAT_NAME CAT_LABEL <<< "${CATEGORIES[$i]}"
        STATUS="${STATUSES[$i]}"
        RUNTIME="${RUNTIMES[$i]}"
        SHA="${SHA256S[$i]}"
        SHA_SHORT="${SHA:0:16}"
        printf "%-6s %-4s %-24s %-19s %5ss      %s\n" "$((i+1))" "$CAT_NUM" "$CAT_NAME" "$STATUS" "$RUNTIME" "$SHA_SHORT"
    done
    echo ""
    echo "Outputs: $OUTPUT_DIR/cat_*.txt"
    echo "Sha256:  $OUTPUT_DIR/cat_*.sha256"
    echo "Log:     $LOG"
} > "$SUMMARY"

cat "$SUMMARY"

# Exit 0 if Cat 5 (index 0), Cat 2 (index 1), Cat 9 (index 2) all OK; else exit 1
if [ "${STATUSES[0]}" = "OK" ] && [ "${STATUSES[1]}" = "OK" ] && [ "${STATUSES[2]}" = "OK" ]; then
    exit 0
else
    exit 1
fi
