import type { Metadata } from "next";
import Link from "next/link";

import { primaryButtonClass, secondaryButtonClass } from "@/components/Form";

export const metadata: Metadata = { title: "Page introuvable", robots: { index: false } };

/** Adresse inconnue : on dit ce qui se passe, et on propose où aller. */
export default function NotFound() {
  return (
    <div className="max-w-[60ch]">
      <p className="text-sm text-mute">Erreur 404</p>
      <h1 className="mt-1">Cette page n&apos;existe pas.</h1>
      <p className="mt-3 text-body">
        L&apos;adresse est peut-être mal écrite, ou la page a été retirée. Les exercices, eux, sont toujours là.
      </p>
      <p className="mt-6 flex flex-wrap gap-3">
        <Link href="/exercices" className={primaryButtonClass}>
          Parcourir les exercices
        </Link>
        <Link href="/" className={secondaryButtonClass}>
          Retour à l&apos;accueil
        </Link>
      </p>
    </div>
  );
}
