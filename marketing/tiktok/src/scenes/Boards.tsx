import { interpolate, useCurrentFrame } from "remotion";
import { ease, glide, pop } from "../anim";
import { Kicker } from "../components/Kicker";
import { ACCENTS, COLORS, MONO, SAFE } from "../theme";

const WIDTH = SAFE.right - SAFE.left;

/** Barre du site : [#####---------------], vingt crans. */
export function asciiBar(value: number, max: number, cells = 20) {
  const filled = Math.round((Math.min(value, max) / max) * cells);
  return `[${"#".repeat(filled)}${"-".repeat(cells - filled)}]`;
}

const decimal = (value: number) => value.toFixed(1).replace(".", ",");

/** Carte de compétences, comme sur la page de progression ; avec `next`, le chapitre à travailler ressort. */
export function Skills({ chapters, next }: { chapters: { name: string; value: number }[]; next?: string }) {
  const frame = useCurrentFrame();
  const highlight = next ? pop(frame, 8, 14, 160) : 0;
  return (
    <>
      <div style={{ position: "absolute", left: SAFE.left, top: 300 }}>
        <Kicker text="progression --carte" delay={-10} />
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: WIDTH,
          top: 400,
          display: "flex",
          flexDirection: "column",
          gap: 22,
        }}
      >
        {chapters.map((chapter, index) => {
          const appear = pop(frame, index * 3, 15, 200);
          const fill = next ? 1 : ease(frame, 6 + index * 3, 26 + index * 3);
          const value = chapter.value * fill;
          const chosen = chapter.name === next;
          const dim = next && !chosen ? 1 - 0.55 * highlight : 1;
          return (
            <div
              key={chapter.name}
              style={{
                position: "relative",
                padding: "16px 22px",
                borderRadius: 18,
                background: chosen ? `rgba(48,209,88,${0.12 * highlight})` : "transparent",
                border: `4px solid ${chosen ? `rgba(48,209,88,${highlight})` : "transparent"}`,
                opacity: Math.min(1, appear * 1.4) * dim,
                transform: `translateX(${(1 - appear) * -80}px) scale(${chosen ? 1 + 0.04 * highlight : 1})`,
                fontFamily: MONO,
                color: COLORS.onDark,
              }}
            >
              <div style={{ fontSize: 44, fontWeight: 800 }}>{chapter.name}</div>
              <div style={{ fontSize: 38, marginTop: 4, whiteSpace: "nowrap" }}>
                <span
                  style={{
                    color: chapter.value >= 3 ? ACCENTS.green : chapter.value >= 2 ? ACCENTS.orange : ACCENTS.red,
                  }}
                >
                  {asciiBar(value, 5)}
                </span>{" "}
                <span style={{ color: COLORS.onDarkMute }}>{decimal(value)} / 5</span>
              </div>
              {chosen && (
                <div
                  style={{
                    position: "absolute",
                    right: -6,
                    top: -34,
                    fontSize: 32,
                    fontWeight: 800,
                    color: COLORS.ink,
                    background: ACCENTS.green,
                    borderRadius: 12,
                    padding: "8px 18px",
                    transform: `scale(${pop(frame, 16, 12, 220)})`,
                  }}
                >
                  prochain : difficulté 2 ↑
                </div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

/** Classement de la semaine : tu gagnes des points et passes devant. */
export function Leaderboard({
  rows,
  duration,
  instant = false,
}: {
  rows: { name: string; points: number; you?: boolean }[];
  duration: number;
  instant?: boolean;
}) {
  const frame = useCurrentFrame();
  const gainAt = Math.round(duration * 0.5);
  const gain = 40;
  const swap = glide(frame, gainAt + 12, 16);
  const youIndex = rows.findIndex((row) => row.you);
  const ROW = 150;
  const TOP = 520;

  return (
    <>
      <div style={{ position: "absolute", left: SAFE.left, top: 300 }}>
        <Kicker text="classements --semaine" delay={-20} />
      </div>
      <div
        style={{
          position: "absolute",
          left: SAFE.left,
          width: WIDTH,
          top: TOP - 80,
          display: "flex",
          fontFamily: MONO,
          fontSize: 32,
          color: COLORS.onDarkMute,
          padding: "0 30px",
          boxSizing: "border-box",
        }}
      >
        <span style={{ width: 110 }}>Rang</span>
        <span style={{ flex: 1 }}>Pseudo</span>
        <span>Points</span>
      </div>
      {rows.map((row, index) => {
        const appear = instant ? 1 : pop(frame, index * 3 - 6, 15, 200);
        const target = row.you ? 0 : index < youIndex ? index + 1 : index;
        const place = interpolate(swap, [0, 1], [index, target]);
        const points = row.you ? row.points + Math.round(ease(frame, gainAt, gainAt + 10) * gain) : row.points;
        const rank = Math.round(place) + 1;
        return (
          <div
            key={row.name}
            style={{
              position: "absolute",
              left: SAFE.left,
              width: WIDTH,
              top: TOP + place * ROW,
              height: ROW - 22,
              display: "flex",
              alignItems: "center",
              padding: "0 30px",
              boxSizing: "border-box",
              borderRadius: 20,
              background: row.you ? "rgba(48,209,88,0.16)" : COLORS.darkElevated,
              border: row.you ? `4px solid ${ACCENTS.green}` : "2px solid rgba(255,240,240,0.08)",
              fontFamily: MONO,
              fontWeight: 800,
              fontSize: 54,
              color: COLORS.onDark,
              opacity: Math.min(1, appear * 1.4),
              transform: `translateX(${(1 - appear) * 120}px) scale(${row.you ? 1 + 0.05 * Math.sin(Math.PI * swap) : 1})`,
              zIndex: row.you ? 2 : 1,
            }}
          >
            <span style={{ width: 110, color: rank === 1 ? ACCENTS.orange : COLORS.onDarkMute }}>{rank}</span>
            <span style={{ flex: 1 }}>{row.name}</span>
            <span style={{ fontVariantNumeric: "tabular-nums" }}>{points}</span>
          </div>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: SAFE.right - 260,
          top: TOP - 10 + youIndex * ROW,
          fontFamily: MONO,
          fontWeight: 800,
          fontSize: 40,
          color: COLORS.ink,
          background: ACCENTS.green,
          borderRadius: 12,
          padding: "6px 16px",
          opacity: frame >= gainAt ? Math.max(0, 1 - (frame - gainAt - 16) / 10) : 0,
          transform: `translateY(${-ease(frame, gainAt, gainAt + 20) * 60}px)`,
          zIndex: 3,
        }}
      >
        +{gain} défi
      </div>
    </>
  );
}

/** Objectif daté : la barre se remplit, le verdict tombe. */
export function Goal({
  title,
  done,
  target,
  deadline,
  continued = false,
}: {
  title: string;
  done: number;
  target: number;
  deadline: string;
  continued?: boolean;
}) {
  const frame = useCurrentFrame();
  const card = continued ? 1 : pop(frame, 0, 16, 150);
  const fill = ease(frame, 8, 30);
  const value = Math.round(done * fill);
  const chip = pop(frame, 32, 12, 220);
  return (
    <div
      style={{
        position: "absolute",
        left: SAFE.left,
        width: WIDTH,
        top: 560,
        borderRadius: 26,
        background: COLORS.canvas,
        padding: "44px 44px 54px",
        boxSizing: "border-box",
        fontFamily: MONO,
        color: COLORS.ink,
        boxShadow: "0 50px 100px rgba(0,0,0,0.55)",
        transform: `translateY(${(1 - card) * 400}px) rotate(${(1 - card) * -5}deg)`,
      }}
    >
      <div style={{ fontSize: 34, color: COLORS.mute }}>Mes objectifs</div>
      <div style={{ fontSize: 62, fontWeight: 800, marginTop: 14 }}>{title}</div>
      <div style={{ fontSize: 40, marginTop: 24, whiteSpace: "nowrap" }}>
        {asciiBar(value, target, 16)}{" "}
        <span style={{ fontWeight: 800 }}>
          {value} / {target}
        </span>
      </div>
      <div style={{ fontSize: 34, color: COLORS.mute, marginTop: 14 }}>{deadline}</div>
      <div
        style={{
          position: "absolute",
          right: 34,
          bottom: -34,
          fontSize: 40,
          fontWeight: 800,
          background: ACCENTS.green,
          borderRadius: 14,
          padding: "10px 24px",
          transform: `rotate(-4deg) scale(${chip})`,
        }}
      >
        dans les temps ✓
      </div>
    </div>
  );
}
