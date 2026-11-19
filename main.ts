// Entry runner for the news-image-20261119 bounty.
//
// Places the pre-rendered front page (entry.png, produced by draw.py)
// where make.fun expects it: <output dir>/entry.png. The output directory
// comes from MAKEFUN_OUTPUT_DIR when set, and defaults to /output.
// Node 22, standard library only. No network, no randomness.

import { copyFile, mkdir, stat } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

function outputDir(): string {
  const override = process.env.MAKEFUN_OUTPUT_DIR;
  if (override !== undefined && override.trim() !== "") {
    return resolve(override);
  }
  return "/output";
}

async function placeImage(): Promise<void> {
  const source = join(HERE, "entry.png");
  const destDir = outputDir();
  const dest = join(destDir, "entry.png");

  await mkdir(destDir, { recursive: true });
  await copyFile(source, dest);

  const info = await stat(dest);
  if (info.size > 1_048_576) {
    throw new Error(`entry.png is ${info.size} bytes, over the 1 MiB limit`);
  }
  console.log(`entry.png -> ${dest} (${info.size} bytes)`);
}

await placeImage();
