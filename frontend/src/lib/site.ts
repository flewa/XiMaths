// Réglages du site partagés par le serveur et le navigateur.

/** Adresse publique du site, pour les liens absolus (SEO, partage). */
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const SITE_DESCRIPTION =
  "Exercices de mathématiques du supérieur, de la licence au master et en prépa, résolus et relus par la communauté.";

export type Theme = "system" | "light" | "dark";
export const THEME_COOKIE = "theme";
