import { Img, staticFile, useCurrentFrame } from "remotion";
import { ease, glide, pop } from "../anim";
import { COLORS, MONO, SAFE } from "../theme";
import manifest from "../../public/shots/manifest.json";

type Rect = { x: number; y: number; w: number; h: number };
type ShotInfo = { width: number; height: number; scale: number; focus: Record<string, Rect> };
const SHOTS = manifest as Record<string, ShotInfo>;

/** Pixels de la vidéo par pixel CSS du téléphone. */
export const K = 1.64;
const BEZEL = 16;
const STATUS = 44;
const SCREEN = { width: 390, height: 844 };
const OUTER = { width: SCREEN.width * K + 2 * BEZEL, height: SCREEN.height * K + 2 * BEZEL };
const LEFT = (SAFE.left + SAFE.right) / 2 - OUTER.width / 2;
const TOP = 300;
/** Hauteur de page visible au-dessus des sous-titres, en pixels CSS. */
const VISIBLE = (1200 - (TOP + BEZEL + STATUS * K)) / K;
/** Où la caméra amène l'élément visé. */
const TARGET = { x: (SAFE.left + SAFE.right) / 2, y: 760 };
const TALL_TARGET = { x: TARGET.x, y: 440 };

export function shotInfo(shot: string) {
  const info = SHOTS[shot];
  if (!info) throw new Error(`Capture inconnue : ${shot}. Lance npm run captures.`);
  return info;
}

/** Téléphone qui monte, fait défiler la capture jusqu'à l'élément visé, puis zoome dessus. */
export function Phone({
  shot,
  focus,
  label,
  tap,
  accent,
  continued = false,
}: {
  shot: string;
  focus?: string;
  label?: string;
  tap?: string;
  accent: string;
  /** Suite de la scène précédente, sur le même écran : la caméra est déjà en place. */
  continued?: boolean;
}) {
  const frame = useCurrentFrame();
  const t = continued ? frame + 90 : frame;
  const info = shotInfo(shot);
  const rect = focus ? info.focus[focus] : undefined;
  if (focus && !rect) throw new Error(`« ${focus} » absent de la capture ${shot}.`);
  const maxScroll = Math.max(0, info.height - (SCREEN.height - STATUS));

  // Un élément plus haut que l'écran : la caméra vise son haut plutôt que son centre.
  const tall = rect ? rect.h > VISIBLE - 40 : false;
  let scroll = 0;
  let zoom = 1;
  if (rect) {
    scroll = Math.min(maxScroll, Math.max(0, tall ? rect.y - 24 : rect.y + rect.h / 2 - VISIBLE / 2));
    const fit = 880 / (rect.w * K);
    zoom = Math.min(1.5, Math.max(1, tall ? fit : Math.min(fit, 560 / (rect.h * K))));
  }

  const enter = pop(t, 0, 16, 120);
  const scrolled = glide(t, 8, 22);
  const zoomed = glide(t, 24, 20);
  const currentScroll = scroll * scrolled;

  // Point visé (centre de l'élément, ou milieu de son bord haut), dans la vidéo, avant le zoom.
  const anchor = rect
    ? {
        x: LEFT + BEZEL + (rect.x + rect.w / 2) * K,
        y: TOP + BEZEL + (STATUS + (tall ? rect.y : rect.y + rect.h / 2) - scroll) * K,
      }
    : TARGET;
  const s = 1 + (zoom - 1) * zoomed;
  const moveTo = zoom === 1 ? anchor : tall ? TALL_TARGET : TARGET;
  const position = { x: anchor.x + (moveTo.x - anchor.x) * zoomed, y: anchor.y + (moveTo.y - anchor.y) * zoomed };
  const translate = { x: position.x - s * anchor.x, y: position.y - s * anchor.y };

  const ring = rect ? pop(t, 34, 18, 160) : 0;
  const chip = label ? pop(frame, continued ? 4 : 38, 13, 190) : 0;
  const tapAt = tap ? info.focus[tap] : undefined;
  const ripple = continued ? ease(frame, 0, 14) : ease(frame, 18, 34);

  const chipTop = rect ? Math.max(SAFE.top, position.y - (tall ? 0 : (rect.h * K * s) / 2) - 120) : SAFE.top;

  return (
    <>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transformOrigin: "0 0",
          transform: `translate(${translate.x}px, ${translate.y}px) scale(${s})`,
        }}
      >
        <div
          style={{
            position: "absolute",
            left: LEFT,
            top: TOP,
            width: OUTER.width,
            height: OUTER.height,
            borderRadius: 96,
            background: "#0c0a0a",
            boxShadow: "0 0 0 3px #3b3434, 0 60px 120px rgba(0,0,0,0.6)",
            transform: `translateY(${(1 - enter) * 700}px) rotate(${(1 - enter) * 7}deg)`,
          }}
        >
          <div
            style={{
              position: "absolute",
              left: BEZEL,
              top: BEZEL,
              width: SCREEN.width * K,
              height: SCREEN.height * K,
              borderRadius: 80,
              overflow: "hidden",
              background: COLORS.canvas,
            }}
          >
            <div
              style={{
                position: "absolute",
                left: 0,
                top: STATUS * K,
                transform: `translateY(${-currentScroll * K}px)`,
              }}
            >
              <Img
                src={staticFile(`shots/${shot}.png`)}
                style={{ width: SCREEN.width * K, height: info.height * K, display: "block" }}
              />
              {rect && (
                <div
                  style={{
                    position: "absolute",
                    left: rect.x * K - 12,
                    top: rect.y * K - 12,
                    width: rect.w * K + 24,
                    height: rect.h * K + 24,
                    borderRadius: 18,
                    border: `5px solid ${accent}`,
                    boxShadow: `0 0 0 4000px rgba(20,16,16,${0.38 * ring}), 0 0 40px ${accent}`,
                    opacity: ring,
                    transform: `scale(${1.08 - 0.08 * ring})`,
                  }}
                />
              )}
              {tapAt && ripple > 0 && ripple < 1 && (
                <div
                  style={{
                    position: "absolute",
                    left: (tapAt.x + 40) * K - 60,
                    top: (tapAt.y + 50) * K - 60,
                    width: 120,
                    height: 120,
                    borderRadius: 60,
                    background: "rgba(32,29,29,0.25)",
                    border: "4px solid rgba(32,29,29,0.5)",
                    transform: `scale(${0.4 + ripple})`,
                    opacity: 1 - ripple,
                  }}
                />
              )}
            </div>
            <StatusBar />
          </div>
        </div>
      </div>
      {label && (
        <div
          style={{
            position: "absolute",
            left: SAFE.left,
            width: SAFE.right - SAFE.left,
            top: chipTop,
            display: "flex",
            justifyContent: "center",
            transform: `translateY(${(1 - chip) * 30}px) scale(${0.7 + 0.3 * chip})`,
            opacity: Math.min(1, chip * 1.5),
          }}
        >
          <div
            style={{
              fontFamily: MONO,
              fontWeight: 800,
              fontSize: 44,
              color: COLORS.ink,
              background: accent,
              borderRadius: 16,
              padding: "14px 28px",
              boxShadow: "0 16px 40px rgba(0,0,0,0.45)",
              whiteSpace: "nowrap",
            }}
          >
            {label} ↓
          </div>
        </div>
      )}
    </>
  );
}

function StatusBar() {
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: SCREEN.width * K,
        height: STATUS * K,
        background: COLORS.canvas,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "6px 56px 0 64px",
        boxSizing: "border-box",
        fontFamily: "-apple-system, 'Helvetica Neue', Arial, sans-serif",
        fontWeight: 600,
        fontSize: 30,
        color: COLORS.ink,
      }}
    >
      <span>9:41</span>
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: 16,
          width: 200,
          height: 58,
          marginLeft: -100,
          borderRadius: 30,
          background: "#000",
        }}
      />
      <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <svg width="34" height="22" viewBox="0 0 17 11" aria-hidden>
          {[0, 1, 2, 3].map((bar) => (
            <rect
              key={bar}
              x={bar * 4.5}
              y={8 - bar * 2.5}
              width="3"
              height={3 + bar * 2.5}
              rx="0.8"
              fill={COLORS.ink}
            />
          ))}
        </svg>
        <svg width="50" height="24" viewBox="0 0 25 12" aria-hidden>
          <rect x="0.5" y="0.5" width="21" height="11" rx="3" fill="none" stroke={COLORS.ink} strokeOpacity="0.4" />
          <rect x="2" y="2" width="16" height="8" rx="1.8" fill={COLORS.ink} />
          <rect x="22.5" y="4" width="1.6" height="4" rx="0.8" fill={COLORS.ink} fillOpacity="0.4" />
        </svg>
      </span>
    </div>
  );
}
