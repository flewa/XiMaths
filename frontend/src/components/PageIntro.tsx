import { cookies } from "next/headers";

import { SEEN_COOKIE } from "@/lib/site";

import { MarkSeen } from "./MarkSeen";

/** Le paragraphe qui explique une page : en entier à la première visite, puis replié sous
 * « Comment ça marche ? », pour aller droit au contenu. La page vue est retenue dans un
 * cookie, lu par le serveur : la page arrive déjà dans le bon état, sans saut. */
export async function PageIntro({ id, children }: { id: string; children: React.ReactNode }) {
  const seen = ((await cookies()).get(SEEN_COOKIE)?.value ?? "").split(".").includes(id);
  if (!seen) {
    return (
      <>
        <p className="mt-2 max-w-[70ch] text-body">{children}</p>
        <MarkSeen id={id} />
      </>
    );
  }
  return (
    <details className="mt-1">
      <summary className="inline-flex min-h-8 items-center text-sm text-mute hover:text-ink">Comment ça marche ?</summary>
      <p className="mt-1 max-w-[70ch] text-body">{children}</p>
    </details>
  );
}
