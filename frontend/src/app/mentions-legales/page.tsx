import type { Metadata } from "next";
import Link from "next/link";

import { ProseSection } from "@/components/Prose";
import { CONTACT_EMAIL, HOST, PUBLISHER_NAME } from "@/lib/legal";

export const metadata: Metadata = {
  title: "Mentions légales",
  description: "Éditeur, hébergeur et contact de XiMaths, et comment signaler un contenu.",
};

const link = "underline underline-offset-4";

export default function LegalNoticePage() {
  return (
    <article className="max-w-[720px]">
      <h1>Mentions légales</h1>

      <ProseSection title="Éditeur">
        {PUBLISHER_NAME ? (
          <p>
            XiMaths est édité par {PUBLISHER_NAME}, à titre personnel et non professionnel. {PUBLISHER_NAME} est
            aussi le directeur de la publication.
          </p>
        ) : (
          <p>
            XiMaths est édité par un particulier, à titre non professionnel. Comme la loi pour la confiance dans
            l&apos;économie numérique le permet dans ce cas, son identité est tenue à la disposition de
            l&apos;hébergeur, indiqué ci-dessous.
          </p>
        )}
      </ProseSection>

      <ProseSection title="Contact">
        <p>
          Pour toute question, une erreur à signaler ou une demande sur tes données :{" "}
          <a href={`mailto:${CONTACT_EMAIL}`} className={link}>
            {CONTACT_EMAIL}
          </a>
          .
        </p>
      </ProseSection>

      <ProseSection title="Hébergeur">
        <p>
          {HOST.name}, {HOST.address}. Téléphone : {HOST.phone}.{" "}
          <a href={HOST.url} rel="noopener" className={link}>
            ovhcloud.com
          </a>
        </p>
      </ProseSection>

      <ProseSection title="Contenus">
        <p>
          Les exercices et les rappels de cours sont publiés sous licence Creative Commons BY-SA 4.0 : tu peux les
          réutiliser et les adapter, en citant leur auteur et en gardant la même licence. Les copies envoyées en
          relecture restent privées, sauf la copie modèle d&apos;un exercice, montrée sans nom avec l&apos;accord
          de son auteur. Le détail est dans les{" "}
          <Link href="/cgu" className={link}>
            conditions d&apos;utilisation
          </Link>
          .
        </p>
      </ProseSection>

      <ProseSection title="Signaler un contenu">
        <p>
          Sous chaque exercice, le bouton « Signaler » prévient la modération : erreur, plagiat, contenu
          inapproprié. Tu peux aussi écrire à{" "}
          <a href={`mailto:${CONTACT_EMAIL}`} className={link}>
            {CONTACT_EMAIL}
          </a>{" "}
          en indiquant l&apos;adresse de la page et ce qui pose problème. Un humain examine chaque signalement.
        </p>
      </ProseSection>

      <ProseSection title="Données personnelles">
        <p>
          Ce que le site collecte, pourquoi, combien de temps, et tes droits :{" "}
          <Link href="/confidentialite" className={link}>
            page Confidentialité
          </Link>
          .
        </p>
      </ProseSection>
    </article>
  );
}
