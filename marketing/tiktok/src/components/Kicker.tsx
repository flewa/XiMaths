import { useCurrentFrame } from "remotion";
import { ease } from "../anim";
import { COLORS, MONO } from "../theme";

/** Invite de terminal, comme l'en-tête du fil sur le site : « › prépa ~ semaine 12▌ ». */
export function Kicker({
  text,
  delay = 0,
  size = 36,
  color = COLORS.onDarkMute,
}: {
  text: string;
  delay?: number;
  size?: number;
  color?: string;
}) {
  const frame = useCurrentFrame();
  const shown = Math.floor(ease(frame, delay, delay + Math.max(6, text.length * 0.9), 0, text.length));
  const cursor = Math.floor(frame / 8) % 2 === 0;
  return (
    <div style={{ fontFamily: MONO, fontSize: size, color, letterSpacing: 0.5, whiteSpace: "pre" }}>
      <span style={{ color: "#30d158" }}>› </span>
      {text.slice(0, shown)}
      <span style={{ opacity: cursor ? 1 : 0, color: COLORS.onDark }}>▌</span>
    </div>
  );
}
