# Static face demo

Vercel project: `omi-window1-watch`. Git root directory: `window1-watch/shell`.
Production branch: `face/window1-watch-20260903` (configure in the Vercel project).

`npm run build:demo` makes a production Vite build of the existing `TuneTest`
components. It does not import the engine, server/auth/database scaffolding,
preview-host bridge, environment files, or perform database migrations.
`npm run preview:demo` serves that production output locally on port 8082.

The asset prep reads the five entries in `../data/index.json`, copies the exact
face and grade bytes, verifies each grade's face/OS/trace binding, and decompresses
each oracle with its stored SHA verification. The picker and history indexes are
included. `.demo-public/demo-assets.json` records asset sizes and hashes.
The old `public/data` folder is deliberately not an input to this build.
No data is regenerated and no game number changes.

Full stage and per-tick accountability files exceed the operator's 50 MB cap,
so they remain local. The hosted inspector reports STORE SILENT for those files;
compact bid cards, floors, grades, oracle paths, and history remain available.

No Vercel environment variables are required. Use preview target first.
Deploy only the prebuilt static output, not the repository or raw data directories.
After linking the shell project, `node scripts/package-demo.mjs` scans the output
and assembles `.vercel/demo-upload/.vercel/output` (static files only). From that
upload directory run `vercel deploy --prebuilt --target=preview` and verify the
reported target: Vercel may automatically assign a new project's first upload
to production. `node scripts/verify-demo.mjs <preview-url>` checks the picker,
grade/oracle bindings, recorded floors, ALT bid-card hover, and excluded stage
404, saving screenshots locally under `.vercel/demo-check`.
Git builds use `vercel.json` and require access to the committed `../data` inputs
(enable files outside the root directory). Future pushes to the configured
production branch rebuild those same allowlisted assets.
