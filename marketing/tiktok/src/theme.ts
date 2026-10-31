import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import type { Accent } from "./videos";

export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// Couleurs de l'application (frontend/src/app/globals.css).
export const COLORS = {
  ink: "#201d1d",
  body: "#424245",
  mute: "#646262",
  ash: "#9a9898",
  canvas: "#fdfcfc",
  card: "#f1eeee",
  dark: "#141010",
  darkElevated: "#2a2525",
  hairlineDark: "rgba(255, 240, 240, 0.14)",
  onDark: "#fdfcfc",
  onDarkMute: "#a09d9d",
  paper: "#f6f1e7",
  pen: "#1c2a6b",
  redPen: "#e0261b",
};

export const ACCENTS: Record<Accent, string> = {
  green: "#30d158",
  orange: "#ff9f0a",
  red: "#ff453a",
  blue: "#64a8ff",
};

// Zone sûre de TikTok : l'interface couvre le haut (onglets), la colonne de droite
// (j'aime, commentaires, partage) et le bas (pseudo, légende, son).
export const SAFE = { top: 230, bottom: 1440, left: 72, right: 940 };
// Les sous-titres se placent juste au-dessus de la légende TikTok.
export const CAPTION_Y = 1300;

export const MONO = "JetBrains Mono";
export const HAND = "Caveat";

const FACES: [string, string, number][] = [
  [MONO, "jetbrains-mono", 400],
  [MONO, "jetbrains-mono", 700],
  [MONO, "jetbrains-mono", 800],
  [HAND, "caveat", 400],
  [HAND, "caveat", 700],
];

/** Polices locales, latin et latin étendu : le rendu attend qu'elles soient chargées. */
export const fontsReady = Promise.all(
  FACES.flatMap(([family, file, weight]) =>
    ["latin", "latin-ext"].map((subset) =>
      loadFont({
        family,
        url: staticFile(`fonts/${file}-${subset}-${weight}-normal.woff2`),
        weight: String(weight),
        unicodeRange:
          subset === "latin"
            ? "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
            : "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF",
      }),
    ),
  ),
);
