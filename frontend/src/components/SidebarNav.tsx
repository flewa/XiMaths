"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import type { Avatar as AvatarData, Level, Topic } from "@/lib/api";
import { LEVEL_TRACKS } from "@/lib/labels";
import { chapterPath, levelPath } from "@/lib/seo-pages";

import { LogoutButton } from "./AccountControls";
import { Avatar } from "./Avatar";
import { Icon, type IconName } from "./Icon";

/** Ce que la navigation montre du membre connecté. */
export type NavAccount = {
  username: string;
  avatar: AvatarData;
  points: number;
  /** Niveau de contributeur. */
  level: number;
  /** Questions de compréhension à ouvrir ou à finir. */
  pendingQuestions: number;
  pendingReviews: number;
  unreadNotifications: number;
  declaredLevel: string | null;
  /** Équipe de modération, et ce qui attend dans ses files. */
  team: boolean;
  /** Tiré au sort pour relire : sinon, l'entrée Relectures ne mènerait qu'à une page d'attente. */
  reviewer: boolean;
  moderationPending: number;
  /** Administrateur du site : il a le panneau d'administration. */
  staff: boolean;
};

type Item = {
  href: string;
  icon: IconName;
  label: string;
  match: (path: string) => boolean;
  count?: number;
  hot?: boolean;
};

function itemsFor(account: NavAccount | null): Item[] {
  const items: Item[] = [
    {
      href: "/",
      icon: "home",
      label: "Accueil",
      match: (path) => path === "/",
    },
    {
      href: "/exercices",
      icon: "browse",
      label: "Parcourir",
      match: (path) =>
        path.startsWith("/exercices") && path !== "/exercices/nouveau",
    },
    {
      href: "/defi",
      icon: "timer",
      label: "Défi du jour",
      match: (path) => path.startsWith("/defi"),
    },
    // Les fiches publiées ; l'équipe y voit aussi celles en relecture.
    {
      href: "/rappels",
      icon: "book",
      label: "Rappels de cours",
      match: (path) => path.startsWith("/rappels"),
    },
  ];
  if (account) {
    items.push(
      ...(account.reviewer || account.pendingReviews > 0
        ? [
            {
              href: "/relectures",
              icon: "review" as IconName,
              label: "Relectures",
              match: (path: string) => path.startsWith("/relectures") || path.startsWith("/evaluations"),
              count: account.pendingReviews,
              hot: true,
            },
          ]
        : []),
      // Un seul espace pour l'équipe : l'administrateur y trouve aussi la modération.
      ...(account.team
        ? [
            {
              href: account.staff ? "/administration" : "/moderation",
              icon: (account.staff ? "grid" : "shield") as IconName,
              label: account.staff ? "Gestion du site" : "Modération",
              match: (path: string) => path.startsWith("/moderation") || path.startsWith("/administration"),
              count: account.moderationPending,
              hot: true,
            },
          ]
        : []),
      {
        href: "/notifications",
        icon: "bell",
        label: "Notifications",
        match: (path) => path.startsWith("/notifications"),
        count: account.unreadNotifications,
      },
    );
  }
  items.push({
    href: "/classements",
    icon: "trophy",
    label: "Classements",
    match: (path) => path.startsWith("/classements"),
  });
  if (account) {
    items.push({
      href: "/progression",
      icon: "chart",
      label: "Progression",
      match: (path) => path.startsWith("/progression"),
    });
  }
  return items;
}

const row = "flex min-h-8 items-center gap-2.5 rounded-md px-2 font-medium";

/** Nom court d'un niveau dans le menu : « Licence 1 », « MPSI », « BCPST », « ECG ». L'année
 * est donnée par l'intertitre de la filière, l'étiquette de code ferait doublon. */
function shortName(level: Level) {
  return level.name.replace(/^Prépa /, "").replace(/ (\d(?:re|e) année)$/, "");
}

const YEAR_LABELS: Record<number, string> = { 1: "1re année", 2: "2e année" };
const MENU_KEY = "ximaths.menu";

/** Groupes du menu ouverts à la main : gardés dans ce navigateur. */
function storedGroups(): Record<string, boolean> {
  try {
    const value = JSON.parse(window.localStorage.getItem(MENU_KEY) ?? "{}");
    return value && typeof value === "object" ? value : {};
  } catch {
    return {};
  }
}

function storeGroup(key: string, open: boolean) {
  try {
    window.localStorage.setItem(MENU_KEY, JSON.stringify({ ...storedGroups(), [key]: open }));
  } catch {
    // Stockage refusé (navigation privée) : le menu oublie, sans gêne.
  }
}

/** Groupe repliable du menu. Fermé par défaut, sauf s'il contient la page affichée ; ensuite,
 * ce que le membre a ouvert ou fermé, retenu d'une visite à l'autre. */
function MenuGroup({ id, label, current, children }: { id: string; label: string; current: boolean; children: React.ReactNode }) {
  const [open, setOpen] = useState(current);
  useEffect(() => {
    const stored = storedGroups()[id];
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (!current && stored !== undefined) setOpen(stored);
  }, [id, current]);
  return (
    <details
      open={open || current}
      onToggle={(event) => {
        const next = event.currentTarget.open;
        if (next !== (open || current)) {
          setOpen(next);
          storeGroup(id, next);
        }
      }}
      className="plain group"
    >
      <summary className={`${row} text-mute hover:bg-hover hover:text-ink`}>
        <Icon name="chevron" size={16} className="-rotate-90 text-stone transition-transform group-open:rotate-0" />
        {label}
      </summary>
      {children}
    </details>
  );
}

function MenuLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <li>
      <Link
        href={href}
        aria-current={active ? "page" : undefined}
        className={`${row} pl-7 ${active ? "bg-selected text-ink-deep" : "text-mute hover:bg-hover hover:text-ink"}`}
      >
        <span className="truncate">{label}</span>
      </Link>
    </li>
  );
}

/** Les niveaux d'une filière. En prépa, rangés sous « 1re année » et « 2e année ». */
function LevelGroup({ track, label, levels, pathname }: { track: string; label: string; levels: Level[]; pathname: string }) {
  if (levels.length === 0) return null;
  const current = levels.some((level) => pathname === levelPath(level.code));
  const years = track === "universite" ? [null] : [...new Set(levels.map((level) => level.year))];
  return (
    <MenuGroup id={track} label={label} current={current}>
      {years.map((year) => (
        <div key={year ?? "tous"}>
          {year !== null && years.length > 1 && (
            <p className="pb-0.5 pl-7 pt-1.5 text-xs font-medium text-mute">
              {YEAR_LABELS[year] ?? `${year}e année`}
            </p>
          )}
          <ul>
            {levels
              .filter((level) => year === null || level.year === year)
              .map((level) => (
                <MenuLink key={level.code} href={levelPath(level.code)} label={shortName(level)} active={pathname === levelPath(level.code)} />
              ))}
          </ul>
        </div>
      ))}
    </MenuGroup>
  );
}

/** Compte, en bas de la barre : un menu qui s'ouvre vers le haut. Un point corail signale
 * une question de compréhension en attente : elle a un délai. */
function AccountFooter({ account }: { account: NavAccount }) {
  const pathname = usePathname();
  const link = "flex items-center rounded-md px-3 py-1.5 hover:bg-hover hover:text-ink";
  const waiting = account.pendingQuestions;
  return (
    <details key={pathname} className="plain relative">
      <summary className={`${row} text-ink hover:bg-hover`}>
        <span className="relative">
          <Avatar avatar={account.avatar} size={24} />
          {waiting > 0 && (
            <span className="absolute -right-1 -top-1 size-2.5 rounded-full bg-accent ring-2 ring-canvas">
              <span className="sr-only">{waiting > 1 ? `, ${waiting} questions t'attendent` : ", une question t'attend"}</span>
            </span>
          )}
        </span>
        <span className="truncate">{account.username}</span>
        <Icon name="gear" size={17} className="ml-auto text-stone" />
      </summary>
      <div className="absolute inset-x-0 bottom-full z-10 mb-2 rounded-lg border border-hairline bg-surface-card p-1.5 text-mute shadow-2xl">
        <Link href="/progression" className="block rounded-md px-3 py-2 hover:bg-hover">
          <span className="block text-sm tabular-nums text-ink">{account.points} points</span>
          <span className="block text-xs">Niveau {account.level} · ma progression</span>
        </Link>
        <div className="mt-1 border-t border-hairline pt-1">
          <Link href={`/membres/${encodeURIComponent(account.username)}`} className={link}>
            Mon profil
          </Link>
          <Link href="/reglages" className={link}>
            Réglages
          </Link>
        </div>
        <div className="mt-1 border-t border-hairline pt-1">
          <p className="px-3 pb-0.5 pt-1 text-xs font-semibold uppercase tracking-[0.04em] text-mute">Modération</p>
          <Link href="/signalements" className={link}>
            Mes signalements
          </Link>
          <Link href="/questions" className={link}>
            Mes questions
            {waiting > 0 && (
              <span className="ml-auto rounded-full bg-accent px-1.5 text-xs font-semibold leading-[18px] text-accent-ink">
                {waiting}
              </span>
            )}
          </Link>
          <Link href="/decisions" className={link}>
            Mes décisions
          </Link>
        </div>
        <div className="mt-1 border-t border-hairline pt-1">
          <LogoutButton className={`${link} w-full text-left`} />
        </div>
      </div>
    </details>
  );
}

export function Brand({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      className={`flex items-baseline gap-2 text-[17px] font-semibold text-ink-deep ${className}`}
    >
      <span
        aria-hidden="true"
        className="font-serif text-[26px] italic leading-none text-accent-text"
      >
        ξ
      </span>
      XiMaths
    </Link>
  );
}

/** Contenu de la barre latérale, sur ordinateur comme dans le tiroir mobile. */
export function SidebarContent({
  account,
  levels,
  topics,
}: {
  account: NavAccount | null;
  levels: Level[];
  topics: Topic[];
}) {
  const pathname = usePathname();
  return (
    <div className="flex min-h-full flex-col px-2.5 py-3 text-sm">
      <Brand className="px-2 pb-3.5 pt-1" />
      {/* Pour un membre, publier est une action parmi d'autres : le corail est gardé pour le
        geste principal de chaque page (envoyer sa copie, rendre sa relecture). */}
      <Link
        href={account ? "/exercices/nouveau" : "/inscription"}
        className={`mx-0.5 mb-3.5 flex h-9 items-center justify-center gap-1.5 rounded-lg font-semibold ${
          account
            ? "border border-hairline bg-surface-card text-ink hover:bg-hover"
            : "bg-accent text-accent-ink hover:brightness-110"
        }`}
      >
        {account && <Icon name="plus" size={16} />}
        {account ? "Publier un exercice" : "Créer un compte"}
      </Link>

      <nav aria-label="Navigation principale">
        <ul>
          {itemsFor(account).map((item) => {
            const active = item.match(pathname);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={`${row} ${active ? "bg-selected text-ink-deep" : "text-mute hover:bg-hover hover:text-ink"}`}
                >
                  <Icon name={item.icon} />
                  {item.label}
                  {item.count ? (
                    <span
                      className={`ml-auto text-xs font-semibold ${item.hot ? "text-accent-text" : "text-mute"}`}
                    >
                      {item.count}
                    </span>
                  ) : null}
                </Link>
              </li>
            );
          })}
        </ul>

        <p className="mb-1 mt-5 px-2 text-xs font-medium text-mute">Niveaux</p>
        {LEVEL_TRACKS.map(({ track, label }) => (
          <LevelGroup key={track} track={track} label={label} levels={levels.filter((level) => level.track === track)} pathname={pathname} />
        ))}
        {topics.length > 0 && (
          <MenuGroup id="chapitres" label="Chapitres" current={pathname.startsWith("/chapitres")}>
            <ul>
              <MenuLink href="/chapitres" label="Tous les chapitres" active={pathname === "/chapitres"} />
              {topics.map((topic) => (
                <MenuLink key={topic.slug} href={chapterPath(topic.slug)} label={topic.name} active={pathname === chapterPath(topic.slug)} />
              ))}
            </ul>
          </MenuGroup>
        )}
      </nav>

      {/* Le compte reste visible en bas, même quand le menu défile. */}
      <div className="sticky bottom-0 -mb-3 mt-auto border-t border-hairline bg-sidebar pb-3 pt-3">
        {account ? (
          <AccountFooter account={account} />
        ) : (
          <Link
            href="/connexion"
            className={`${row} text-mute hover:bg-hover hover:text-ink`}
          >
            <Icon name="user" />
            Se connecter
          </Link>
        )}
      </div>
    </div>
  );
}

/** Sous 1024 px : barre du haut, et la barre latérale dans un tiroir. */
export function MobileBar({
  account,
  levels,
  topics,
}: {
  account: NavAccount | null;
  levels: Level[];
  topics: Topic[];
}) {
  const pathname = usePathname();
  // Le tiroir reste ouvert sur la page où on l'a ouvert : changer de page le referme.
  const [openedOn, setOpenedOn] = useState<string | null>(null);
  const open = openedOn === pathname;
  const setOpen = (value: boolean) => setOpenedOn(value ? pathname : null);
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    closeButton.current?.focus();
    const onKey = (event: KeyboardEvent) =>
      event.key === "Escape" && setOpenedOn(null);
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  // L'accueil du visiteur a son propre en-tête, réduit au nom du site et à la connexion.
  if (!account && pathname === "/") return null;

  return (
    <>
      {/* Le tiroir est un frère de la barre, pas un enfant : le flou de la barre ferait de
        celle-ci le cadre de tout élément fixe placé dedans. */}
      <div className="sticky top-0 z-20 flex h-14 items-center gap-1 bg-canvas/95 px-2 backdrop-blur lg:hidden">
        <button
          type="button"
          aria-label="Ouvrir le menu"
          aria-expanded={open}
          onClick={() => setOpen(true)}
          className="grid size-10 place-items-center rounded-lg text-mute hover:bg-hover hover:text-ink"
        >
          <Icon name="menu" size={20} />
        </button>
        <Brand />
        <div className="ml-auto flex items-center gap-1">
          {account ? (
            <Link
              href="/notifications"
              aria-label={`Notifications, ${account.unreadNotifications} non lues`}
              className="relative grid size-10 place-items-center rounded-lg text-mute hover:bg-hover hover:text-ink"
            >
              <Icon name="bell" size={19} />
              {account.unreadNotifications > 0 && (
                <span
                  aria-hidden="true"
                  className="absolute right-2.5 top-2.5 size-1.5 rounded-full bg-accent"
                />
              )}
            </Link>
          ) : (
            <Link
              href="/connexion"
              className="rounded-lg px-3 py-2 text-sm font-medium text-ink hover:bg-hover"
            >
              Se connecter
            </Link>
          )}
        </div>
      </div>

      {open && (
        <>
          <div
            aria-hidden="true"
            className="fixed inset-0 z-30 bg-black/55"
            onClick={() => setOpen(false)}
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Menu"
            className="thin-scroll fixed inset-y-0 left-0 z-40 w-[84%] max-w-80 overflow-y-auto bg-sidebar shadow-2xl"
          >
            <button
              ref={closeButton}
              type="button"
              aria-label="Fermer le menu"
              onClick={() => setOpen(false)}
              className="absolute right-2 top-2 grid size-10 place-items-center rounded-lg text-mute hover:bg-hover hover:text-ink"
            >
              <Icon name="close" size={18} />
            </button>
            <SidebarContent account={account} levels={levels} topics={topics} />
          </div>
        </>
      )}
    </>
  );
}
