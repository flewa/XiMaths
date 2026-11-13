import type { MetadataRoute } from "next";

import { fetchSitemap } from "@/lib/api";
import { chapterPath, levelPath } from "@/lib/seo-pages";
import { SITE_URL } from "@/lib/site";

// Construit à chaque lecture, pas une fois pour toutes au moment du build : l'API n'est pas
// joignable pendant le build, et le plan resterait réduit aux pages fixes pendant une heure
// après chaque mise à jour. Les robots le lisent quelques fois par jour : trois requêtes légères.
export const dynamic = "force-dynamic";

const PAGES = ["", "/exercices", "/chapitres", "/defi", "/classements", "/badges", "/cgu", "/confidentialite", "/mentions-legales"];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages: MetadataRoute.Sitemap = PAGES.map((path) => ({ url: `${SITE_URL}${path}` }));
  try {
    const { exercises, levels, topics, courseNotes } = await fetchSitemap();
    return [
      ...pages,
      // Les pages d'entrée : ce que cherchent les élèves (« exercices MPSI », « exercices de probabilités »).
      ...levels.map((level) => ({ url: `${SITE_URL}${levelPath(level.code)}` })),
      // Chapitres et notions ; une notion encore vide n'a rien à montrer.
      ...topics
        .filter((topic) => topic.exercises > 0)
        .map((topic) => ({ url: `${SITE_URL}${chapterPath(topic.slug)}` })),
      // Rappels de cours publiés par l'équipe ; aucun tant qu'ils sont en relecture.
      ...(courseNotes.length > 0 ? [{ url: `${SITE_URL}/rappels` }] : []),
      ...courseNotes.map((note) => ({ url: `${SITE_URL}/rappels/${note.slug}`, lastModified: note.updated_at })),
      ...exercises.map((exercise) => ({
        url: `${SITE_URL}/exercices/${exercise.id}`,
        lastModified: exercise.updated_at,
      })),
    ];
  } catch (error) {
    // API injoignable : les pages fixes seules, le plan complet à la lecture suivante.
    console.error(error);
    return pages;
  }
}
