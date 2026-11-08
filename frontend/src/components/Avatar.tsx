import type { Avatar as AvatarData } from "@/lib/api";
import { AVATAR_TINTS } from "@/lib/profile-art";

/** Avatar d'un membre : une tuile de sa couleur, avec son symbole ou son initiale.
 * Décoratif par défaut (le pseudo est écrit à côté) ; `label` le fait lire.
 * La taille vaut `size` pixels, sauf si `className` fixe `--avatar` (par exemple `max-sm:[--avatar:48px]`). */
export function Avatar({
  avatar,
  size = 32,
  label,
  className = "",
}: {
  avatar: AvatarData;
  size?: number;
  label?: string;
  className?: string;
}) {
  const tint = AVATAR_TINTS[avatar.color] ?? AVATAR_TINTS.sable;
  const side = `var(--avatar, ${size}px)`;
  return (
    <span
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      className={`inline-grid shrink-0 select-none place-items-center font-serif leading-none ${className}`}
      style={{
        width: side,
        height: side,
        borderRadius: `calc(${side} * 0.3)`,
        background: tint,
        color: "#1c1c1c",
        fontSize: `calc(${side} * ${avatar.custom_symbol ? 0.58 : 0.5})`,
      }}
    >
      {avatar.symbol}
    </span>
  );
}
