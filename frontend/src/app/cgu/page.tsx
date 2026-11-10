import type { Metadata } from "next";
import Link from "next/link";

import { Bullets, ProseSection } from "@/components/Prose";

export const metadata: Metadata = {
  title: "Conditions d'utilisation",
  description: "Règles de publication, licence des contenus, modération et recours sur XiMaths.",
};

export default function TermsPage() {
  return (
    <article className="max-w-[720px]">
      <h1>Conditions d&apos;utilisation</h1>

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
          Les exercices sont publiés sous licence{" "}
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
          Tes solutions et tes relectures ne sont pas publiées. Une copie n&apos;est vue que de son auteur, de
          ses relecteurs tirés au sort et de la modération ; un commentaire de relecture, de l&apos;auteur de la
          copie et de la modération. Le site affiche seulement le nombre de solutions envoyées.
        </p>
        <p>
          Une exception, la copie modèle : si tu donnes ton accord (une case, à l&apos;envoi ou plus tard) et que
          l&apos;équipe choisit ta copie validée, elle est montrée sans ton pseudo aux membres qui ont déjà envoyé
          leur copie sur cet exercice. Tu peux retirer ton accord à tout moment ; elle n&apos;est alors plus montrée.
          Après avoir ouvert une copie modèle, tu peux encore envoyer une copie sur cet exercice, mais elle ne
          rapporte plus de points.
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
            "Sous chaque exercice, un fil public de questions et de remarques, signé de ton pseudo : on y demande une précision, on y signale une coquille, on y discute d'une méthode. On n'y donne pas la solution. L'équipe retire les messages qui n'y ont pas leur place ; leur auteur en reçoit le motif et peut faire appel.",
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
            "Tout membre peut signaler un contenu, y compris un message sous un exercice. Un modérateur humain tranche, jamais un algorithme seul.",
            "Chaque retrait ou sanction est motivé : tu reçois le motif et les contenus concernés.",
            "Échelle des sanctions : avertissement et annulation des points concernés, exclusion des classements pendant 30 jours, suspension de 7 jours, bannissement.",
            "Tu peux faire appel sous 14 jours. Un autre modérateur examine l'appel et répond sous 7 jours.",
            "Un modérateur ne tranche jamais ce qui le concerne : son propre contenu, ou l'appel d'une décision qu'il a prise.",
            "Chaque décision est inscrite dans un journal que toute l'équipe de modération peut relire.",
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
