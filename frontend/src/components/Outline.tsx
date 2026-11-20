import { Icon } from "./Icon";
import { MathText } from "./MathText";

// En deçà, la page se parcourt d'un coup d'œil.
const MIN_PARTS = 4;

/** Sommaire replié d'un texte long : un lien par partie. Sur téléphone, une fiche fait jusqu'à
 * sept écrans ; on y saute droit à la partie cherchée. */
export function Outline({ items }: { items: { id: string; title: string }[] }) {
  if (items.length < MIN_PARTS) return null;
  return (
    <nav aria-label="Sommaire" className="mt-6">
      <details className="plain group rounded-xl border border-hairline">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 px-4 text-sm font-medium [&::-webkit-details-marker]:hidden">
          Sommaire · {items.length} parties
          <Icon name="chevron" size={16} className="text-mute transition-transform group-open:rotate-180" />
        </summary>
        <ol className="space-y-0.5 border-t border-hairline px-2 py-2 text-sm">
          {items.map((item, index) => (
            <li key={item.id}>
              <a
                href={`#${item.id}`}
                className="flex min-h-10 items-baseline gap-3 rounded-lg px-2 py-2 text-body hover:bg-hover hover:text-ink"
              >
                <span className="w-5 shrink-0 text-right text-mute tabular-nums">{index + 1}</span>
                <MathText>{item.title}</MathText>
              </a>
            </li>
          ))}
        </ol>
      </details>
    </nav>
  );
}
