import { unstable_rethrow } from "next/navigation";

export function Difficulty({ value }: { value: number }) {
  return (
    <span aria-label={`Difficulté ${value} sur 5`} title={`Difficulté ${value} sur 5`}>
      <span aria-hidden="true">
        {"■".repeat(value)}
        <span className="text-ash">{"□".repeat(5 - value)}</span>
      </span>
    </span>
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
