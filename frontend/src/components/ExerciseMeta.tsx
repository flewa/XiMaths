import { unstable_rethrow } from "next/navigation";

/** Difficulté en cinq barres croissantes ; `withLabel` l'écrit aussi en toutes lettres,
 * `short` en chiffres (« 2/5 »). */
export function Difficulty({
  value,
  withLabel = false,
  short = false,
}: {
  value: number;
  withLabel?: boolean;
  short?: boolean;
}) {
  return (
    <span
      role="img"
      aria-label={`Difficulté ${value} sur 5`}
      title={`Difficulté ${value} sur 5`}
      className="inline-flex items-center gap-2 whitespace-nowrap"
    >
      <span aria-hidden="true" className="inline-flex items-end gap-[2px]">
        {[6, 8, 10, 12, 14].map((height, index) => (
          <span
            key={height}
            style={{ height }}
            className={`w-[3px] rounded-[1px] ${index < value ? "bg-ink" : "bg-hairline-strong"}`}
          />
        ))}
      </span>
      {withLabel && <span className="text-mute">difficulté {value}/5</span>}
      {short && !withLabel && <span>{value}/5</span>}
    </span>
  );
}

const LICENSES: Record<string, { label: string; url: string }> = {
  "CC-BY-SA-4.0": { label: "CC BY-SA 4.0", url: "https://creativecommons.org/licenses/by-sa/4.0/deed.fr" },
};

/** Licence d'un contenu, lisible et liée à son texte quand on la connaît. */
export function License({ code }: { code: string }) {
  const license = LICENSES[code];
  if (!license) return <>{code}</>;
  return (
    <a href={license.url} rel="license" className="underline underline-offset-4 hover:text-ink">
      {license.label}
    </a>
  );
}

export function LevelTags({ levels }: { levels: string[] }) {
  return <span className="font-medium text-ink">{levels.join(", ")}</span>;
}

/** À appeler dans le catch d'une page : laisse remonter les signaux internes de Next
 * (rendu dynamique, redirection), puis consigne la vraie erreur. */
export function logApiError(error: unknown) {
  unstable_rethrow(error);
  console.error(error);
}

export function ApiUnavailable() {
  return (
    <div role="alert" className="rounded-xl bg-surface-soft p-5">
      <h1 className="text-2xl">L&apos;API ne répond pas</h1>
      <p className="mt-2 text-mute">Lance le backend Django sur le port 8000, puis recharge la page.</p>
    </div>
  );
}
