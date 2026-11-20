import { Icon } from "./Icon";

// Au-delà, une rangée d'étiquettes repousse la liste d'exercices de plusieurs écrans sur téléphone.
const PHONE_LIMIT = 8;

/** Une rangée d'étiquettes-liens précédée de son libellé (« Par notion : »). Sur téléphone, une
 * rangée longue se replie derrière un bouton qui donne leur nombre ; sur grand écran, elle reste
 * ouverte. Les deux versions coexistent dans la page, une seule est affichée. */
export function ChipRow({
  label,
  count,
  className = "mt-4",
  children,
}: {
  label: string;
  count: number;
  className?: string;
  children: React.ReactNode;
}) {
  if (count === 0) return null;
  const row = (
    <p className="flex flex-wrap items-center gap-2 text-sm">
      <span className="mr-1 text-mute">{label} :</span>
      {children}
    </p>
  );
  if (count <= PHONE_LIMIT) return <div className={className}>{row}</div>;
  return (
    <div className={className}>
      <div className="max-sm:hidden">{row}</div>
      <details className="plain group sm:hidden">
        <summary className="inline-flex min-h-10 cursor-pointer list-none items-center gap-1.5 rounded-full border border-hairline px-3.5 text-sm text-body [&::-webkit-details-marker]:hidden">
          {label} ({count})
          <Icon name="chevron" size={14} className="transition-transform group-open:rotate-180" />
        </summary>
        <p className="mt-3 flex flex-wrap gap-2 text-sm">{children}</p>
      </details>
    </div>
  );
}

/** Classe d'une étiquette-lien de ces rangées. */
export const chipLinkClass =
  "inline-flex min-h-8 items-center rounded-full bg-surface-card px-3 text-ink hover:bg-surface-dark-elevated";
