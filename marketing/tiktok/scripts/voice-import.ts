// Importe la voix off d'une vidéo, générée d'un seul tenant (par exemple avec le connecteur
// ElevenLabs de Claude, ou depuis le site), et sa transcription mot à mot, puis la découpe
// scène par scène pour les sous-titres.
//
//   npm run voice:import -- 01-prepa-relue voix.mp3 mots.json
//
// mots.json : les mots dans l'ordre, [{ "text", "start", "end" }] en secondes (le champ
// `words` d'une transcription ElevenLabs Scribe convient tel quel). La transcription peut
// écrire certains mots autrement que le script (le nom de la marque, un nombre) : les mots
// sont alignés au plus proche, et ceux qui manquent prennent un temps interpolé.
//
// Écrit public/voice/<vidéo>/<scène>.mp3 et .json, comme scripts/voice.ts. Le volume est
// normalisé à −14 LUFS, le niveau habituel des réseaux sociaux.
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { VIDEOS } from "../src/videos";
import type { Word } from "../src/words";

const PUBLIC = join(dirname(fileURLToPath(import.meta.url)), "..", "public");

type Heard = { text: string; start: number; end: number; type?: string };

const normalize = (text: string) =>
  text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]/g, "");

function distance(a: string, b: string) {
  const row = Array.from({ length: b.length + 1 }, (_, index) => index);
  for (let i = 1; i <= a.length; i++) {
    let previous = row[0];
    row[0] = i;
    for (let j = 1; j <= b.length; j++) {
      const current = row[j];
      row[j] = Math.min(row[j] + 1, row[j - 1] + 1, previous + (a[i - 1] === b[j - 1] ? 0 : 1));
      previous = current;
    }
  }
  return row[b.length];
}

const similarity = (a: string, b: string) => 1 - distance(a, b) / Math.max(a.length, b.length, 1);

/** Pour chaque mot écrit, l'indice du mot entendu qui lui correspond, ou -1. */
function align(written: string[], heard: string[]) {
  const GAP = 0.6;
  const n = written.length;
  const m = heard.length;
  const cost = Array.from({ length: n + 1 }, () => new Float64Array(m + 1));
  for (let i = 1; i <= n; i++) cost[i][0] = i * GAP;
  for (let j = 1; j <= m; j++) cost[0][j] = j * GAP;
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      cost[i][j] = Math.min(
        cost[i - 1][j - 1] + 1 - similarity(written[i - 1], heard[j - 1]),
        cost[i - 1][j] + GAP,
        cost[i][j - 1] + GAP,
      );
    }
  }
  const match = new Array<number>(n).fill(-1);
  for (let i = n, j = m; i > 0 && j > 0; ) {
    const diagonal = cost[i - 1][j - 1] + 1 - similarity(written[i - 1], heard[j - 1]);
    if (Math.abs(cost[i][j] - diagonal) < 1e-9) {
      if (similarity(written[i - 1], heard[j - 1]) >= 0.4) match[i - 1] = j - 1;
      i--;
      j--;
    } else if (Math.abs(cost[i][j] - (cost[i - 1][j] + GAP)) < 1e-9) i--;
    else j--;
  }
  return match;
}

function main() {
  const [id, audio, wordsFile] = process.argv.slice(2);
  const video = VIDEOS.find((candidate) => candidate.id === id);
  if (!video || !audio || !wordsFile) {
    throw new Error("Usage : npm run voice:import -- <vidéo> <voix.mp3> <mots.json>");
  }
  const raw = JSON.parse(readFileSync(wordsFile, "utf8")) as Heard[] | { words: Heard[] };
  const heard = (Array.isArray(raw) ? raw : raw.words).filter(
    (word) => (word.type ?? "word") === "word" && normalize(word.text),
  );

  // Les mots du script, scène par scène ; la ponctuation isolée (« : », « ? ») suit le mot d'avant.
  const tokens = video.scenes.flatMap((scene, sceneIndex) =>
    scene.voice
      .split(/\s+/)
      .filter(Boolean)
      .map((text) => ({ text, scene: sceneIndex, key: normalize(text) })),
  );
  const spoken = tokens.filter((token) => token.key);
  const match = align(
    spoken.map((token) => token.key),
    heard.map((word) => normalize(word.text)),
  );
  const timed = spoken.map((token, index) => ({
    ...token,
    start: match[index] >= 0 ? heard[match[index]].start : NaN,
    end: match[index] >= 0 ? heard[match[index]].end : NaN,
  }));
  // Les mots non retrouvés se partagent le temps entre leurs voisins, au prorata des lettres.
  for (let index = 0; index < timed.length; ) {
    if (!Number.isNaN(timed[index].start)) {
      index++;
      continue;
    }
    let last = index;
    while (last < timed.length && Number.isNaN(timed[last].start)) last++;
    const from = index > 0 ? timed[index - 1].end : 0;
    const to = last < timed.length ? timed[last].start : Math.max(from + 0.3, heard[heard.length - 1]?.end ?? from);
    const letters = timed.slice(index, last).reduce((sum, token) => sum + token.key.length, 0);
    let time = from;
    for (let k = index; k < last; k++) {
      const span = ((to - from) * timed[k].key.length) / letters;
      timed[k].start = time;
      timed[k].end = time + span;
      time += span;
    }
    console.warn(
      `  non retrouvés : ${timed
        .slice(index, last)
        .map((token) => token.text)
        .join(" ")}`,
    );
    index = last;
  }

  const duration = Number(
    execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).toString(),
  );
  // Coupe au milieu du silence entre deux scènes.
  const scenes = video.scenes.map((_, sceneIndex) => timed.filter((token) => token.scene === sceneIndex));
  const cuts = [0];
  for (let index = 0; index < scenes.length - 1; index++) {
    const end = scenes[index][scenes[index].length - 1].end;
    const start = scenes[index + 1][0].start;
    cuts.push((end + start) / 2);
  }
  cuts.push(duration);

  const work = mkdtempSync(join(tmpdir(), "voix-"));
  const normalized = join(work, "voix.wav");
  execFileSync("ffmpeg", [
    "-loglevel",
    "error",
    "-y",
    "-i",
    audio,
    "-af",
    "loudnorm=I=-14:TP=-1.5:LRA=11",
    "-ar",
    "44100",
    "-ac",
    "1",
    normalized,
  ]);

  const dir = join(PUBLIC, "voice", video.id);
  mkdirSync(dir, { recursive: true });
  for (const file of readdirSync(dir)) rmSync(join(dir, file));
  video.scenes.forEach((scene, index) => {
    const base = join(dir, String(index + 1).padStart(2, "0"));
    const [from, to] = [cuts[index], cuts[index + 1]];
    execFileSync("ffmpeg", [
      "-loglevel",
      "error",
      "-y",
      "-ss",
      from.toFixed(3),
      "-to",
      to.toFixed(3),
      "-i",
      normalized,
      "-c:a",
      "libmp3lame",
      "-b:a",
      "128k",
      `${base}.mp3`,
    ]);
    // Les mots de la scène, ponctuation isolée comprise, en temps relatif à son début.
    const words: Word[] = [];
    for (const text of scene.voice.split(/\s+/).filter(Boolean)) {
      const token = normalize(text) ? scenes[index][words.filter((word) => normalize(word.text)).length] : undefined;
      const previous = words[words.length - 1];
      words.push(
        token
          ? { text, start: round(token.start - from), end: round(token.end - from) }
          : { text, start: previous?.end ?? 0, end: previous?.end ?? 0 },
      );
    }
    writeFileSync(
      `${base}.json`,
      `${JSON.stringify({ text: scene.voice, words, duration: round(to - from) }, null, 2)}\n`,
    );
    console.log(`${video.id} · scène ${index + 1} : ${(to - from).toFixed(2)} s`);
  });
  rmSync(work, { recursive: true });
}

const round = (value: number) => Math.round(value * 1000) / 1000;

try {
  main();
} catch (error) {
  console.error((error as Error).message);
  process.exit(1);
}
