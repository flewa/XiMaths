import { Icon } from "./Icon";

/** Recherche d'exercices : un formulaire simple vers le catalogue (/exercices?q=…), sans script. */
export function SearchBox({
  id,
  defaultValue = "",
  className = "",
}: {
  id: string;
  defaultValue?: string;
  className?: string;
}) {
  return (
    <form
      action="/exercices"
      role="search"
      className={`flex h-10 items-center gap-2.5 rounded-[10px] border border-hairline bg-surface-soft px-3.5 text-mute focus-within:border-accent ${className}`}
    >
      <Icon name="search" size={16} />
      <label htmlFor={id} className="sr-only">
        Chercher un exercice
      </label>
      <input
        id={id}
        name="q"
        type="search"
        defaultValue={defaultValue}
        placeholder="Chercher un exercice, une notion…"
        className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-mute"
      />
    </form>
  );
}
