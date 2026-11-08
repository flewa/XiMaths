import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { cookies } from "next/headers";
import Link from "next/link";
import "katex/dist/katex.min.css";

import { VerifyBanner } from "@/components/AccountControls";
import { AudienceTracker } from "@/components/Audience";
import { BottomNav } from "@/components/BottomNav";
import { MobileBar, SidebarContent, type NavAccount } from "@/components/SidebarNav";
import { fetchLevels, fetchMe, fetchTopics, nullOnError } from "@/lib/api";
import { chaptersOf } from "@/lib/seo-pages";
import { DEFAULT_THEME, SITE_DESCRIPTION, SITE_URL, SOCIAL_PROFILES, THEME_COOKIE, type Theme } from "@/lib/site";

import "./globals.css";

// Le texte courant ; les titres sont dans la police des formules (voir globals.css).
const sans = Inter({
  variable: "--font-sans-face",
  subsets: ["latin", "latin-ext"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "XiMaths", template: "%s · XiMaths" },
  description: SITE_DESCRIPTION,
  openGraph: { siteName: "XiMaths", locale: "fr_FR", type: "website", description: SITE_DESCRIPTION },
  twitter: { card: "summary_large_image" },
  // Installée sur l'écran d'accueil d'un iPhone, la PWA s'ouvre sans la barre de Safari.
  appleWebApp: { capable: true, title: "XiMaths", statusBarStyle: "default" },
};

export const viewport: Viewport = {
  // Le contenu va jusqu'aux bords arrondis de l'écran ; la barre du bas réserve la zone du geste d'accueil.
  viewportFit: "cover",
  themeColor: "#191919",
};

const FOOTER_LINKS = [
  { href: "/badges", label: "Badges" },
  { href: "/cgu", label: "Conditions" },
  { href: "/confidentialite", label: "Confidentialité" },
];

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Thème choisi dans les réglages ; sans choix, le sombre.
  const theme = ((await cookies()).get(THEME_COOKIE)?.value ?? DEFAULT_THEME) as Theme;
  const [me, levels, topics] = await Promise.all([
    fetchMe().catch(nullOnError),
    fetchLevels().catch(() => []),
    fetchTopics()
      .then(chaptersOf)
      .catch(() => []),
  ]);
  const account: NavAccount | null = me && {
    username: me.username,
    points: me.points,
    pendingReviews: me.pending_reviews,
    unreadNotifications: me.unread_notifications,
    declaredLevel: me.declared_level,
    isStaff: me.is_staff,
  };
  // Site déclaré dans Umami (deploy/statistiques.sh), lu au démarrage du serveur : sans lui,
  // aucune mesure d'audience.
  const audience = process.env.UMAMI_WEBSITE_ID;
  return (
    <html lang="fr" data-theme={theme}>
      {/* Sous 1024 px, la barre d'onglets du bas recouvrirait la fin de la page : on lui fait de la place. */}
      <body className={`${sans.variable} pb-[calc(3.5rem+env(safe-area-inset-bottom))] font-sans antialiased lg:pb-0`}>
        <a
          href="#contenu"
          className="sr-only z-50 rounded-lg bg-accent px-4 py-2 font-medium text-accent-ink focus:not-sr-only focus:fixed focus:left-4 focus:top-3"
        >
          Aller au contenu
        </a>
        {/* La colonne de la barre latérale garde sa teinte jusqu'en bas, même sur une page longue. */}
        <div className="min-h-screen lg:grid lg:grid-cols-[252px_minmax(0,1fr)] lg:bg-[linear-gradient(90deg,var(--sidebar)_252px,var(--canvas)_252px)]">
          <aside aria-label="Barre latérale" className="sticky top-0 hidden h-screen overflow-y-auto bg-sidebar lg:block">
            <SidebarContent account={account} levels={levels} topics={topics} />
          </aside>
          <MobileBar account={account} levels={levels} topics={topics} />
          <div className="min-w-0">
            {me && !me.email_verified && <VerifyBanner email={me.email} />}
            <main
              id="contenu"
              tabIndex={-1}
              className="mx-auto max-w-[860px] px-5 py-8 outline-none sm:px-10 sm:py-14"
            >
              {children}
            </main>
            <footer className="mx-auto max-w-[860px] px-5 pb-10 text-sm text-stone sm:px-10">
              <nav
                aria-label="Pied de page"
                className="flex flex-wrap gap-x-5 gap-y-1 border-t border-hairline pt-5"
              >
                {FOOTER_LINKS.map((link) => (
                  <Link key={link.href} href={link.href} className="hover:text-ink">
                    {link.label}
                  </Link>
                ))}
                {SOCIAL_PROFILES.map((profile) => (
                  <a key={profile.url} href={profile.url} rel="me noopener" className="hover:text-ink">
                    {profile.label}
                  </a>
                ))}
                <a
                  href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr"
                  rel="license"
                  className="hover:text-ink sm:ml-auto"
                >
                  Contenus sous licence CC BY-SA 4.0
                </a>
              </nav>
            </footer>
          </div>
        </div>
        <BottomNav signedIn={me !== null} />
        {audience && <AudienceTracker websiteId={audience} domain={new URL(SITE_URL).hostname} />}
      </body>
    </html>
  );
}
