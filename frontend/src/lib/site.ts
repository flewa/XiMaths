// Réglages du site partagés par le serveur et le navigateur.

/** Adresse publique du site, pour les liens absolus (SEO, partage). */
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const SITE_DESCRIPTION =
  "Exercices de mathématiques du supérieur, de la licence au master et en prépa, résolus et relus par la communauté.";

export type Theme = "system" | "light" | "dark";
export const THEME_COOKIE = "theme";
/** Image de partage (app/opengraph-image.png), à redonner aux pages qui définissent leur
 * propre openGraph : celui-ci remplace celui de la mise en page, image comprise. */
export const SHARE_IMAGE = {
  url: "/opengraph-image.png",
  width: 1200,
  height: 630,
  alt: "XiMaths : des maths du supérieur, résolues et relues par la communauté.",
};

/** Comptes officiels de XiMaths : déclarés aux moteurs (sameAs) et liés en pied de page.
 * Ils aident Google à rattacher le nom « XiMaths » au site. */
export const SOCIAL_PROFILES = [{ label: "YouTube", url: "https://www.youtube.com/@Ximathsfr" }];

/** Sans choix dans les réglages, le site est sombre. */
export const DEFAULT_THEME: Theme = "dark";
