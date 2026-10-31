import { Config } from "@remotion/cli/config";

Config.setEntryPoint("src/index.ts");
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
Config.setCodec("h264");
// Qualité constante élevée : TikTok recompresse, autant lui donner une bonne source.
Config.setCrf(18);
Config.setPixelFormat("yuv420p");
// Un Chromium déjà installé, si on en indique un (sinon Remotion télécharge le sien).
if (process.env.REMOTION_BROWSER) Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
