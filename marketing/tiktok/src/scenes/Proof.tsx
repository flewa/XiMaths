import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Tex } from "../components/Tex";
import { ACCENTS, COLORS, HAND, SAFE } from "../theme";
import { RichLines } from "./Title";

type Mark = { line: number; type: "cross" | "check" | "question"; note?: string };

const LINE = 124;
const CARD = { left: SAFE.left + 10, width: SAFE.right - SAFE.left - 20 };
const MARGIN = 120;

function stampColor(stamp: string) {
  if (stamp === "?") return ACCENTS.orange;
  return stamp.startsWith("5/") ? "#1f9d45" : COLORS.redPen;
}

/** Une copie : les lignes s'écrivent, le correcteur annote au stylo rouge, puis tamponne la note. */
export function Proof({
  headline,
  title,
  lines,
  marks = [],
  stamp,
  instant = false,
}: {
  headline?: string;
  title?: string;
  lines: string[];
  marks?: Mark[];
  stamp?: string;
  instant?: boolean;
}) {
  const frame = useCurrentFrame();
  const enter = instant ? 1 : pop(frame, 0, 16, 150);
  // En ouverture, la copie est déjà écrite : seules les annotations arrivent.
  const lineStart = instant ? -60 : 6;
  const marksAt = instant ? 8 : lineStart + lines.length * 7 + 6;
  const stampAt = marksAt + marks.length * 7 + 4;
  const height = 150 + lines.length * LINE + 50;
  const stamped = stamp ? pop(frame, stampAt, 10, 240) : 0;
  // Sous un titre, la copie descend ; seule, elle se centre dans la zone utile.
  const top = headline ? 700 : Math.max(380, 740 - height / 2);

  return (
    <>
      {headline && (
        <div style={{ position: "absolute", left: SAFE.left, width: SAFE.right - SAFE.left, top: 300 }}>
          <RichLines text={headline} size={96} accent="orange" instant={instant} />
        </div>
      )}
      <div
        style={{
          position: "absolute",
          left: CARD.left,
          top,
          width: CARD.width,
          height,
          background: COLORS.paper,
          borderRadius: 10,
          boxShadow: "0 50px 100px rgba(0,0,0,0.55)",
          transform: `translateY(${(1 - enter) * 500}px) rotate(${-1.5 + (1 - enter) * -8}deg)`,
          backgroundImage: `linear-gradient(90deg, transparent ${MARGIN - 4}px, rgba(224,38,27,0.45) ${MARGIN - 4}px, rgba(224,38,27,0.45) ${MARGIN - 1}px, transparent ${MARGIN - 1}px), repeating-linear-gradient(180deg, transparent 0, transparent ${LINE - 2}px, rgba(70,110,190,0.22) ${LINE - 2}px, rgba(70,110,190,0.22) ${LINE}px)`,
          backgroundPosition: `0 0, 0 ${150 - LINE + 36}px`,
          overflow: "visible",
        }}
      >
        {title && (
          <div
            style={{
              position: "absolute",
              left: MARGIN + 24,
              top: 40,
              fontFamily: HAND,
              fontWeight: 700,
              fontSize: 64,
              color: COLORS.pen,
            }}
          >
            {title}
          </div>
        )}
        {lines.map((latex, index) => {
          const reveal = ease(frame, lineStart + index * 7, lineStart + index * 7 + 12);
          return (
            <div
              key={latex}
              style={{
                position: "absolute",
                left: MARGIN + 24,
                top: 150 + index * LINE,
                height: LINE,
                display: "flex",
                alignItems: "center",
                clipPath: `inset(0 ${(1 - reveal) * 100}% 0 0)`,
              }}
            >
              <Tex latex={latex} size={58} color={COLORS.pen} />
            </div>
          );
        })}
        <svg style={{ position: "absolute", inset: 0, overflow: "visible" }} width={CARD.width} height={height}>
          {marks.map((mark, index) => {
            const draw = ease(frame, marksAt + index * 7, marksAt + index * 7 + 12);
            const y = 150 + mark.line * LINE + LINE / 2;
            const color = mark.type === "check" ? "#1f9d45" : COLORS.redPen;
            if (mark.type === "question") {
              return (
                <ellipse
                  key={index}
                  cx={MARGIN + 330}
                  cy={y}
                  rx={300}
                  ry={58}
                  fill="none"
                  stroke={color}
                  strokeWidth={7}
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - draw}
                  transform={`rotate(-3 ${MARGIN + 330} ${y})`}
                />
              );
            }
            const x = CARD.width - 120;
            const path =
              mark.type === "check"
                ? `M ${x} ${y} l 26 30 l 52 -66`
                : `M ${x} ${y - 32} l 60 64 M ${x + 60} ${y - 32} l -60 64`;
            return (
              <path
                key={index}
                d={path}
                fill="none"
                stroke={color}
                strokeWidth={11}
                strokeLinecap="round"
                strokeLinejoin="round"
                pathLength={1}
                strokeDasharray={1}
                strokeDashoffset={1 - draw}
              />
            );
          })}
        </svg>
        {marks.map((mark, index) =>
          mark.note ? (
            <div
              key={`note-${index}`}
              style={{
                position: "absolute",
                left: mark.type === "question" ? MARGIN + 330 : CARD.width - 330,
                top: 150 + mark.line * LINE + (mark.type === "question" ? LINE - 6 : -40),
                fontFamily: HAND,
                fontWeight: 700,
                fontSize: 62,
                color: mark.type === "check" ? "#1f9d45" : COLORS.redPen,
                opacity: ease(frame, marksAt + index * 7 + 8, marksAt + index * 7 + 14),
                transform: "rotate(-5deg)",
                whiteSpace: "nowrap",
              }}
            >
              {mark.note}
            </div>
          ) : null,
        )}
        {stamp && (
          <div
            style={{
              position: "absolute",
              right: -20,
              top: -70,
              width: 230,
              height: 230,
              borderRadius: 115,
              border: `10px solid ${stampColor(stamp)}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: HAND,
              fontWeight: 700,
              fontSize: stamp.length > 2 ? 110 : 150,
              color: stampColor(stamp),
              background: "rgba(246,241,231,0.85)",
              opacity: Math.min(1, stamped * 2),
              transform: `rotate(${-14 + (1 - stamped) * 20}deg) scale(${2.2 - 1.2 * stamped})`,
            }}
          >
            {stamp}
          </div>
        )}
      </div>
    </>
  );
}
