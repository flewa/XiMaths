import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Kicker } from "../components/Kicker";
import { ACCENTS, COLORS, MONO, SAFE } from "../theme";
import type { Accent } from "../videos";

type Token = { text: string; style: "plain" | "accent" | "strike"; suffix?: string };

/** « Relues :\n~toutes~ *presque aucune* » : lignes de mots, chacun avec son style. Ce qui
 * suit un mot stylé sans espace (« *rédaction*. ») reste collé à lui. */
export function parseRich(text: string): Token[][] {
  return text.split("\n").map((line) => {
    const tokens: Token[] = [];
    for (const match of line.matchAll(/\*([^*]+)\*|~([^~]+)~|([^*~]+)/g)) {
      const [, accent, strike, plain] = match;
      const style = accent ? "accent" : strike ? "strike" : "plain";
      const words = (accent ?? strike ?? plain).split(/\s+/);
      const previous = tokens[tokens.length - 1];
      if (plain && previous && words[0]) previous.suffix = (previous.suffix ?? "") + words.shift();
      for (const word of words.filter(Boolean)) tokens.push({ text: word, style });
    }
    return tokens;
  });
}

/** Phrase-choc : les mots tombent un à un, les mots-clés en couleur, les barrés se barrent. */
export function Title({
  text,
  kicker,
  accent = "green",
  size = 92,
  instant = false,
}: {
  text: string;
  kicker?: string;
  accent?: Accent;
  size?: number;
  instant?: boolean;
}) {
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: SAFE.right - SAFE.left,
        top: 0,
        bottom: 1920 - 1200,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 40,
      }}
    >
      {kicker && <Kicker text={kicker} delay={instant ? -20 : 0} />}
      <RichLines text={text} accent={accent} size={size} instant={instant} />
    </div>
  );
}

/** Les lignes d'un texte balisé, mot par mot. */
export function RichLines({
  text,
  accent = "green",
  size,
  instant = false,
}: {
  text: string;
  accent?: Accent;
  size: number;
  instant?: boolean;
}) {
  const frame = useCurrentFrame();
  const color = ACCENTS[accent];
  const lines = parseRich(text);
  const count = lines.flat().length;
  const step = instant ? 1.5 : 2.5;
  const start = instant ? -8 : 4;
  const strikeAt = start + count * step + 8;
  let index = 0;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: size * 0.12,
        transform: instant ? `scale(${1.08 - 0.08 * pop(frame, 0, 12, 200)})` : undefined,
        transformOrigin: "0 50%",
      }}
    >
      {lines.map((line, lineIndex) => (
        <div key={lineIndex} style={{ display: "flex", flexWrap: "wrap", gap: `${size * 0.1}px ${size * 0.38}px` }}>
          {line.map((token) => {
            const delay = start + index++ * step;
            const p = instant ? 1 : pop(frame, delay, 12, 200);
            const strike = token.style === "strike" ? ease(frame, strikeAt, strikeAt + 10) : 0;
            const mark = token.style === "accent" ? ease(frame, delay + 4, delay + 14) : 0;
            return (
              <span
                key={`${lineIndex}-${delay}`}
                style={{
                  position: "relative",
                  display: "inline-block",
                  fontFamily: MONO,
                  fontWeight: 800,
                  fontSize: size,
                  lineHeight: 1.12,
                  letterSpacing: -size * 0.02,
                  color: token.style === "accent" ? color : COLORS.onDark,
                  opacity: Math.min(1, p * 1.4) * (1 - 0.55 * strike),
                  transform: `translateY(${(1 - p) * 60}px) scale(${0.9 + 0.1 * p})`,
                }}
              >
                {token.style === "accent" && (
                  <span
                    style={{
                      position: "absolute",
                      left: -8,
                      bottom: size * 0.06,
                      height: size * 0.2,
                      width: `calc(${mark} * (100% - ${token.suffix ? token.suffix.length * 0.6 : 0}em + 16px))`,
                      background: color,
                      opacity: 0.28,
                      borderRadius: 6,
                    }}
                  />
                )}
                <span style={{ position: "relative" }}>{token.text}</span>
                {token.suffix && <span style={{ position: "relative", color: COLORS.onDark }}>{token.suffix}</span>}
                {token.style === "strike" && (
                  <span
                    style={{
                      position: "absolute",
                      left: -10,
                      top: "52%",
                      height: size * 0.11,
                      width: `calc(${strike} * (100% - ${token.suffix ? token.suffix.length * 0.6 : 0}em + 20px))`,
                      background: ACCENTS.red,
                      borderRadius: 8,
                      transform: "rotate(-4deg)",
                    }}
                  />
                )}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
}
