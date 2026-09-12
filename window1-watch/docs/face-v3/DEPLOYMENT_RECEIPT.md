# FACE v3 deployment

Public preview verified on 2026-09-12 without login:

https://omi-window1-watch-dggdsxoyo-omi-groups-projects.vercel.app/?tab=lab&event=KXATPMATCH-26JUL12ALTGAS&gate=480

Deployment: `dpl_3q4SkRQQB97rUiJeUvQxcz48esKY`, READY, preview target. It contains only the reviewed static output. The upload directory is content-addressed to prevent retaining stale bundles.

VERIFY_HOSTED.json: all five grades and face hashes match local inputs; two oracle paths and gap strips per game; bid-card reasons; fixed receipt inspection; game/gate keyboard shortcuts; prepared-face import/source rejection; all three tabs; zero JavaScript page errors. The three `*-built.png` desktop screenshots now show this actual public preview, not a mockup.

Project: `omi-window1-watch`, root `window1-watch/shell`, `npm run build:demo`, `dist-demo`, Node 24.x. Configured project environment-variable list is empty. Git connection and branch read back successfully: `OMIGROUPOPS/Omi-Workspace`, production `face/window1-watch-20260903`. Stable assigned domain: https://omi-window1-watch.vercel.app. The old obm10302k URL remains an immutable older preview; use the current preview or verified stable deployment.

No engine/OS, tape, grade or rubric changes. DESK remains disconnected. Raw-tape LAB execution is not yet connected; full original stage/renewal streams remain local. These limits are described in BUILD_RECEIPT.md and on the page.

## Stable-domain verification

The Git push of `52bf0665b1578bcf0b39c23ff0490331b98a8cce` triggered production deployment `dpl_BVBBWtSxPmxBqWHC1veQYk6TCSyc` on the correct branch. It was still cloning the large repository at this check; that Git build is not certified complete here.

To make the stable demo available immediately, the already-verified static preview was promoted. Vercel created production deployment `dpl_9CHN5tb4smy1c3YGUxQ8cC9hPBKS`, READY. https://omi-window1-watch.vercel.app was tested independently without login: five unchanged face/grade bindings, all three tabs, oracle/gap paths, bid reasons, keyboard controls, import rejection and zero JavaScript page errors. See VERIFY_PRODUCTION.json. This verifies the stable site, not completion of the separate repository build.
