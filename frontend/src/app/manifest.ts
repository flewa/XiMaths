import type { MetadataRoute } from "next";

import { SITE_DESCRIPTION } from "@/lib/site";

/** Manifeste de la PWA : XiMaths s'installe sur l'écran d'accueil, ce qui ouvre aussi
 * les notifications push sur iPhone et iPad. */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "XiMaths",
    short_name: "XiMaths",
    description: SITE_DESCRIPTION,
    lang: "fr",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#fdfcfc",
    theme_color: "#fdfcfc",
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
      { src: "/icons/icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
