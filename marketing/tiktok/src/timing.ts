// Durée des scènes et position des mots dans le temps.
//
// Avec la voix (public/voice/<vidéo>/<scène>.json, écrit par scripts/voice.ts), chaque
// scène dure le temps de sa phrase, et les sous-titres suivent l'alignement renvoyé par
// ElevenLabs. Sans elle, une estimation au débit d'une voix off TikTok permet de monter
// et de relire la vidéo : la voix ajoutée, rien d'autre ne change.
import type { CalculateMetadataFunction } from "remotion";
import { getStaticFiles, staticFile } from "remotion";
import { FPS } from "./theme";
import { VIDEOS, type Video } from "./videos";
import { estimateWords, TAIL, TRANSITION, type Word } from "./words";

export { TRANSITION, type Word };

export type SceneTiming = { words: Word[]; seconds: number; audio: string | null };
export type VoiceFile = { words: Word[]; duration: number };

export const voicePath = (videoId: string, scene: number, ext: "json" | "mp3") =>
  `voice/${videoId}/${String(scene + 1).padStart(2, "0")}.${ext}`;

export async function sceneTimings(video: Video): Promise<SceneTiming[]> {
  const files = new Set(getStaticFiles().map((file) => file.name));
  return Promise.all(
    video.scenes.map(async (scene, index) => {
      const json = voicePath(video.id, index, "json");
      const mp3 = voicePath(video.id, index, "mp3");
      if (files.has(json) && files.has(mp3)) {
        const voice: VoiceFile = await fetch(staticFile(json)).then((response) => response.json());
        return { words: voice.words, seconds: voice.duration + TAIL, audio: mp3 };
      }
      const words = estimateWords(scene.voice);
      return { words, seconds: words[words.length - 1].end + TAIL, audio: null };
    }),
  );
}

export const sceneFrames = (timing: SceneTiming) => Math.max(45, Math.ceil(timing.seconds * FPS));

export type VideoProps = { videoId: string; timings: SceneTiming[] | null; music: string | null };

export const calculateMetadata: CalculateMetadataFunction<VideoProps> = async ({ props }) => {
  const video = VIDEOS.find((candidate) => candidate.id === props.videoId);
  if (!video) throw new Error(`Vidéo inconnue : ${props.videoId}`);
  const timings = await sceneTimings(video);
  const total = timings.reduce((sum, timing) => sum + sceneFrames(timing), 0) - TRANSITION * (timings.length - 1);
  // Un fond musical facultatif, commun aux vidéos : public/music/fond.mp3.
  const music = getStaticFiles().some((file) => file.name === "music/fond.mp3") ? "music/fond.mp3" : null;
  return { durationInFrames: total, props: { ...props, timings, music } };
};
