import { useCurrentFrame } from "remotion";
import { pop } from "../anim";
import { ACCENTS, CAPTION_Y, FPS, MONO, SAFE } from "../theme";
import type { Word } from "../timing";

const MAX_CHARS = 16;
const MAX_WORDS = 3;

type Page = { words: Word[]; start: number; end: number };

/** Pages de quelques mots, coupées aux signes de ponctuation : on lit d'un coup d'œil. */
export function paginate(words: Word[]): Page[] {
  const pages: Page[] = [];
  let current: Word[] = [];
  const flush = () => {
    if (current.length) pages.push({ words: current, start: current[0].start, end: current[current.length - 1].end });
    current = [];
  };
  for (const word of words) {
    const length = current.reduce((sum, w) => sum + w.text.length + 1, 0) + word.text.length;
    if (current.length && (length > MAX_CHARS || current.length >= MAX_WORDS)) flush();
    current.push(word);
    if (/[.?!…:;,]$/.test(word.text)) flush();
  }
  flush();
  // Chaque page reste affichée jusqu'à la suivante.
  return pages.map((page, index) => ({ ...page, end: pages[index + 1]?.start ?? page.end + 0.5 }));
}

/** Sous-titres mot à mot, le mot prononcé en couleur. Le temps est celui de la scène. */
export function Captions({ words, accent = ACCENTS.green }: { words: Word[]; accent?: string }) {
  const frame = useCurrentFrame();
  const time = frame / FPS;
  const page = paginate(words).find((candidate) => time >= candidate.start && time < candidate.end);
  if (!page) return null;
  const enter = pop(frame, Math.round(page.start * FPS), 13, 260);
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: SAFE.right - SAFE.left,
        top: CAPTION_Y,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "0 22px",
        isolation: "isolate",
        transform: `translateY(-50%) scale(${0.86 + 0.14 * enter})`,
        opacity: Math.min(1, enter * 1.6),
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: "-40px -60px",
          background:
            "radial-gradient(ellipse at center, rgba(12,9,9,0.72) 0%, rgba(12,9,9,0.45) 45%, rgba(12,9,9,0) 72%)",
          zIndex: -1,
        }}
      />
      {page.words.map((word, index) => {
        const active = time >= word.start && (index === page.words.length - 1 || time < page.words[index + 1].start);
        return (
          <span
            key={`${word.start}-${word.text}`}
            style={{
              fontFamily: MONO,
              fontWeight: 800,
              fontSize: 76,
              lineHeight: 1.18,
              color: active ? accent : "#ffffff",
              WebkitTextStroke: "12px #0b0808",
              paintOrder: "stroke fill",
              textShadow: "0 6px 18px rgba(0,0,0,0.55)",
              transform: active ? "scale(1.06)" : undefined,
              display: "inline-block",
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
}
