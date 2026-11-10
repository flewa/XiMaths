import type { Metadata } from "next";
import QRCode from "qrcode";

import { SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Affiche à imprimer",
  description: "Une affiche A4 avec QR code pour faire connaître XiMaths en BU, en salle de prépa ou au CDI.",
  robots: { index: false },
};

// L'adresse du QR code porte sa source : la mesure d'audience compte les visites venues d'une affiche.
const TARGET = `${SITE_URL}/?utm_source=affiche`;
const DOMAIN = new URL(SITE_URL).host;
const STRIPS = 8;

const POINTS = [
  ["Choisis un exercice", "de la L1 au master, et dans toutes les prépas : MPSI à PT, BCPST, ECG, B/L."],
  ["Rédige à la main, envoie la photo", "de ta copie, depuis ton téléphone."],
  ["Trois étudiants la relisent", "tirés au sort parmi ceux de ton niveau, et te disent ce qui manque."],
];

/** Affiche A4 à imprimer : le QR code mène au site, les languettes se détachent avec l'adresse. */
export default async function PosterPage() {
  const qr = await QRCode.toString(TARGET, { type: "svg", margin: 0, errorCorrectionLevel: "M", color: { dark: "#191919", light: "#ffffff" } });
  return (
    <div className="max-w-[720px]">
      <div className="affiche-consignes">
        <h1>Affiche à imprimer</h1>
        <p className="mt-2 text-body">
          Imprime cette page en A4 (Ctrl + P, ou Partager puis Imprimer sur téléphone), avec les marges à zéro et sans
          en-têtes. Le QR code mène au site, et chaque languette du bas porte l&apos;adresse : on en détache une en passant.
        </p>
        <p className="mt-2 text-sm text-mute">
          Demande l&apos;accord avant d&apos;afficher : bibliothèque universitaire, salle de travail de la prépa, CDI, panneau
          du bureau des étudiants.
        </p>
      </div>

      <article className="affiche mt-8" aria-label="Aperçu de l'affiche">
        <div className="affiche-corps">
          <p className="affiche-marque">
            <span className="affiche-xi" aria-hidden="true">
              ξ
            </span>
            XiMaths
          </p>
          <h2 className="affiche-titre">Ta copie de maths, corrigée par trois étudiants.</h2>
          <p className="affiche-sous-titre">Des exercices de maths du supérieur, gratuits et sans publicité.</p>
          <ol className="affiche-points">
            {POINTS.map(([strong, rest]) => (
              <li key={strong}>
                <strong>{strong}</strong> {rest}
              </li>
            ))}
          </ol>
          <p className="affiche-defi">Et chaque jour, un défi de 30 minutes pour ton année d&apos;études.</p>
          <div className="affiche-qr-ligne">
            <div className="affiche-qr" dangerouslySetInnerHTML={{ __html: qr }} />
            <p className="affiche-adresse">
              Scanne, ou tape
              <span>{DOMAIN}</span>
            </p>
          </div>
        </div>
        <ul className="affiche-languettes" aria-label="Languettes à détacher">
          {Array.from({ length: STRIPS }, (_, index) => (
            <li key={index}>
              <span className="affiche-languette-texte">
                <span>{DOMAIN}</span>
                <span className="affiche-languette-sous">copies corrigées</span>
              </span>
            </li>
          ))}
        </ul>
      </article>
    </div>
  );
}
