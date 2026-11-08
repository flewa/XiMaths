import { BADGE_ART, type BadgeShape, FALLBACK_ART } from "@/lib/profile-art";

const HEXAGON = (radius: number) =>
  Array.from({ length: 6 }, (_, index) => {
    const angle = (Math.PI / 3) * index - Math.PI / 2;
    return `${(32 + radius * Math.cos(angle)).toFixed(2)},${(32 + radius * Math.sin(angle)).toFixed(2)}`;
  }).join(" ");

const SHIELD = "M32 3 L57 11.5 V30 C57 45 46.5 55.5 32 61 C17.5 55.5 7 45 7 30 V11.5 Z";

function Shape({ shape, inset, ...props }: { shape: BadgeShape; inset: boolean } & React.SVGProps<SVGElement>) {
  if (shape === "circle") return <circle cx="32" cy="32" r={inset ? 23.5 : 30} {...(props as React.SVGProps<SVGCircleElement>)} />;
  if (shape === "hexagon") return <polygon points={HEXAGON(inset ? 24 : 30.5)} {...(props as React.SVGProps<SVGPolygonElement>)} />;
  return (
    <path
      d={SHIELD}
      transform={inset ? "translate(32 32) scale(0.78) translate(-32 -32)" : undefined}
      {...(props as React.SVGProps<SVGPathElement>)}
    />
  );
}

/** Médaille d'un badge : un émail sombre cerclé de sa couleur, et son symbole mathématique.
 * Pas encore obtenu (`locked`), elle reste en gris. Décorative si `label` manque. */
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
  const art = BADGE_ART[slug] ?? FALLBACK_ART;
  const rim = locked ? "var(--hairline-strong)" : art.tint;
  const glyph = locked ? "var(--stone)" : art.tint;
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      className="shrink-0"
    >
      <Shape shape={art.shape} inset={false} fill={rim} />
      <Shape shape={art.shape} inset fill={locked ? "var(--surface-card)" : "#1b1b1b"} />
      {!locked && (
        <Shape shape={art.shape} inset fill="none" stroke={art.tint} strokeOpacity={0.35} strokeWidth={1} />
      )}
      <text
        x="32"
        y="33"
        textAnchor="middle"
        dominantBaseline="central"
        fill={glyph}
        fontFamily="KaTeX_Main, 'Latin Modern Roman', Georgia, serif"
        fontSize={art.glyph.length > 1 ? 18 : 26}
      >
        {art.glyph}
      </text>
    </svg>
  );
}
