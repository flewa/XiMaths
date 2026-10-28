// Rend les vidéos en MP4 (1080 × 1920, 30 i/s, H.264) dans out/.
//   npm run render                    # toutes
//   npm run render -- 04-defi-chrono  # celles-ci
import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia, selectComposition } from "@remotion/renderer";
import { join } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname;
const browserExecutable = process.env.REMOTION_BROWSER ?? null;

const serveUrl = await bundle({ entryPoint: join(ROOT, "src", "index.ts") });
const only = process.argv.slice(2);
const ids = (await getCompositions(serveUrl, { browserExecutable }))
  .map((composition) => composition.id)
  .filter((id) => !only.length || only.includes(id));

for (const id of ids) {
  const composition = await selectComposition({ serveUrl, id, inputProps: {}, browserExecutable });
  const outputLocation = join(ROOT, "out", `${id}.mp4`);
  const started = Date.now();
  await renderMedia({
    serveUrl,
    composition,
    codec: "h264",
    crf: 18,
    pixelFormat: "yuv420p",
    imageFormat: "jpeg",
    jpegQuality: 92,
    outputLocation,
    browserExecutable,
  });
  console.log(
    `${outputLocation} · ${(composition.durationInFrames / composition.fps).toFixed(1)} s · rendu en ${Math.round((Date.now() - started) / 1000)} s`,
  );
}
