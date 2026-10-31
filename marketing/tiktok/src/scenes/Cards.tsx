import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Kicker } from "../components/Kicker";
import { ACCENTS, COLORS, MONO, SAFE } from "../theme";
import type { Accent } from "../videos";

const WIDTH = SAFE.right - SAFE.left;

/** Liste à cases du site : « [✓] Relectures », qui tombent une à une. */
export function Chips({
  title,
  items,
  accent = "green",
  marks,
  colors,
}: {
  title?: string;
  items: string[];
  accent?: Accent;
  marks?: string[];
  colors?: Accent[];
}) {
  const frame = useCurrentFrame();
  const size = items.some((item) => item.length > 18) ? 50 : 60;
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: WIDTH,
        top: 0,
        bottom: 1920 - 1200,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 34,
      }}
    >
      {title && <Kicker text={title} delay={-6} size={42} />}
      {items.map((item, index) => {
        const p = pop(frame, 4 + index * 6, 13, 210);
        const color = ACCENTS[colors?.[index] ?? accent];
        return (
          <div
            key={item}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 26,
              padding: "22px 30px",
              borderRadius: 20,
              background: COLORS.darkElevated,
              border: `3px solid ${color}55`,
              fontFamily: MONO,
              fontWeight: 800,
              fontSize: size,
              color: COLORS.onDark,
              opacity: Math.min(1, p * 1.4),
              transform: `translateX(${(1 - p) * -140}px)`,
            }}
          >
            <span style={{ color, flexShrink: 0 }}>{marks?.[index] ?? "[✓]"}</span>
            <span>{item}</span>
          </div>
        );
      })}
    </div>
  );
}

/** Une IA qui démontre un résultat faux avec aplomb, puis le tampon « faux ». */
export function Chat({
  text,
  verdict,
  duration,
  instant = false,
}: {
  text: string;
  verdict: string;
  duration: number;
  instant?: boolean;
}) {
  const frame = useCurrentFrame();
  // En ouverture, la réponse est déjà là : l'erreur se lit dès la première image.
  const typedFrom = instant ? -200 : 6;
  const typed = Math.floor(ease(frame, typedFrom, typedFrom + text.length / 2.4, 0, text.length));
  const stampAt = Math.round(duration * 0.55);
  const stamp = pop(frame, stampAt, 10, 240);
  return (
    <>
      <div
        style={{
          position: "absolute",
          right: 1080 - SAFE.right,
          top: 330,
          maxWidth: 640,
          padding: "26px 34px",
          borderRadius: "34px 34px 8px 34px",
          background: "#2f6ff0",
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 46,
          color: "#ffffff",
        }}
      >
        ∑ 1/n² converge ?
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          top: 500,
          display: "flex",
          alignItems: "center",
          gap: 18,
          fontFamily: MONO,
          fontSize: 34,
          color: COLORS.onDarkMute,
        }}
      >
        <svg width="56" height="56" viewBox="0 0 24 24" aria-hidden>
          <path d="M12 1 C 13 8 16 11 23 12 C 16 13 13 16 12 23 C 11 16 8 13 1 12 C 8 11 11 8 12 1 Z" fill="#c9b8ff" />
        </svg>
        Assistant IA
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: WIDTH,
          top: 590,
          padding: "34px 40px",
          borderRadius: "8px 34px 34px 34px",
          background: COLORS.darkElevated,
          border: "2px solid rgba(255,240,240,0.1)",
          fontFamily: MONO,
          fontSize: 54,
          lineHeight: 1.35,
          color: COLORS.onDark,
          boxSizing: "border-box",
          minHeight: 300,
        }}
      >
        {frame < typedFrom ? <span style={{ color: COLORS.onDarkMute }}>• • •</span> : text.slice(0, typed)}
        {frame >= stampAt && (
          <div
            style={{
              position: "absolute",
              left: 40,
              right: 40,
              top: "58%",
              height: 10,
              borderRadius: 6,
              background: ACCENTS.red,
              transform: `scaleX(${ease(frame, stampAt, stampAt + 8)}) rotate(-2deg)`,
              transformOrigin: "0 50%",
            }}
          />
        )}
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.right - 420,
          top: 880,
          border: `12px solid ${ACCENTS.red}`,
          borderRadius: 20,
          padding: "6px 36px",
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 120,
          color: ACCENTS.red,
          letterSpacing: 6,
          opacity: Math.min(1, stamp * 2),
          transform: `rotate(-12deg) scale(${2.4 - 1.4 * stamp})`,
          background: "rgba(20,16,16,0.75)",
        }}
      >
        {verdict.toUpperCase()}
      </div>
    </>
  );
}

/** Fin : la marque, l'invite de terminal, la phrase, et le lien en bio. */
export function Cta({ prompt, line }: { prompt: string; line: string }) {
  const frame = useCurrentFrame();
  const logo = pop(frame, 0, 13, 180);
  const text = pop(frame, 14, 14, 180);
  const pill = pop(frame, 22, 11, 200);
  const bounce = Math.abs(Math.sin(frame / 6)) * 16;
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: WIDTH,
        top: 0,
        bottom: 1920 - 1240,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 44,
        textAlign: "center",
      }}
    >
      <div
        style={{
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 150,
          color: COLORS.onDark,
          letterSpacing: -4,
          transform: `scale(${0.6 + 0.4 * logo})`,
          opacity: Math.min(1, logo * 1.5),
        }}
      >
        <span style={{ color: ACCENTS.green }}>[ξ]</span> XiMaths
      </div>
      <Kicker text={prompt} delay={4} size={38} />
      <div
        style={{
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 64,
          lineHeight: 1.15,
          color: COLORS.onDark,
          opacity: text,
          transform: `translateY(${(1 - text) * 40}px)`,
        }}
      >
        {line}
      </div>
      <div
        style={{
          marginTop: 20,
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 52,
          color: COLORS.ink,
          background: ACCENTS.green,
          borderRadius: 18,
          padding: "16px 40px",
          transform: `scale(${pill})`,
          boxShadow: "0 0 60px rgba(48,209,88,0.35)",
        }}
      >
        lien en bio <span style={{ display: "inline-block", transform: `translateY(${bounce}px)` }}>↓</span>
      </div>
    </div>
  );
}
