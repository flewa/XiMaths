import type { Metadata } from "next";
import Link from "next/link";

import { Bullets, DraftNotice, ProseSection } from "@/components/Prose";

export const metadata: Metadata = {
  title: "Confidentialité",
  description: "Données collectées par XiMaths, finalités, durées de conservation et droits.",
};

export default function PrivacyPage() {
  return (
    <article className="max-w-[720px]">
      <h1>Confidentialité</h1>
      <DraftNotice />

      <ProseSection title="Ce que nous collectons">
        <Bullets
          items={[
            "Compte : pseudo, adresse email, mot de passe chiffré, niveau déclaré, tiers-temps si tu le déclares, préférences.",
            "Contributions : exercices, solutions, relectures, votes, signalements.",
            "Activité : points, badges, sessions chronométrées (temps, nombre de sorties d'onglet, taille des collages venus d'ailleurs, jamais leur contenu), jours actifs, objectifs et mode vacances.",
            "Questions de compréhension, si l'une t'est posée : la question, ta réponse et l'évaluation.",
            "Connexion Google, si tu l'utilises : ton adresse email et l'identifiant de ton compte Google.",
            "Email académique, si tu en vérifies un : seulement son domaine et une empreinte chiffrée, qui l'empêche de vérifier un second compte. L'adresse elle-même n'est pas conservée.",
          ]}
        />
      </ProseSection>

      <ProseSection title="Pourquoi">
        <Bullets
          items={[
            "Faire fonctionner le service : publication, relecture par les pairs, points et classements.",
            "Protéger la communauté : limites de débit, détection des doublons et du plagiat, comptes liés. Aucune sanction n'est automatique.",
            "T'envoyer les emails que tu as choisis dans les réglages.",
          ]}
        />
        <p>
          Quand il est activé, le modèle Claude d&apos;Anthropic reçoit des énoncés publiés, pour la
          détection des doublons, et, si une question de compréhension t&apos;est posée, ta solution et
          ta réponse, pour préparer la question et l&apos;évaluation. Ni ton pseudo ni ton adresse ne
          lui sont transmis, et la décision reste toujours humaine.
        </p>
        <p>Pas de publicité, pas de revente de données, pas de traceur tiers.</p>
      </ProseSection>

      <ProseSection title="Cookies">
        <p>
          Seulement ceux nécessaires au service : la session, la protection contre la falsification de
          requêtes (CSRF) et ton choix de thème. Aucun ne demande ton consentement, et il n&apos;y a pas
          de bandeau.
        </p>
      </ProseSection>

      <ProseSection title="Combien de temps">
        <Bullets
          items={[
            "Compte et activité : tant que le compte existe.",
            "Notifications : 6 mois.",
            "Signaux d'intégrité (plagiat, collages) : jusqu'à la décision de modération, puis effacés au plus tard après 1 an.",
            "Questions de compréhension : tant que le compte existe ; elles sont effacées avec lui.",
          ]}
        />
      </ProseSection>

      <ProseSection title="Tes droits">
        <p>
          Depuis les{" "}
          <Link href="/reglages" className="underline underline-offset-4">
            réglages
          </Link>
          , tu peux télécharger toutes tes données et supprimer ton compte. La suppression efface tes
          données personnelles ; tes contributions restent publiées sans ton pseudo, conformément à leur
          licence. Tu peux aussi saisir la CNIL.
        </p>
      </ProseSection>
    </article>
  );
}
