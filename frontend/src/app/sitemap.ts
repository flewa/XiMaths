import type { MetadataRoute } from "next";

import { fetchSitemap } from "@/lib/api";
import { chapterPath, levelPath } from "@/lib/seo-pages";
import { SITE_URL } from "@/lib/site";

export const revalidate = 3600;

const PAGES = ["", "/exercices", "/defi", "/classements", "/badges", "/cgu", "/confidentialite"];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const pages: MetadataRoute.Sitemap = PAGES.map((path) => ({ url: `${SITE_URL}${path}` }));
  try {
    const { exercises, levels, topics } = await fetchSitemap();
    return [
      ...pages,
      // Les pages d'entrée : ce que cherchent les élèves (« exercices MPSI », « exercices de probabilités »).
      ...levels.map((level) => ({ url: `${SITE_URL}${levelPath(level.code)}` })),
      ...topics.map((topic) => ({ url: `${SITE_URL}${chapterPath(topic.slug)}` })),
      ...exercises.map((exercise) => ({
        url: `${SITE_URL}/exercices/${exercise.id}`,
        lastModified: exercise.updated_at,
      })),
    ];
  } catch (error) {
    // API injoignable (pendant la construction, par exemple) : les pages fixes seules,
    // jusqu'à la prochaine régénération.
    console.error(error);
    return pages;
  }
}
