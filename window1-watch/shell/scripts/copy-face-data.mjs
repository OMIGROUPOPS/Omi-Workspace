import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const shellRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(shellRoot, "..", "data", "altgas.face.json");
const destination = resolve(shellRoot, "public", "data", "altgas.face.json");

mkdirSync(dirname(destination), { recursive: true });
copyFileSync(source, destination);
console.log(`copied ${source} -> ${destination}`);
