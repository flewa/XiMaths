import type { Metadata, Viewport } from "next";
import { JetBrains_Mono } from "next/font/google";
import { cookies } from "next/headers";
import Link from "next/link";
import "katex/dist/katex.min.css";

import { SiteHeader } from "@/components/SiteHeader";
import { SITE_DESCRIPTION, SITE_URL, THEME_COOKIE, type Theme } from "@/lib/site";

import "./globals.css";

// Substitut libre de Berkeley Mono recommandé par le document de design.
const mono = JetBrains_Mono({
  variable: "--font-mono-face",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "XiMaths", template: "%s · XiMaths" },
  description: SITE_DESCRIPTION,
  openGraph: { siteName: "XiMaths", locale: "fr_FR", type: "website", description: SITE_DESCRIPTION },
  twitter: { card: "summary" },
  // Installée sur l'écran d'accueil d'un iPhone, la PWA s'ouvre sans la barre de Safari.
  appleWebApp: { capable: true, title: "XiMaths", statusBarStyle: "default" },
};

export const viewport: Viewport = {
  // Le contenu va jusqu'aux bords arrondis de l'écran ; la barre du bas réserve la zone du geste d'accueil.
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fdfcfc" },
    { media: "(prefers-color-scheme: dark)", color: "#161313" },
  ],
};

const FOOTER_LINKS = [
  { href: "/exercices", label: "Parcourir" },
  { href: "/classements", label: "Classements" },
  { href: "/badges", label: "Badges" },
  { href: "/cgu", label: "Conditions" },
  { href: "/confidentialite", label: "Confidentialité" },
];

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Thème choisi dans les réglages ; sans choix, celui du système.
  const theme = (await cookies()).get(THEME_COOKIE)?.value as Theme | undefined;
  return (
    <html lang="fr" data-theme={theme === "light" || theme === "dark" ? theme : undefined}>
      {/* Sous 1024 px, la barre d'onglets du bas recouvrirait la fin de la page : on lui fait de la place. */}
      <body className={`${mono.variable} pb-[calc(3.5rem+env(safe-area-inset-bottom))] font-mono antialiased lg:pb-0`}>
        <a
          href="#contenu"
          className="sr-only z-50 rounded-sm bg-ink px-4 py-2 font-medium text-canvas focus:not-sr-only focus:fixed focus:left-4 focus:top-3"
        >
          Aller au contenu
        </a>
        <SiteHeader />
        <main id="contenu" tabIndex={-1} className="mx-auto max-w-[960px] px-4 py-8 outline-none sm:py-12">
          {children}
        </main>
        <footer className="mx-auto mt-12 max-w-[960px] px-4 text-sm leading-loose text-mute">
          <nav
            aria-label="Pied de page"
            className="flex flex-wrap justify-center gap-x-5 border-t border-hairline py-2 sm:grid sm:grid-cols-5 sm:gap-0 sm:py-0"
          >
            {FOOTER_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="py-1 text-center hover:text-ink sm:border-l sm:border-hairline sm:py-2 sm:first:border-l-0"
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <p className="flex flex-wrap justify-between gap-2 border-t border-hairline py-6">
            <span>XiMaths</span>
            <a
              href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr"
              rel="license"
              className="hover:text-ink"
            >
              Contenus sous licence CC BY-SA 4.0
            </a>
          </p>
        </footer>
      </body>
    </html>
  );
}
