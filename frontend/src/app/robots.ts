import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

// Pages personnelles ou de travail : rien à indexer.
const PRIVATE = [
  "/api/",
  "/arbitrages",
  "/decisions",
  "/desabonnement",
  "/entrainement",
  "/mot-de-passe",
  "/notifications",
  "/progression",
  "/questions",
  "/reglages",
  "/relectures",
  "/signalements",
  "/verifier-email",
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: PRIVATE },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
