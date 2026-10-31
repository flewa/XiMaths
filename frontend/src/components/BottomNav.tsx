"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type Item = { href: string; glyph: string; label: string; match: (path: string) => boolean };

const FEED: Item = { href: "/", glyph: "~", label: "Fil", match: (path) => path === "/" };
const BROWSE: Item = {
  href: "/exercices",
  glyph: ">",
  label: "Parcourir",
  match: (path) => path.startsWith("/exercices") && path !== "/exercices/nouveau",
};
const CHALLENGE: Item = { href: "/defi", glyph: "⏱", label: "Défi", match: (path) => path.startsWith("/defi") };

const SIGNED_IN: Item[] = [
  FEED,
  BROWSE,
  { href: "/exercices/nouveau", glyph: "+", label: "Publier", match: (path) => path === "/exercices/nouveau" },
  CHALLENGE,
  {
    href: "/progression",
    glyph: "@",
    label: "Moi",
    match: (path) => ["/progression", "/reglages", "/membres", "/notifications"].some((prefix) => path.startsWith(prefix)),
  },
];

// La connexion et l'inscription restent dans l'en-tête et l'accueil.
const VISITOR: Item[] = [
  FEED,
  BROWSE,
  CHALLENGE,
  { href: "/classements", glyph: "#", label: "Classements", match: (path) => path.startsWith("/classements") },
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
      aria-label="Navigation principale"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-hairline bg-canvas pb-[env(safe-area-inset-bottom)] lg:hidden"
    >
      <ul className={`grid ${items.length === 5 ? "grid-cols-5" : "grid-cols-4"}`}>
        {items.map((item) => {
          const active = item.match(pathname);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex min-h-14 flex-col items-center justify-center gap-1 whitespace-nowrap text-[13px] leading-none ${
                  active ? "font-bold text-ink" : "text-mute"
                }`}
              >
                <span
                  aria-hidden="true"
                  className={
                    item.glyph === "+"
                      ? "rounded-sm bg-ink px-2 py-0.5 font-bold text-canvas"
                      : active
                        ? "text-ink"
                        : "text-stone"
                  }
                >
                  [{item.glyph}]
                </span>
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
