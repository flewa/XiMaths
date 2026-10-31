// Voix off ElevenLabs, scène par scène, avec l'alignement mot à mot pour les sous-titres.
//
//   ELEVENLABS_API_KEY=… npm run voice -- --voices          # voix disponibles (choisir une voix française)
//   ELEVENLABS_API_KEY=… ELEVENLABS_VOICE_ID=… npm run voice                    # toutes les vidéos
//   ELEVENLABS_API_KEY=… ELEVENLABS_VOICE_ID=… npm run voice -- 04-defi-chrono  # une seule
//
// Écrit public/voice/<vidéo>/<scène>.mp3 et .json ; une scène dont le texte n'a pas changé
// n'est pas régénérée (--force pour tout refaire). La clé se lit dans l'environnement,
// jamais dans un fichier du dépôt.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { VIDEOS } from "../src/videos";
import type { Word } from "../src/words";

const API = "https://api.elevenlabs.io/v1";
const MODEL = process.env.ELEVENLABS_MODEL ?? "eleven_multilingual_v2";
const PUBLIC = join(dirname(fileURLToPath(import.meta.url)), "..", "public");

// Ce que la voix doit dire autrement qu'on l'écrit. Un mot reste un mot (pas d'espace
// ajoutée), pour que l'alignement retombe sur les mots des sous-titres.
const SAY: Record<string, string> = {
  XiMaths: "Ksi-maths",
  LaTeX: "Latek",
  L1: "L-un",
  M2: "M-deux",
};

// Une voix posée mais vivante : un peu de variation, pas de jeu d'acteur.
const VOICE_SETTINGS = { stability: 0.45, similarity_boost: 0.8, style: 0.25, use_speaker_boost: true, speed: 1.05 };

type Alignment = {
  characters: string[];
  character_start_times_seconds: number[];
  character_end_times_seconds: number[];
};

const spoken = (text: string) =>
  text
    .split(" ")
    .map((word) => word.replace(/[\p{L}\p{N}]+/gu, (core) => SAY[core] ?? core))
    .join(" ");

/** Début et fin de chaque mot, d'après l'alignement caractère par caractère. */
function wordsFrom(alignment: Alignment, original: string): Word[] {
  const words: Word[] = [];
  let start: number | null = null;
  let end = 0;
  alignment.characters.forEach((character, index) => {
    if (/\s/.test(character)) {
      if (start !== null) words.push({ text: "", start, end });
      start = null;
      return;
    }
    start ??= alignment.character_start_times_seconds[index];
    end = alignment.character_end_times_seconds[index];
  });
  if (start !== null) words.push({ text: "", start, end });
  const texts = original.split(/\s+/).filter(Boolean);
  if (texts.length !== words.length) {
    throw new Error(`Alignement : ${words.length} mots entendus pour ${texts.length} écrits dans « ${original} ».`);
  }
  return words.map((word, index) => ({ ...word, text: texts[index] }));
}

async function api(path: string, init: RequestInit = {}) {
  const key = process.env.ELEVENLABS_API_KEY;
  if (!key) throw new Error("ELEVENLABS_API_KEY manque dans l'environnement.");
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { "xi-api-key": key, "Content-Type": "application/json", ...init.headers },
  });
  if (!response.ok) throw new Error(`ElevenLabs ${response.status} : ${await response.text()}`);
  return response.json();
}

async function listVoices() {
  const { voices } = (await api("/voices")) as {
    voices: { voice_id: string; name: string; labels?: Record<string, string> }[];
  };
  for (const voice of voices) {
    const labels = Object.values(voice.labels ?? {}).join(", ");
    console.log(`${voice.voice_id}  ${voice.name}${labels ? `  (${labels})` : ""}`);
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--voices")) return listVoices();
  const voiceId = process.env.ELEVENLABS_VOICE_ID;
  if (!voiceId) throw new Error("ELEVENLABS_VOICE_ID manque : `npm run voice -- --voices` liste les voix.");
  const force = args.includes("--force");
  const only = args.filter((arg) => !arg.startsWith("--"));

  for (const video of VIDEOS) {
    if (only.length && !only.includes(video.id)) continue;
    const dir = join(PUBLIC, "voice", video.id);
    mkdirSync(dir, { recursive: true });
    for (const [index, scene] of video.scenes.entries()) {
      const base = join(dir, String(index + 1).padStart(2, "0"));
      if (!force && existsSync(`${base}.json`) && existsSync(`${base}.mp3`)) {
        const saved = JSON.parse(readFileSync(`${base}.json`, "utf8")) as { text?: string };
        if (saved.text === scene.voice) continue;
      }
      // Les phrases voisines donnent le ton : la voix enchaîne au lieu de repartir à zéro.
      const body = {
        text: spoken(scene.voice),
        model_id: MODEL,
        voice_settings: VOICE_SETTINGS,
        previous_text: index > 0 ? spoken(video.scenes[index - 1].voice) : undefined,
        next_text: index < video.scenes.length - 1 ? spoken(video.scenes[index + 1].voice) : undefined,
      };
      const result = (await api(`/text-to-speech/${voiceId}/with-timestamps?output_format=mp3_44100_128`, {
        method: "POST",
        body: JSON.stringify(body),
      })) as { audio_base64: string; alignment: Alignment };
      const audio = Buffer.from(result.audio_base64, "base64");
      const words = wordsFrom(result.alignment, scene.voice);
      // MP3 à 128 kbit/s constant : la taille donne la durée, silence final compris.
      const duration = Math.max(words[words.length - 1].end + 0.05, (audio.length * 8) / 128000);
      writeFileSync(`${base}.mp3`, audio);
      writeFileSync(`${base}.json`, `${JSON.stringify({ text: scene.voice, words, duration }, null, 2)}\n`);
      console.log(`${video.id} · scène ${index + 1} : ${duration.toFixed(2)} s`);
    }
  }
}

main().catch((error: Error) => {
  console.error(error.message);
  process.exit(1);
});
