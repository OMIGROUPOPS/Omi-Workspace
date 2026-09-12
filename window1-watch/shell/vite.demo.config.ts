import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
// Local LAB reads original gzip stages without shipping them in the static build.
// @ts-expect-error Local JavaScript middleware
import { faceDataPlugin } from "./scripts/face-data-plugin.mjs";

// Static-only deployment entry: the same face components, no OS, auth, DB,
// server handlers, preview-host bridge, or environment-file loading.
const at = (path: string) => fileURLToPath(new URL(path, import.meta.url));
export default defineConfig({
  root: at("./demo/"),
  publicDir: at("./.demo-public/"),
  envDir: false,
  envPrefix: [],
  resolve: { alias: { "@": at("./src/") } },
  plugins: [tailwindcss(), react(), faceDataPlugin()],
  build: { outDir: at("./dist-demo/"), emptyOutDir: true, sourcemap: false },
});
