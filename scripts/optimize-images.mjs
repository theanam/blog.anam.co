#!/usr/bin/env node
// Shrinks blog images in place so pages stay fast.
//
//   node scripts/optimize-images.mjs <file>...   optimise these files (the pre-commit hook does this)
//   node scripts/optimize-images.mjs --all       optimise everything under content/images (CI does this)
//   add --check to report what would change without writing anything
//
// Rules: anything wider than MAX_WIDTH is scaled down, EXIF orientation is applied and metadata
// (camera details, GPS) is dropped, and the file is re-encoded. A file is only rewritten if it gets
// at least MIN_SAVING smaller, so running this again on an optimised image leaves it alone rather
// than recompressing it a little worse each time.
import { readFile, writeFile, readdir } from "node:fs/promises";
import { extname, join } from "node:path";
import sharp from "sharp";

const MAX_WIDTH = 2000; // Casper shows feature images up to 2000px wide
const MIN_SAVING = 0.05;
const IMAGE_ROOT = "content/images";
const ENCODERS = {
  ".jpg": (img) => img.jpeg({ quality: 80, mozjpeg: true, progressive: true }),
  ".jpeg": (img) => img.jpeg({ quality: 80, mozjpeg: true, progressive: true }),
  // palette: quantise to <=256 colours like pngquant; screenshots shrink a lot, the result is only
  // kept if it is actually smaller.
  ".png": (img) => img.png({ compressionLevel: 9, palette: true, quality: 90, effort: 10 }),
  ".webp": (img) => img.webp({ quality: 80, effort: 6 }),
};
// Left untouched: GIFs may be animated, SVGs are text. HEIC isn't displayable by most browsers.
const REFUSE = { ".heic": "HEIC doesn't display in most browsers. Export it as JPEG first." };

const args = process.argv.slice(2);
const check = args.includes("--check");
const files = args.includes("--all") ? await walk(IMAGE_ROOT) : args.filter((a) => !a.startsWith("--"));

async function walk(dir) {
  const out = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...(await walk(path)));
    else out.push(path);
  }
  return out;
}

const kb = (n) => `${(n / 1024).toFixed(0)} KB`;
let saved = 0;
let changed = 0;
let failed = false;

for (const file of files) {
  const ext = extname(file).toLowerCase();
  if (REFUSE[ext]) {
    console.error(`✗ ${file}: ${REFUSE[ext]}`);
    failed = true;
    continue;
  }
  const encode = ENCODERS[ext];
  if (!encode) continue;

  try {
    const original = await readFile(file);
    const meta = await sharp(original).metadata();
    const pages = meta.pages ?? 1;
    if (pages > 1) continue; // animated WebP

    let img = sharp(original).rotate(); // apply EXIF orientation; metadata is dropped on output
    const resize = (meta.autoOrient?.width ?? meta.width) > MAX_WIDTH;
    if (resize) img = img.resize({ width: MAX_WIDTH, withoutEnlargement: true });
    const output = await encode(img).toBuffer();

    if (!resize && output.length > original.length * (1 - MIN_SAVING)) continue;
    if (output.length >= original.length) continue;

    saved += original.length - output.length;
    changed += 1;
    const note = resize ? `, resized to ${MAX_WIDTH}px wide` : "";
    console.log(`${check ? "would shrink" : "✓"} ${file}: ${kb(original.length)} → ${kb(output.length)}${note}`);
    if (!check) await writeFile(file, output);
  } catch (err) {
    console.error(`✗ ${file}: ${err.message}`);
    failed = true;
  }
}

if (changed) console.log(`${check ? "Would save" : "Saved"} ${kb(saved)} across ${changed} image(s).`);
process.exit(failed ? 1 : 0);
