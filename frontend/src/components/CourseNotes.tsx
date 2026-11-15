"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiPost } from "@/lib/client-api";

import { FormMessage, primaryButtonClass, secondaryButtonClass } from "./Form";

/** Relecture d'une fiche (ou d'une démonstration) par l'équipe : la publier une fois relue,
 * ou la retirer. */
export function CourseNoteReview({
  slug,
  published,
  noun = "fiche",
}: {
  slug: string;
  published: boolean;
  noun?: "fiche" | "démonstration";
}) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggle() {
    setBusy(true);
    setError(null);
    const result = await apiPost(`/course-notes/${encodeURIComponent(slug)}/${published ? "unpublish" : "publish"}`);
    setBusy(false);
    if (!result.ok) setError(result.error);
    else router.refresh();
  }

  return (
    <section
      aria-label={`Relecture de la ${noun}`}
      className="mt-6 space-y-3 rounded-xl border border-hairline bg-surface-soft p-4 text-sm"
    >
      <p className="text-body">
        {published ? (
          <>
            <strong className="font-medium text-ink">Publiée</strong> : visible de tous, et proposée sur la page de sa
            notion.
          </>
        ) : (
          <>
            <strong className="font-medium text-ink">Brouillon</strong> : visible de l&apos;équipe seulement. Relis-la en
            entier, formules et hypothèses comprises, avant de la publier.
          </>
        )}
      </p>
      <button
        type="button"
        onClick={toggle}
        disabled={busy}
        className={published ? secondaryButtonClass : primaryButtonClass}
      >
        {published ? "Repasser en brouillon" : `Publier cette ${noun}`}
      </button>
      <FormMessage error={error} />
    </section>
  );
}
