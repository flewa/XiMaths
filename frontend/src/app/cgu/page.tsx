import type { Metadata } from "next";
import Link from "next/link";

import { Bullets, DraftNotice, ProseSection } from "@/components/Prose";

export const metadata: Metadata = {
  title: "Conditions d'utilisation",
  description: "Règles de publication, licence des contenus, modération et recours sur XiMaths.",
};

export default function TermsPage() {
  return (
    <article className="max-w-[720px]">
      <h1>Conditions d&apos;utilisation</h1>
      <DraftNotice />

      <ProseSection title="Ce qu'est XiMaths">
        <p>
          Une plateforme gratuite d&apos;exercices de mathématiques du supérieur. Les membres publient
          des exercices, proposent des solutions et relisent celles des autres.
        </p>
      </ProseSection>

      <ProseSection title="Ton compte">
        <Bullets
          items={[
            "Un compte par personne, avec une adresse email vérifiée.",
            "Ton pseudo est public ; ton adresse email ne l'est jamais.",
            "Tu peux exporter tes données ou supprimer ton compte à tout moment, depuis les réglages.",
          ]}
        />
      </ProseSection>

      <ProseSection title="Licence de tes contributions">
        <p>
          Exercices, solutions et relectures sont publiés sous licence{" "}
          <a
            href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr"
            rel="license"
            className="underline underline-offset-4"
          >
            Creative Commons BY-SA 4.0
          </a>
          , avec ton pseudo comme attribution. Chacun peut les réutiliser, y compris commercialement,
          à condition de te citer et de partager ses modifications sous la même licence. Si tu supprimes
          ton compte, tes contributions restent publiées sans ton pseudo.
        </p>
        <p>
          La licence autorise aussi la réutilisation pour entraîner des modèles d&apos;IA, dans le
          respect de ses conditions. XiMaths ne vend pas les contenus à des tiers.
        </p>
      </ProseSection>

      <ProseSection title="Ce que tu publies">
        <Bullets
          items={[
            "Reformule avec tes mots un énoncé publié ailleurs, et indique la source : la formulation d'un livre ou d'un sujet est protégée.",
            "Ne recopie pas la solution d'un autre, ni un corrigé publié ailleurs.",
            "Déclare l'usage d'une IA. Une solution générée est permise, mais étiquetée et sans points.",
            "Pas de contenu injurieux, hors sujet ou illicite.",
          ]}
        />
      </ProseSection>

      <ProseSection title="Points, classements et badges">
        <p>
          Ils récompensent les contributions relues par d&apos;autres. Ils n&apos;ont aucune valeur
          monétaire, et un point obtenu par fraude est annulé.
        </p>
      </ProseSection>

      <ProseSection title="Modération et recours">
        <Bullets
          items={[
            "Tout membre peut signaler un contenu. Un modérateur humain tranche, jamais un algorithme seul.",
            "Chaque retrait ou sanction est motivé : tu reçois le motif et les contenus concernés.",
            "Échelle des sanctions : avertissement et annulation des points concernés, exclusion des classements pendant 30 jours, suspension de 7 jours, bannissement.",
            "Tu peux faire appel sous 14 jours. Un autre modérateur examine l'appel et répond sous 7 jours.",
            "Aucune accusation n'est jamais rendue publique.",
          ]}
        />
        <p>
          Tes décisions et tes appels sont sur la page{" "}
          <Link href="/decisions" className="underline underline-offset-4">
            Mes décisions
          </Link>
          .
        </p>
      </ProseSection>
    </article>
  );
}
