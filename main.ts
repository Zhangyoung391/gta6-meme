// gta6-meme-x-01 entrypoint (Node 22, standard library only).
//
// The entry is the X post itself: the meme (meme.png) and its text. This
// program does exactly one thing the gate needs: it carries POST.json, the
// file at this repository's root naming the post's address, into the output
// directory, byte for byte. It prints nothing on success and exits non-zero
// only when POST.json cannot be read or is not valid JSON.
//
// Until the post exists, POST.json holds a placeholder address; the program
// still runs fine on it (a placeholder is valid JSON), and the real address
// replaces it before the entry is submitted.
//
// Run it the way the grader does:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
//
// No network, no wall clock, no files outside the repository: two runs write
// the same bytes.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const SOURCE = join(BOT_DIR, "POST.json");
const TARGET = join(OUTPUT_DIR, "POST.json");

let bytes: Buffer;
try {
  bytes = readFileSync(SOURCE);
} catch (err) {
  console.error(`POST.json could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}

try {
  const parsed: unknown = JSON.parse(bytes.toString("utf8"));
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("POST.json is not a JSON object");
  }
} catch (err) {
  console.error(`POST.json is not valid: ${(err as Error).message}`);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
writeFileSync(TARGET, bytes);
