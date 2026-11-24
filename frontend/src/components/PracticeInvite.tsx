import Link from "next/link";

import { plural } from "@/lib/labels";
import { chapterPath, ofChapter } from "@/lib/seo-pages";

import { primaryButtonClass } from "./Form";

/** « 12 exercices d'algèbre linéaire », ou « exercices d'algèbre linéaire » sans décompte. */
export function practiceLabel(topicName: string, exercises: number) {
  return `${exercises > 0 ? plural(exercises, "exercice") : "exercices"} ${ofChapter(topicName)}`;
}

/** En bas d'une fiche, pour un visiteur : il arrive souvent d'un moteur de recherche pour réviser.
 * On lui dit ce qu'il trouve ici en plus du cours, et le compte le ramène aux exercices du chapitre.
 * Rien quand le chapitre n'a pas encore d'exercice. */
export function PracticeInvite({
  topic,
  topicName,
  exercises,
  slug,
}: {
  topic: string;
  topicName: string;
  exercises: number;
  /** La fiche d'où vient le visiteur, pour la mesure d'audience. */
  slug: string;
}) {
  if (exercises === 0) return null;
  const href = chapterPath(topic);
  return (
    <section
      aria-labelledby="entrainement"
      className="print-hidden mt-10 rounded-2xl border border-hairline bg-surface-soft px-5 py-5"
    >
      <h2 id="entrainement" className="text-lg font-semibold text-ink">
        Entraîne-toi : {practiceLabel(topicName, exercises)}
      </h2>
      <p className="mt-2 text-body">
        Tu cherches à la main, tu envoies une photo de ta copie : trois autres étudiants la relisent et te
        disent ce qui est juste.
      </p>
      <p className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2">
        <Link
          href={`/inscription?suivant=${encodeURIComponent(href)}`}
          className={primaryButtonClass}
          data-umami-event="fiche-inscription"
          data-umami-event-fiche={slug}
        >
          Créer un compte
        </Link>
        <Link
          href={href}
          className="inline-flex min-h-8 items-center text-sm text-body underline underline-offset-4 hover:text-ink"
        >
          Voir les exercices
        </Link>
      </p>
      <p className="mt-3 text-xs text-mute">Gratuit et sans publicité.</p>
    </section>
  );
}
