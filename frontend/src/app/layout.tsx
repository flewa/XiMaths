import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import { cookies } from "next/headers";
import Link from "next/link";
import "katex/dist/katex.min.css";

import { SiteHeader } from "@/components/SiteHeader";
import { SITE_URL, THEME_COOKIE, type Theme } from "@/lib/site";

import "./globals.css";

// Substitut libre de Berkeley Mono recommandé par le document de design.
const mono = JetBrains_Mono({
  variable: "--font-mono-face",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

const DESCRIPTION =
  "Exercices de mathématiques du supérieur, de la licence au master et en prépa, résolus et relus par la communauté.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "XiMaths", template: "%s · XiMaths" },
  description: DESCRIPTION,
  openGraph: { siteName: "XiMaths", locale: "fr_FR", type: "website", description: DESCRIPTION },
  twitter: { card: "summary" },
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
      <body className={`${mono.variable} font-mono antialiased`}>
        <SiteHeader />
        <main className="mx-auto max-w-[960px] px-4 py-8 sm:py-12">{children}</main>
        <footer className="mx-auto mt-12 max-w-[960px] px-4 text-sm leading-loose text-mute">
          <nav
            aria-label="Pied de page"
            className="grid grid-cols-2 border-t border-hairline sm:grid-cols-5"
          >
            {FOOTER_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="border-b border-hairline py-2 text-center hover:text-ink sm:border-b-0 sm:border-l sm:first:border-l-0"
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
