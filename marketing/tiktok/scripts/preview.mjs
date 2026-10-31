// Planches de contrôle : une image par scène (aux trois quarts de la scène), côte à côte.
//   node scripts/preview.mjs [vidéo…]   → out/preview/<vidéo>.png
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;
const OUT = join(ROOT, "out", "preview");
const TRANSITION = 8;
const FPS = 30;
const at = Number(process.env.AT ?? 0.75);

mkdirSync(OUT, { recursive: true });
const serveUrl = await bundle({ entryPoint: join(ROOT, "src", "index.ts") });
const ids = process.argv.slice(2);
const browserExecutable = process.env.REMOTION_BROWSER ?? null;

// HOOKS=1 : la première image de chaque vidéo, celle qui doit arrêter le défilement.
if (process.env.HOOKS) {
  const files = [];
  for (const id of ids) {
    const composition = await selectComposition({ serveUrl, id, inputProps: {}, browserExecutable });
    const output = join(OUT, `hook-${id}.png`);
    await renderStill({ serveUrl, composition, frame: 0, output, browserExecutable, scale: 0.5 });
    files.push(output);
  }
  execFileSync("ffmpeg", [
    "-loglevel",
    "error",
    "-y",
    ...files.flatMap((file) => ["-i", file]),
    "-filter_complex",
    `hstack=${files.length}`,
    join(OUT, "hooks.png"),
  ]);
  for (const file of files) rmSync(file);
  console.log(join(OUT, "hooks.png"));
  process.exit(0);
}

for (const id of ids) {
  const composition = await selectComposition({ serveUrl, id, inputProps: {}, browserExecutable });
  const frames = composition.props.timings.map((timing) => Math.max(45, Math.ceil(timing.seconds * FPS)));
  const files = [];
  let start = 0;
  for (const [index, length] of frames.entries()) {
    const frame = start + Math.floor(length * at);
    const output = join(OUT, `${id}-${index}.png`);
    await renderStill({ serveUrl, composition, frame, output, browserExecutable, scale: 0.5 });
    files.push(output);
    start += length - TRANSITION;
  }
  execFileSync("ffmpeg", [
    "-loglevel",
    "error",
    "-y",
    ...files.flatMap((file) => ["-i", file]),
    "-filter_complex",
    `hstack=${files.length}`,
    join(OUT, `${id}.png`),
  ]);
  for (const file of files) rmSync(file);
  console.log(join(OUT, `${id}.png`));
}
