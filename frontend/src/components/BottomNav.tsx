"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Icon, type IconName } from "./Icon";

type Item = { href: string; icon: IconName; label: string; match: (path: string) => boolean; publish?: boolean };

const FEED: Item = { href: "/", icon: "home", label: "Accueil", match: (path) => path === "/" };
const BROWSE: Item = {
  href: "/exercices",
  icon: "browse",
  label: "Parcourir",
  match: (path) => path.startsWith("/exercices") && path !== "/exercices/nouveau",
};
const CHALLENGE: Item = { href: "/defi", icon: "timer", label: "Défi du jour", match: (path) => path.startsWith("/defi") };

const SIGNED_IN: Item[] = [
  FEED,
  BROWSE,
  {
    href: "/exercices/nouveau",
    icon: "plus",
    label: "Publier un exercice",
    match: (path) => path === "/exercices/nouveau",
    publish: true,
  },
  CHALLENGE,
  {
    href: "/progression",
    icon: "user",
    label: "Ma progression",
    match: (path) => ["/progression", "/reglages", "/membres", "/notifications"].some((prefix) => path.startsWith(prefix)),
  },
];

// La connexion et l'inscription restent dans la barre du haut et l'accueil.
const VISITOR: Item[] = [
  FEED,
  BROWSE,
  CHALLENGE,
  { href: "/classements", icon: "trophy", label: "Classements", match: (path) => path.startsWith("/classements") },
];

// Pendant une session chronométrée, la barre ne doit pas inviter à quitter la page.
const HIDDEN_ON = [/\/chrono$/, /^\/entrainement\//];

/** Barre d'onglets en bas d'écran, sous 1024 px : à portée du pouce. */
export function BottomNav({ signedIn }: { signedIn: boolean }) {
  const pathname = usePathname();
  if (HIDDEN_ON.some((pattern) => pattern.test(pathname))) return null;
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
                aria-label={item.label}
                title={item.label}
                aria-current={active ? "page" : undefined}
                className={`grid min-h-14 place-items-center ${active ? "text-ink-deep" : "text-mute"}`}
              >
                {item.publish ? (
                  <span className="grid h-8 w-10 place-items-center rounded-lg bg-accent text-accent-ink">
                    <Icon name={item.icon} size={20} />
                  </span>
                ) : (
                  <Icon name={item.icon} size={22} />
                )}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
