import { AbsoluteFill, useCurrentFrame } from "remotion";
import { COLORS, MONO } from "../theme";

const GLYPHS = ["∑", "∫", "∂", "ε", "∀", "ℝ", "π", "∞", "⇒", "λ", "∃", "ξ"];

// Positions fixes, tirées une fois : le fond reste le même d'une image à l'autre.
const FLOATERS = GLYPHS.map((glyph, index) => ({
  glyph,
  x: ((index * 397) % 1000) + 20,
  y: (index * 613) % 1880,
  size: 70 + ((index * 53) % 90),
  speed: 0.25 + ((index * 7) % 5) * 0.08,
}));

/** Fond commun à toutes les scènes : sombre, une grille légère et des symboles qui montent. */
export function Backdrop() {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.dark }}>
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 90% 60% at 50% 38%, #2b2424 0%, rgba(20,16,16,0) 70%)",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,240,240,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,240,240,0.035) 1px, transparent 1px)",
          backgroundSize: "72px 72px",
          backgroundPosition: `0 ${-(frame * 0.4) % 72}px`,
        }}
      />
      {FLOATERS.map((item) => (
        <div
          key={item.glyph}
          style={{
            position: "absolute",
            left: item.x,
            top: (((item.y - frame * item.speed) % 1920) + 1920) % 1920,
            fontFamily: MONO,
            fontSize: item.size,
            color: "rgba(255, 240, 240, 0.045)",
          }}
        >
          {item.glyph}
        </div>
      ))}
      <AbsoluteFill style={{ boxShadow: "inset 0 0 260px rgba(0,0,0,0.55)" }} />
    </AbsoluteFill>
  );
}
