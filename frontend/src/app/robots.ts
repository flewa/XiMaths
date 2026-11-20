import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

// Pages personnelles ou de travail : rien à indexer.
const PRIVATE = [
  "/api/",
  "/evaluations",
  "/decisions",
  "/desabonnement",
  "/entrainement",
  "/exercices/nouveau",
  "/mot-de-passe",
  "/notifications",
  "/photos/",
  "/progression",
  "/questions",
  "/reglages",
  "/relectures",
  "/signalements",
  "/verifier-email",
];

// Variantes sans valeur pour un moteur : chaque niveau × chaque semaine des classements, et les
// résultats de recherche. Google en explorait des centaines sans les indexer, au lieu des
// exercices. La page /classements elle-même reste explorée.
const VARIANTS = ["/classements?", "/exercices?q=", "/exercices?*&q="];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: [...PRIVATE, ...VARIANTS] },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
