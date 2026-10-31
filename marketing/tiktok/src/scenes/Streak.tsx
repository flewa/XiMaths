import { interpolate, useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Kicker } from "../components/Kicker";
import { ACCENTS, COLORS, MONO, SAFE } from "../theme";

const MID = (SAFE.left + SAFE.right) / 2;

/** La série quotidienne d'une autre appli qui meurt pendant les partiels. */
export function StreakBreak({ days, duration }: { days: number; duration: number }) {
  const frame = useCurrentFrame();
  const breakAt = Math.round(duration * 0.42);
  const broken = frame >= breakAt;
  const count = broken ? 0 : days;
  const dying = ease(frame, breakAt - 4, breakAt + 8);
  const shake = broken ? Math.sin(frame * 2.3) * 14 * Math.max(0, 1 - (frame - breakAt) / 12) : 0;
  const flicker = 1 + Math.sin(frame * 0.9) * 0.04 + Math.sin(frame * 2.1) * 0.025;
  const chip = pop(frame, breakAt + 10, 12, 200);

  return (
    <>
      <div style={{ position: "absolute", left: SAFE.left, top: 300 }}>
        <Kicker text="série quotidienne" delay={-20} />
      </div>
      <svg
        style={{ position: "absolute", left: MID - 190, top: 420, overflow: "visible" }}
        width={380}
        height={460}
        viewBox="0 0 380 460"
      >
        <defs>
          <linearGradient id="flame" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0" stopColor="#ff3b30" />
            <stop offset="0.55" stopColor="#ff9f0a" />
            <stop offset="1" stopColor="#ffd60a" />
          </linearGradient>
        </defs>
        <g
          style={{
            transformOrigin: "190px 440px",
            transform: `scale(${(1 - 0.75 * dying) * flicker}, ${(1 - 0.85 * dying) * (2 - flicker)})`,
            filter: `grayscale(${dying}) drop-shadow(0 0 ${50 * (1 - dying)}px #ff9f0a)`,
            opacity: 1 - 0.6 * dying,
          }}
        >
          <path
            d="M190 20 C 250 120 340 180 330 300 C 322 390 262 440 190 440 C 118 440 58 390 50 300 C 44 220 100 180 120 100 C 150 160 160 190 190 200 C 170 140 170 80 190 20 Z"
            fill="url(#flame)"
          />
          <path
            d="M190 210 C 230 270 270 300 262 360 C 256 410 226 432 190 432 C 154 432 124 410 118 360 C 114 320 140 300 156 260 C 168 290 176 300 190 304 C 182 270 182 240 190 210 Z"
            fill="#fff3c4"
            opacity={0.9}
          />
        </g>
        {broken &&
          [0, 1, 2].map((puff) => {
            const t = (frame - breakAt - puff * 4) / 30;
            return t > 0 && t < 1 ? (
              <circle
                key={puff}
                cx={190 + (puff - 1) * 30}
                cy={360 - t * 260}
                r={30 + t * 50}
                fill="rgba(200,200,200,0.18)"
                opacity={1 - t}
              />
            ) : null;
          })}
      </svg>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.right - SAFE.left,
          top: 930,
          textAlign: "center",
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 132,
          color: broken ? ACCENTS.red : COLORS.onDark,
          transform: `translateX(${shake}px)`,
        }}
      >
        {count} jour{count > 1 ? "s" : ""}
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.right - SAFE.left,
          top: 1110,
          display: "flex",
          justifyContent: "center",
          opacity: chip,
          transform: `scale(${0.7 + 0.3 * chip})`,
        }}
      >
        <span
          style={{
            fontFamily: MONO,
            fontWeight: 800,
            fontSize: 46,
            color: COLORS.ink,
            background: ACCENTS.red,
            borderRadius: 14,
            padding: "10px 26px",
          }}
        >
          perdue en plein partiel
        </span>
      </div>
    </>
  );
}

const DAYS = ["L", "M", "M", "J", "V", "S", "D"];
const CELL = 84;
const GAP = 12;
const GRID_LEFT = SAFE.left + 30;
const GRID_TOP = 470;
const GOAL = 3;

const WEEKLY = [
  [1, 0, 1, 0, 1, 0, 0],
  [0, 1, 0, 0, 1, 1, 0],
  [1, 0, 0, 1, 0, 0, 1],
  [0, 0, 1, 1, 0, 1, 0],
  [1, 1, 0, 0, 1, 0, 0],
];
// La quatrième semaine n'a qu'un jour actif : un joker la sauve.
const JOKER = [
  [1, 0, 1, 0, 1, 0, 0],
  [0, 1, 0, 0, 1, 1, 0],
  [1, 0, 0, 1, 0, 0, 1],
  [0, 0, 0, 1, 0, 0, 0],
  [1, 1, 0, 0, 1, 0, 0],
];

/** Une série hebdomadaire : trois jours actifs suffisent ; avec `joker`, une semaine manquée est sauvée. */
export function Weeks({ mode }: { mode: "weekly" | "joker" }) {
  const frame = useCurrentFrame();
  const weeks = mode === "joker" ? JOKER : WEEKLY;
  const rowAt = (row: number) => 6 + row * 9;
  const jokerRow = 3;
  const jokerAt = rowAt(jokerRow) + 10;
  const jokerFly = mode === "joker" ? ease(frame, jokerAt, jokerAt + 14) : 0;
  const statusLeft = GRID_LEFT + 7 * (CELL + GAP) + 20;

  const held = weeks.filter(
    (week, row) =>
      frame >= rowAt(row) + 8 &&
      (week.reduce((a, b) => a + b, 0) >= GOAL || (mode === "joker" && row === jokerRow && jokerFly >= 1)),
  ).length;
  const jokersLeft = mode === "joker" && jokerFly >= 1 ? 1 : 2;

  return (
    <>
      <div style={{ position: "absolute", left: SAFE.left, top: 300 }}>
        <Kicker
          text={
            mode === "joker" ? `jokers ce mois-ci : ${jokersLeft} / 2` : `objectif : ${GOAL} jours actifs / semaine`
          }
          delay={-10}
        />
      </div>
      <div style={{ position: "absolute", left: GRID_LEFT, top: GRID_TOP - 70, display: "flex", gap: GAP }}>
        {DAYS.map((day, index) => (
          <div
            key={index}
            style={{ width: CELL, textAlign: "center", fontFamily: MONO, fontSize: 34, color: COLORS.onDarkMute }}
          >
            {day}
          </div>
        ))}
      </div>
      {weeks.map((week, row) => {
        const ok = week.reduce((a, b) => a + b, 0) >= GOAL;
        const status = pop(frame, rowAt(row) + 8, 12, 220);
        const saved = mode === "joker" && row === jokerRow;
        return (
          <div key={row}>
            {week.map((active, day) => {
              const lit = active ? pop(frame, rowAt(row) + day, 14, 240) : 0;
              return (
                <div
                  key={day}
                  style={{
                    position: "absolute",
                    left: GRID_LEFT + day * (CELL + GAP),
                    top: GRID_TOP + row * (CELL + GAP),
                    width: CELL,
                    height: CELL,
                    borderRadius: 16,
                    background: COLORS.darkElevated,
                    border: "2px solid rgba(255,240,240,0.08)",
                    opacity: ease(frame, rowAt(row) - 4, rowAt(row) + 2),
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      inset: 6,
                      borderRadius: 11,
                      background: ACCENTS.green,
                      transform: `scale(${lit})`,
                      opacity: lit,
                    }}
                  />
                </div>
              );
            })}
            <div
              style={{
                position: "absolute",
                left: statusLeft,
                top: GRID_TOP + row * (CELL + GAP),
                height: CELL,
                display: "flex",
                alignItems: "center",
                fontFamily: MONO,
                fontWeight: 800,
                fontSize: 52,
                color: saved ? ACCENTS.orange : ok ? ACCENTS.green : COLORS.onDarkMute,
                opacity: saved ? jokerFly : status,
                transform: `scale(${saved ? 0.6 + 0.4 * jokerFly : 0.6 + 0.4 * status})`,
              }}
            >
              {saved ? "J" : ok ? "✓" : "·"}
            </div>
          </div>
        );
      })}
      {mode === "joker" && jokerFly > 0 && jokerFly < 1 && (
        <div
          style={{
            position: "absolute",
            left: interpolate(jokerFly, [0, 1], [SAFE.right - 120, statusLeft - 10]),
            top: interpolate(jokerFly, [0, 1], [300, GRID_TOP + jokerRow * (CELL + GAP)]),
            width: 80,
            height: 100,
            borderRadius: 12,
            background: ACCENTS.orange,
            color: COLORS.ink,
            fontFamily: MONO,
            fontWeight: 800,
            fontSize: 56,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `rotate(${(1 - jokerFly) * 30}deg)`,
            boxShadow: "0 16px 40px rgba(0,0,0,0.5)",
          }}
        >
          J
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: SAFE.right - SAFE.left,
          top: GRID_TOP + 5 * (CELL + GAP) + 40,
          textAlign: "center",
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 64,
          color: COLORS.onDark,
        }}
      >
        <span style={{ color: ACCENTS.green }}>{held}</span> semaine{held > 1 ? "s" : ""} d&apos;affilée
      </div>
    </>
  );
}
