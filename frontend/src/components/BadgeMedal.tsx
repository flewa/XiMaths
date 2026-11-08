import { useId } from "react";

import { BADGE_ART, type BadgeShape, FALLBACK_ART } from "@/lib/profile-art";

/** Mélange deux couleurs #rrggbb : `amount` vaut 0 pour `color`, 1 pour `target`. */
function mix(color: string, target: string, amount: number) {
  const channels = (hex: string) => [1, 3, 5].map((start) => parseInt(hex.slice(start, start + 2), 16));
  const [from, to] = [channels(color), channels(target)];
  return `#${from
    .map((value, index) => Math.round(value + (to[index] - value) * amount).toString(16).padStart(2, "0"))
    .join("")}`;
}

const HEXAGON = (radius: number) =>
  Array.from({ length: 6 }, (_, index) => {
    const angle = (Math.PI / 3) * index - Math.PI / 2;
    return `${(32 + radius * Math.cos(angle)).toFixed(2)},${(32 + radius * Math.sin(angle)).toFixed(2)}`;
  }).join(" ");

const SHIELD = "M32 3 L57 11.5 V30 C57 45 46.5 55.5 32 61 C17.5 55.5 7 45 7 30 V11.5 Z";

/** La forme du badge, réduite d'un facteur `scale` autour du centre. */
function Shape({
  shape,
  scale = 1,
  strokeWidth,
  ...props
}: { shape: BadgeShape; scale?: number; strokeWidth?: number } & React.SVGProps<SVGElement>) {
  if (shape === "circle") {
    return <circle cx="32" cy="32" r={30 * scale} strokeWidth={strokeWidth} {...(props as React.SVGProps<SVGCircleElement>)} />;
  }
  if (shape === "hexagon") {
    return <polygon points={HEXAGON(30.5 * scale)} strokeWidth={strokeWidth} {...(props as React.SVGProps<SVGPolygonElement>)} />;
  }
  // L'écusson est réduit par une transformation, qui réduirait aussi son trait.
  return (
    <path
      d={SHIELD}
      transform={scale === 1 ? undefined : `translate(32 32) scale(${scale}) translate(-32 -32)`}
      strokeWidth={strokeWidth === undefined ? undefined : strokeWidth / scale}
      {...(props as React.SVGProps<SVGPathElement>)}
    />
  );
}

const glyphFont = "KaTeX_Main, 'Latin Modern Roman', Georgia, serif";

/** Médaille d'un badge : un rebord en relief de sa couleur, un émail de la même teinte, un
 * reflet, et son symbole mathématique ; les paliers (bronze, argent, or) ajoutent des points.
 * Pas encore obtenue (`locked`), elle n'est qu'une empreinte en pointillés. Décorative si
 * `label` manque. */
export function BadgeMedal({
  slug,
  size = 56,
  locked = false,
  label,
}: {
  slug: string;
  size?: number;
  locked?: boolean;
  label?: string;
}) {
  const id = `medaille${useId().replace(/[^\w-]/g, "")}`;
  const art = BADGE_ART[slug] ?? FALLBACK_ART;
  const tier = art.tier ?? 0;
  const glyphY = (art.shape === "shield" ? 31 : 32) - (tier ? 4 : 0);
  const glyph = {
    x: 32,
    textAnchor: "middle",
    dominantBaseline: "central",
    fontFamily: glyphFont,
    fontSize: art.glyph.length > 1 ? 17 : 24,
  } as const;
  const dots = (fill: string) =>
    Array.from({ length: tier }, (_, index) => (
      <circle key={index} cx={32 + (index - (tier - 1) / 2) * 5} cy={glyphY + 16} r={1.6} fill={fill} />
    ));
  const svg = {
    viewBox: "0 0 64 64",
    width: size,
    height: size,
    role: label ? "img" : undefined,
    "aria-label": label,
    "aria-hidden": label ? undefined : true,
    className: "shrink-0 overflow-visible",
  } as const;

  if (locked) {
    return (
      <svg {...svg}>
        <Shape
          shape={art.shape}
          scale={0.97}
          fill="var(--surface-card)"
          stroke="var(--hairline-strong)"
          strokeWidth={1.75}
          strokeDasharray="4 3"
        />
        <text {...glyph} y={glyphY} fill="var(--stone)">
          {art.glyph}
        </text>
        {dots("var(--stone)")}
      </svg>
    );
  }

  const light = mix(art.tint, "#ffffff", 0.5);
  const dark = mix(art.tint, "#000000", 0.45);
  return (
    // En grand, la médaille diffuse un peu de sa couleur autour d'elle.
    <svg {...svg} style={size >= 48 ? { filter: `drop-shadow(0 4px 10px ${art.tint}55)` } : undefined}>
      <defs>
        <linearGradient id={`${id}-rebord`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={light} />
          <stop offset="0.5" stopColor={art.tint} />
          <stop offset="1" stopColor={dark} />
        </linearGradient>
        <linearGradient id={`${id}-biseau`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={dark} />
          <stop offset="1" stopColor={light} />
        </linearGradient>
        <radialGradient id={`${id}-email`} cx="0.5" cy="0.35" r="0.7">
          <stop offset="0" stopColor={mix(art.tint, "#000000", 0.45)} />
          <stop offset="1" stopColor={mix(art.tint, "#000000", 0.82)} />
        </radialGradient>
        <clipPath id={`${id}-champ`}>
          <Shape shape={art.shape} scale={0.8} />
        </clipPath>
      </defs>
      <Shape shape={art.shape} fill={`url(#${id}-rebord)`} />
      <Shape shape={art.shape} scale={0.88} fill={`url(#${id}-biseau)`} />
      <Shape shape={art.shape} scale={0.8} fill={`url(#${id}-email)`} />
      <Shape
        shape={art.shape}
        scale={0.68}
        fill="none"
        stroke={light}
        strokeOpacity={0.4}
        strokeWidth={1.1}
        strokeLinecap="round"
        strokeDasharray={art.shape === "circle" ? "0.1 2.6" : undefined}
      />
      <g clipPath={`url(#${id}-champ)`}>
        <ellipse cx="32" cy="12" rx="30" ry="16" fill="#ffffff" opacity="0.1" />
      </g>
      <text {...glyph} y={glyphY + 1.2} fill="#000000" opacity={0.45}>
        {art.glyph}
      </text>
      <text {...glyph} y={glyphY} fill={mix(art.tint, "#ffffff", 0.6)}>
        {art.glyph}
      </text>
      {dots(light)}
    </svg>
  );
}
