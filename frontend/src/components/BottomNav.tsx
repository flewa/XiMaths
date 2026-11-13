"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon, type IconName } from "./Icon";

/** `short` : le mot affiché sous l'icône ; `label` : le nom complet, pour les lecteurs d'écran. */
type Item = { href: string; icon: IconName; label: string; short: string; match: (path: string) => boolean; main?: boolean };

const FEED: Item = { href: "/", icon: "home", label: "Accueil", short: "Accueil", match: (path) => path === "/" };
const BROWSE: Item = {
  href: "/exercices",
  icon: "browse",
  label: "Parcourir les exercices",
  short: "Parcourir",
  match: (path) => path.startsWith("/exercices") && path !== "/exercices/nouveau",
};
const CHALLENGE: Item = { href: "/defi", icon: "timer", label: "Défi du jour", short: "Défi", match: (path) => path.startsWith("/defi") };
const RANKINGS: Item = {
  href: "/classements",
  icon: "trophy",
  label: "Classements",
  short: "Classements",
  match: (path) => path.startsWith("/classements"),
};

// Au centre, ce qu'on vient faire : résoudre. Publier reste dans le menu et sur « Parcourir ».
const SIGNED_IN: Item[] = [
  FEED,
  BROWSE,
  { ...CHALLENGE, main: true },
  RANKINGS,
  {
    href: "/progression",
    icon: "user",
    label: "Ma progression",
    short: "Progression",
    match: (path) => ["/progression", "/reglages", "/membres", "/notifications"].some((prefix) => path.startsWith(prefix)),
  },
];

// La connexion et l'inscription restent dans la barre du haut et l'accueil.
const VISITOR: Item[] = [FEED, BROWSE, { ...CHALLENGE, main: true }, RANKINGS];

// Pendant une session chronométrée, la barre ne doit pas inviter à quitter la page.
const HIDDEN_ON = [/\/chrono$/, /^\/entrainement\//];

/** Barre d'onglets en bas d'écran, sous 1024 px : à portée du pouce. */
export function BottomNav({ signedIn }: { signedIn: boolean }) {
  const pathname = usePathname();
  if (HIDDEN_ON.some((pattern) => pattern.test(pathname))) return null;
  // L'accueil du visiteur tient en une action : pas d'onglets.
  if (!signedIn && pathname === "/") return null;
  const items = signedIn ? SIGNED_IN : VISITOR;
  return (
    <nav
      aria-label="Navigation du bas"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-hairline bg-sidebar/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden"
    >
      <ul className={`grid ${items.length === 5 ? "grid-cols-5" : "grid-cols-4"}`}>
        {items.map((item) => {
          const active = item.match(pathname);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-label={item.label === item.short ? undefined : item.label}
                aria-current={active ? "page" : undefined}
                className={`flex min-h-14 flex-col items-center justify-center gap-0.5 text-xs font-medium leading-none ${active ? "text-ink-deep" : "text-mute"}`}
              >
                {item.main ? (
                  // Plein seulement sur sa page : sinon on croirait l'onglet sélectionné.
                  <span
                    className={`grid h-7 w-10 place-items-center rounded-lg ${
                      active ? "bg-accent text-accent-ink" : "bg-accent-soft text-accent-text"
                    }`}
                  >
                    <Icon name={item.icon} size={18} />
                  </span>
                ) : (
                  <span className="grid h-7 place-items-center">
                    <Icon name={item.icon} size={21} />
                  </span>
                )}
                <span aria-hidden={item.label === item.short ? undefined : true}>{item.short}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
