import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import "katex/dist/katex.min.css";

import { SiteHeader } from "@/components/SiteHeader";

import "./globals.css";

// Substitut libre de Berkeley Mono recommandé par le document de design.
const mono = JetBrains_Mono({
  variable: "--font-mono-face",
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: { default: "XiMaths", template: "%s · XiMaths" },
  description:
    "Exercices de mathématiques du supérieur, résolus et relus par la communauté.",
};

const FOOTER_LINKS = [
  { href: "/exercices", label: "Parcourir" },
  { href: "/classements", label: "Classements" },
  { href: "/badges", label: "Badges" },
  { href: "/signalements", label: "Signalements" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${mono.variable} font-mono antialiased`}>
        <SiteHeader />
        <main className="mx-auto max-w-[960px] px-4 py-8 sm:py-12">{children}</main>
        <footer className="mx-auto mt-12 max-w-[960px] px-4 text-sm leading-loose text-mute">
          <nav
            aria-label="Pied de page"
            className="grid grid-cols-2 border-t border-hairline sm:grid-cols-4"
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
            <span>Contenus sous licence CC BY-SA 4.0</span>
          </p>
        </footer>
      </body>
    </html>
  );
}
