import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Kicker } from "../components/Kicker";
import { ACCENTS, COLORS, FPS, MONO, SAFE } from "../theme";

const CENTER = { x: (SAFE.left + SAFE.right) / 2, y: 760 };
const RADIUS = 300;
const TICKS = 60;

/** Chronomètre : l'anneau se dessine, les secondes défilent. Avec `extra`, le temps
 * passe de minutes − 10 à minutes, comme le tiers-temps. */
export function Timer({
  minutes,
  label,
  extra,
  instant = false,
}: {
  minutes: number;
  label?: string;
  extra?: string;
  instant?: boolean;
}) {
  const frame = useCurrentFrame();
  const draw = instant ? 1 : ease(frame, 0, 14);
  const bump = extra ? Math.round(ease(frame, 12, 26, 0, 10)) : 10;
  const shown = minutes - 10 + bump;
  const elapsed = Math.max(0, frame - (extra ? 30 : 6)) / FPS;
  const total = shown * 60 - Math.floor(elapsed);
  const mm = String(Math.floor(total / 60)).padStart(2, "0");
  const ss = String(total % 60).padStart(2, "0");
  const beat = 1 + 0.03 * Math.max(0, 1 - (frame % FPS) / 6);
  const chip = extra ? pop(frame, 12, 11, 220) : 0;
  const orange = ACCENTS.orange;

  return (
    <>
      {label && (
        <div style={{ position: "absolute", left: SAFE.left, top: 300 }}>
          <Kicker text={label} delay={instant ? -20 : 0} size={44} />
        </div>
      )}
      <svg style={{ position: "absolute", inset: 0 }} width={1080} height={1920}>
        <circle
          cx={CENTER.x}
          cy={CENTER.y}
          r={RADIUS}
          fill="rgba(255,159,10,0.06)"
          stroke="rgba(255,240,240,0.12)"
          strokeWidth={26}
        />
        <circle
          cx={CENTER.x}
          cy={CENTER.y}
          r={RADIUS}
          fill="none"
          stroke={orange}
          strokeWidth={26}
          strokeLinecap="round"
          strokeDasharray={2 * Math.PI * RADIUS}
          strokeDashoffset={2 * Math.PI * RADIUS * (1 - draw * (1 - elapsed / (shown * 60)))}
          transform={`rotate(-90 ${CENTER.x} ${CENTER.y})`}
          style={{ filter: `drop-shadow(0 0 24px ${orange}88)` }}
        />
        {Array.from({ length: TICKS }, (_, index) => {
          const angle = (index / TICKS) * 2 * Math.PI - Math.PI / 2;
          const long = index % 5 === 0;
          const inner = RADIUS - (long ? 64 : 48);
          const outer = RADIUS - 34;
          const lit = index / TICKS <= draw;
          return (
            <line
              key={index}
              x1={CENTER.x + Math.cos(angle) * inner}
              y1={CENTER.y + Math.sin(angle) * inner}
              x2={CENTER.x + Math.cos(angle) * outer}
              y2={CENTER.y + Math.sin(angle) * outer}
              stroke={lit ? "rgba(255,240,240,0.55)" : "rgba(255,240,240,0.1)"}
              strokeWidth={long ? 6 : 3}
              strokeLinecap="round"
            />
          );
        })}
      </svg>
      <div
        style={{
          position: "absolute",
          left: CENTER.x - RADIUS,
          width: RADIUS * 2,
          top: CENTER.y - 90,
          textAlign: "center",
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 160,
          lineHeight: "180px",
          color: COLORS.onDark,
          fontVariantNumeric: "tabular-nums",
          transform: `scale(${beat})`,
        }}
      >
        {mm}:{ss}
      </div>
      {extra && (
        <div
          style={{
            position: "absolute",
            left: CENTER.x + 150,
            top: CENTER.y - 300,
            fontFamily: MONO,
            fontWeight: 800,
            fontSize: 54,
            color: COLORS.ink,
            background: orange,
            borderRadius: 16,
            padding: "10px 24px",
            transform: `rotate(8deg) scale(${chip})`,
          }}
        >
          {extra}
        </div>
      )}
    </>
  );
}
