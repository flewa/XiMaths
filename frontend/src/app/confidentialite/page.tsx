import type { Metadata } from "next";
import Link from "next/link";

import { AudienceOptOut } from "@/components/Audience";
import { Bullets, ProseSection } from "@/components/Prose";

export const metadata: Metadata = {
  title: "Confidentialité",
  description: "Données collectées par XiMaths, mesure d'audience, finalités, durées de conservation et droits.",
};

export default function PrivacyPage() {
  return (
    <article className="max-w-[720px]">
      <h1>Confidentialité</h1>

      <ProseSection title="Ce que nous collectons">
        <Bullets
          items={[
            "Compte : pseudo, adresse email, mot de passe chiffré, niveau déclaré, préférences.",
            "Contributions : exercices, solutions, relectures, votes, signalements.",
            "Photos de copie, qui sont tes solutions (en libre, en entraînement et au défi du jour) : 3 pages au plus, réencodées à la réception, ce qui efface leurs métadonnées (lieu de la prise, appareil). Elles restent privées, même validées : seuls leurs relecteurs et la modération les voient.",
            "Activité : points, badges, sessions chronométrées (temps, nombre de sorties d'onglet, taille des collages venus d'ailleurs, jamais leur contenu), jours actifs, objectifs et mode vacances.",
            "Questions de compréhension, si l'une t'est posée : la question, ta réponse et l'évaluation.",
            "Connexion Google, si tu l'utilises : ton adresse email et l'identifiant de ton compte Google.",
            "Notifications push, si tu les actives sur un appareil : l'adresse du service de push de ton navigateur et ses clés de chiffrement.",
            "Email académique, si tu en vérifies un : seulement son domaine et une empreinte chiffrée, qui l'empêche de vérifier un second compte. L'adresse elle-même n'est pas conservée.",
          ]}
        />
      </ProseSection>

      <ProseSection title="Pourquoi">
        <Bullets
          items={[
            "Faire fonctionner le service : publication, relecture par les pairs, points et classements.",
            "Protéger la communauté : limites de débit, détection des doublons, comptes liés. Aucune sanction n'est automatique.",
            "T'envoyer les emails que tu as choisis dans les réglages.",
          ]}
        />
        <p>
          Quand il est activé, le modèle Claude d&apos;Anthropic reçoit des énoncés publiés, pour la
          détection des doublons, et, si une question de compréhension t&apos;est posée, ta solution (les
          photos de ta copie) et ta réponse, pour préparer la question et l&apos;évaluation. Ni ton pseudo ni ton adresse
          ne lui sont transmis, et la décision reste toujours humaine.
        </p>
        <p>Pas de publicité, pas de revente de données, pas de traceur tiers.</p>
      </ProseSection>

      <ProseSection title="Mesure d'audience">
        <p>
          Pour savoir combien de personnes utilisent XiMaths et quelles pages servent, nous comptons les visites
          avec Umami, installé sur notre propre serveur : rien ne part chez un tiers, et il ne pose aucun cookie.
          Pour chaque page vue : son adresse (sans les jetons qu&apos;elle peut contenir), le site d&apos;où tu
          viens, l&apos;appareil (type, système, taille d&apos;écran), le navigateur, la langue, et la ville ou le
          pays déduits de ton adresse IP. Celle-ci n&apos;est pas enregistrée : avec ton navigateur, elle sert à
          calculer un identifiant chiffré, renouvelé chaque mois, qui compte les visiteurs sans les reconnaître
          d&apos;un mois à l&apos;autre. Ces mesures ne sont pas reliées à ton compte. Si ton navigateur demande à
          ne pas être suivi (« Do Not Track »), rien n&apos;est compté.
        </p>
        <AudienceOptOut />
      </ProseSection>

      <ProseSection title="Cookies">
        <p>
          Seulement ceux nécessaires au service : la session, la protection contre la falsification de
          requêtes (CSRF) et ton choix de thème. La mesure d&apos;audience n&apos;en pose pas. Aucun ne demande ton consentement, et il n&apos;y a pas
          de bandeau.
        </p>
      </ProseSection>

      <ProseSection title="Combien de temps">
        <Bullets
          items={[
            "Compte et activité : tant que le compte existe.",
            "Notifications : 6 mois.",
            "Photos de copie jamais jointes à une solution : effacées au bout d'un jour.",
            "Abonnements push : jusqu'à ce que tu les désactives, ou que ton navigateur les révoque.",
            "Décisions de modération pour plagiat : effacées au plus tard 1 an après la décision.",
            "Questions de compréhension : tant que le compte existe ; elles sont effacées avec lui.",
            "Mesure d'audience : 25 mois, puis effacée.",
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
