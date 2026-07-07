#!/bin/bash
# [C47-ENFORCE] commit+push an AUDIT HALT alert artifact. Invoked detached by
# live_v4's post-boot audit on FAIL; never blocks trading (best-effort).
set -e
ART="$1"
[ -f "$ART" ] || exit 1
cd /root/Omi-Workspace
BR="$(git rev-parse --abbrev-ref HEAD)"
git add "$ART"
git commit -m "AUDIT HALT artifact: $(basename "$ART") -- conceptions halted, exits working; clears on passing re-audit" || exit 0
git push origin "$BR" || true
