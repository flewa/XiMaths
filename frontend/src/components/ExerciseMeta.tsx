import { unstable_rethrow } from "next/navigation";

/** Difficulté en carrés pleins sur 5 ; `withLabel` l'écrit aussi en toutes lettres. */
export function Difficulty({ value, withLabel = false }: { value: number; withLabel?: boolean }) {
  return (
    <span aria-label={`Difficulté ${value} sur 5`} title={`Difficulté ${value} sur 5`} className="whitespace-nowrap">
      <span aria-hidden="true">
        {"■".repeat(value)}
        <span className="text-stone">{"□".repeat(5 - value)}</span>
        {withLabel && <span className="text-mute"> difficulté {value}/5</span>}
      </span>
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
  return <span className="font-medium text-ink">[{levels.join(" ")}]</span>;
}

/** À appeler dans le catch d'une page : laisse remonter les signaux internes de Next
 * (rendu dynamique, redirection), puis consigne la vraie erreur. */
export function logApiError(error: unknown) {
  unstable_rethrow(error);
  console.error(error);
}

export function ApiUnavailable() {
  return (
    <div role="alert" className="border border-hairline p-4">
      <h1 className="text-base">[x] L&apos;API ne répond pas</h1>
      <p className="mt-2 text-mute">Lance le backend Django sur le port 8000, puis recharge la page.</p>
    </div>
  );
}
