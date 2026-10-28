import { Easing, interpolate, spring } from "remotion";
import { FPS } from "./theme";

/** Ressort de 0 à 1 qui démarre à `delay` images : entrées vives, sans rebond excessif. */
export function pop(frame: number, delay = 0, damping = 14, stiffness = 170) {
  return spring({ frame: frame - delay, fps: FPS, config: { damping, stiffness, mass: 0.7 } });
}

/** Ressort amorti, pour les mouvements de caméra. */
export function glide(frame: number, delay = 0, durationInFrames = 18) {
  return spring({ frame: frame - delay, fps: FPS, config: { damping: 200 }, durationInFrames });
}

const OUT = Easing.bezier(0.16, 1, 0.3, 1);

/** Interpolation bornée, sortie douce. */
export function ease(frame: number, from: number, to: number, a = 0, b = 1, easing = OUT) {
  return interpolate(frame, [from, to], [a, b], {
    easing,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
}
