import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Tex } from "../components/Tex";
import { ACCENTS, COLORS, HAND, MONO, SAFE } from "../theme";

const LETTERS = "ABCDEFGHJKLMNPRSTVY";
const COLUMN = (SAFE.right - SAFE.left) / 3;
const AVATAR_Y = 640;
const CARD = { top: 850, height: 340 };

const REVIEWERS = [
  { tint: "#9fe7b3", letter: "L", verdict: "✓ correcte", color: ACCENTS.green, settle: 14 },
  { tint: "#ffd29a", letter: "S", verdict: "~ lacunes", color: ACCENTS.orange, settle: 20 },
  { tint: "#b5d4ff", letter: "T", verdict: "✓ correcte", color: ACCENTS.green, settle: 26 },
];

/** Trois relecteurs tirés au sort (les initiales défilent puis s'arrêtent), reliés à la solution. */
export function Reviewers({
  title,
  verdicts = false,
  continued = false,
}: {
  title?: string;
  verdicts?: boolean;
  /** Suite de la scène précédente : les relecteurs sont déjà tirés, seuls les verdicts arrivent. */
  continued?: boolean;
}) {
  const frame = useCurrentFrame();
  const t = continued ? frame + 60 : frame;
  const card = pop(t, 2, 16, 150);
  const verdictStart = continued ? 6 : 36;
  // Une relecture compte quand son verdict tombe, pas quand le relecteur est tiré.
  const reviewed = verdicts ? REVIEWERS.filter((_, index) => frame >= verdictStart + index * 7).length : 0;

  return (
    <>
      {title && (
        <div
          style={{
            position: "absolute",
            left: SAFE.left,
            width: SAFE.right - SAFE.left,
            top: 300,
            textAlign: "center",
            fontFamily: MONO,
            fontWeight: 800,
            fontSize: 50,
            color: COLORS.onDark,
            opacity: ease(t, 0, 8),
            transform: `translateY(${(1 - ease(t, 0, 10)) * 30}px)`,
          }}
        >
          {title}
        </div>
      )}

      <svg style={{ position: "absolute", inset: 0 }} width={1080} height={1920}>
        {REVIEWERS.map((reviewer, index) => {
          const x = SAFE.left + COLUMN * (index + 0.5);
          const draw = ease(t, reviewer.settle + 4, reviewer.settle + 14);
          const end = { x: (SAFE.left + SAFE.right) / 2 + (index - 1) * 120, y: CARD.top };
          const start = { x, y: AVATAR_Y + 80 };
          return (
            <line
              key={reviewer.letter}
              x1={start.x}
              y1={start.y}
              x2={start.x + (end.x - start.x) * draw}
              y2={start.y + (end.y - start.y) * draw}
              stroke="rgba(255,240,240,0.35)"
              strokeWidth={4}
              strokeDasharray="10 12"
              strokeDashoffset={-frame * 1.5}
              opacity={draw > 0 ? 1 : 0}
            />
          );
        })}
      </svg>

      {REVIEWERS.map((reviewer, index) => {
        const x = SAFE.left + COLUMN * (index + 0.5);
        const settled = t >= reviewer.settle;
        const appear = pop(t, index * 3, 14, 200);
        const lock = pop(t, reviewer.settle, 9, 260);
        const letter = settled ? reviewer.letter : LETTERS[(Math.floor(frame / 2) * 7 + index * 5) % LETTERS.length];
        const chip = verdicts ? pop(frame, verdictStart + index * 7, 12, 220) : 0;
        return (
          <div key={reviewer.letter}>
            <div
              style={{
                position: "absolute",
                left: x - 80,
                top: AVATAR_Y - 80,
                width: 160,
                height: 160,
                borderRadius: 80,
                background: settled ? reviewer.tint : COLORS.darkElevated,
                border: `5px solid ${settled ? reviewer.tint : "rgba(255,240,240,0.25)"}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: MONO,
                fontWeight: 800,
                fontSize: 78,
                color: settled ? COLORS.ink : COLORS.onDarkMute,
                transform: `scale(${appear * (settled ? 0.9 + 0.1 * lock : 0.92)})`,
                boxShadow: settled ? `0 0 ${40 * lock}px ${reviewer.tint}66` : "none",
              }}
            >
              {letter}
            </div>
            <div
              style={{
                position: "absolute",
                left: x - COLUMN / 2,
                width: COLUMN,
                top: AVATAR_Y - 130,
                textAlign: "center",
                fontFamily: MONO,
                fontSize: 28,
                color: COLORS.onDarkMute,
                opacity: appear,
              }}
            >
              {settled ? "tiré au sort" : "…"}
            </div>
            {verdicts && (
              <div
                style={{
                  position: "absolute",
                  left: x - COLUMN / 2 + 6,
                  width: COLUMN - 12,
                  top: AVATAR_Y + 100,
                  textAlign: "center",
                  fontFamily: MONO,
                  fontWeight: 800,
                  fontSize: 34,
                  color: COLORS.ink,
                  background: reviewer.color,
                  borderRadius: 14,
                  padding: "10px 0",
                  opacity: Math.min(1, chip * 1.5),
                  transform: `scale(${0.6 + 0.4 * chip})`,
                  zIndex: 2,
                }}
              >
                {reviewer.verdict}
              </div>
            )}
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          left: (SAFE.left + SAFE.right) / 2 - 300,
          width: 600,
          top: CARD.top,
          height: CARD.height,
          borderRadius: 24,
          background: COLORS.canvas,
          boxShadow: "0 40px 90px rgba(0,0,0,0.55)",
          padding: "30px 36px",
          boxSizing: "border-box",
          transform: `translateY(${(1 - card) * 300}px) rotate(${(1 - card) * -6}deg)`,
          opacity: Math.min(1, card * 2),
          color: COLORS.ink,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: MONO, fontSize: 30 }}>
          <span style={{ fontWeight: 800 }}>Ta solution</span>
          <span style={{ color: reviewed === 3 ? "#1f9d45" : COLORS.mute }}>
            {verdicts ? `${reviewed} / 3 relectures` : "en relecture…"}
          </span>
        </div>
        <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 14 }}>
          <Tex latex="u_{n+1} - u_n = \tfrac{1}{(n+1)^2} > 0" size={40} />
          <Tex latex="u_n \le 2 - \tfrac{1}{n}" size={40} />
          <Tex latex="\text{donc } (u_n) \text{ converge.}" size={40} />
        </div>
        {verdicts && (
          <div
            style={{
              position: "absolute",
              right: -50,
              bottom: -36,
              fontFamily: HAND,
              fontWeight: 700,
              fontSize: 50,
              color: COLORS.redPen,
              transform: `rotate(-6deg) scale(${pop(frame, verdictStart + 24, 12, 200)})`,
              background: "#fff6d6",
              padding: "6px 20px",
              borderRadius: 10,
              boxShadow: "0 10px 24px rgba(0,0,0,0.25)",
            }}
          >
            « pour tout n ≥ 1 ? »
          </div>
        )}
      </div>
    </>
  );
}
