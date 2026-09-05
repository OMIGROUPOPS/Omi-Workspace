import { cpSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const shellRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(shellRoot, "..", "data");
const destination = resolve(shellRoot, "public", "data");

mkdirSync(dirname(destination), { recursive: true });
cpSync(source, destination, { recursive: true, filter: (file) => !file.endsWith('.export.json') && !file.endsWith('.tmp') && !file.endsWith('/altgas.json') && !file.endsWith('\\altgas.json') && !(file.includes('.stages') && file.endsWith('.json')) });
console.log(`copied ${source} -> ${destination}`);
