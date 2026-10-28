import { Fragment } from "react";
import { useCurrentFrame } from "remotion";
import { ease, pop } from "../anim";
import { Tex } from "../components/Tex";
import { ACCENTS, COLORS, HAND, MONO, SAFE } from "../theme";

const PAPER = { left: SAFE.left + 10, width: SAFE.right - SAFE.left - 20, top: 360, height: 560 };
const LINE = 120;

/** ≤ et ≥ manquent à la police manuscrite : un chevron souligné à la main. */
function Handwritten({ text }: { text: string }) {
  return (
    <>
      {text.split(/([≤≥])/).map((part, index) =>
        part === "≤" || part === "≥" ? (
          <span key={index} style={{ position: "relative", display: "inline-block", padding: "0 0.08em" }}>
            {part === "≤" ? "<" : ">"}
            <span
              style={{
                position: "absolute",
                left: "0.1em",
                right: "0.08em",
                bottom: "0.16em",
                height: "0.06em",
                borderRadius: 4,
                background: "currentColor",
                transform: "rotate(-6deg)",
              }}
            />
          </span>
        ) : (
          <Fragment key={index}>{part}</Fragment>
        ),
      )}
    </>
  );
}

/** La copie s'écrit ; avec `source`, elle est photographiée, puis transcrite dans l'éditeur. */
export function Handwriting({ lines, source, preview }: { lines: string[]; source?: string; preview?: string[] }) {
  const frame = useCurrentFrame();
  const transcribe = Boolean(source);
  const enter = transcribe ? 1 : pop(frame, 0, 16, 140);
  const flash = transcribe ? Math.max(0, 1 - Math.abs(frame - 8) / 5) : 0;
  const shrink = transcribe ? ease(frame, 14, 30) : 0;
  const typed = source ? Math.floor(ease(frame, 30, 30 + source.length / 2.6, 0, source.length)) : 0;
  const previewAt = 30 + (source?.length ?? 0) / 2.6 + 2;

  return (
    <>
      <div
        style={{
          position: "absolute",
          left: PAPER.left,
          top: PAPER.top,
          width: PAPER.width,
          height: PAPER.height,
          transformOrigin: "50% 0",
          transform: `translateY(${(1 - enter) * 600 - shrink * 120}px) scale(${1 - 0.5 * shrink}) rotate(${(1 - enter) * 8 - 2 + shrink * 4}deg)`,
          background: COLORS.paper,
          borderRadius: 8,
          boxShadow: "0 50px 100px rgba(0,0,0,0.55)",
          backgroundImage: `repeating-linear-gradient(180deg, transparent 0, transparent ${LINE - 2}px, rgba(70,110,190,0.22) ${LINE - 2}px, rgba(70,110,190,0.22) ${LINE}px)`,
          backgroundPosition: "0 40px",
          padding: "70px 50px",
          boxSizing: "border-box",
        }}
      >
        {lines.map((line, index) => {
          const reveal = transcribe ? 1 : ease(frame, 6 + index * 14, 6 + index * 14 + 16, 0, 1);
          return (
            <div
              key={line}
              style={{
                height: LINE,
                fontFamily: HAND,
                fontWeight: 700,
                fontSize: 84,
                color: COLORS.pen,
                whiteSpace: "nowrap",
                clipPath: `inset(-20px ${(1 - reveal) * 100}% -20px 0)`,
              }}
            >
              <Handwritten text={line} />
            </div>
          );
        })}
        {transcribe && (
          <>
            {/* Viseur de l'appareil photo. */}
            {[0, 1, 2, 3].map((corner) => (
              <div
                key={corner}
                style={{
                  position: "absolute",
                  width: 90,
                  height: 90,
                  left: corner % 2 ? undefined : 18,
                  right: corner % 2 ? 18 : undefined,
                  top: corner < 2 ? 18 : undefined,
                  bottom: corner < 2 ? undefined : 18,
                  borderColor: "#ffffff",
                  borderStyle: "solid",
                  borderWidth: `${corner < 2 ? 8 : 0}px ${corner % 2 ? 8 : 0}px ${corner < 2 ? 0 : 8}px ${corner % 2 ? 0 : 8}px`,
                  opacity: 1 - shrink,
                  filter: "drop-shadow(0 0 6px rgba(0,0,0,0.5))",
                }}
              />
            ))}
            <div style={{ position: "absolute", inset: 0, background: "#ffffff", opacity: flash, borderRadius: 8 }} />
          </>
        )}
      </div>

      {transcribe && (
        <div
          style={{
            position: "absolute",
            left: SAFE.left,
            width: SAFE.right - SAFE.left,
            top: 690,
            opacity: ease(frame, 24, 32),
            transform: `translateY(${(1 - ease(frame, 24, 34)) * 80}px)`,
          }}
        >
          <div style={{ fontFamily: MONO, fontSize: 30, color: ACCENTS.green, marginBottom: 14 }}>
            [■] Photographier ma copie · transcrit ✓
          </div>
          <div
            style={{
              background: COLORS.card,
              borderRadius: 14,
              padding: "22px 26px",
              fontFamily: MONO,
              fontSize: 34,
              lineHeight: 1.45,
              color: COLORS.ink,
              minHeight: 150,
              boxShadow: "0 30px 70px rgba(0,0,0,0.45)",
            }}
          >
            {source?.slice(0, typed)}
            <span style={{ opacity: Math.floor(frame / 8) % 2 ? 1 : 0 }}>▌</span>
          </div>
          {preview && (
            <div
              style={{
                marginTop: 18,
                background: COLORS.canvas,
                borderLeft: `8px solid ${COLORS.ink}`,
                borderRadius: 8,
                padding: "18px 24px",
                display: "flex",
                flexDirection: "column",
                gap: 8,
                opacity: ease(frame, previewAt, previewAt + 8),
                transform: `scale(${0.94 + 0.06 * ease(frame, previewAt, previewAt + 10)})`,
                transformOrigin: "0 0",
              }}
            >
              {preview.map((latex) => (
                <Tex key={latex} latex={latex} size={38} color={COLORS.ink} />
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
}
