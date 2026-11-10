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
  moderationPending: number;
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
      {
        href: "/relectures",
        icon: "review",
        label: "Relectures",
        match: (path) =>
          path.startsWith("/relectures") || path.startsWith("/evaluations"),
        count: account.pendingReviews,
        hot: true,
      },
      ...(account.team
        ? [
            {
              href: "/moderation",
              icon: "shield" as IconName,
              label: "Modération",
              match: (path: string) => path.startsWith("/moderation"),
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

/** Les niveaux d'une filière, rangés comme des pages : ouverts si le membre y a déclaré le sien. */
/** À côté de l'étiquette du code : « Licence 1 », « MPSI », « 1re année » (BCPST, ECG, B/L). */
function shortName(level: Level) {
  const name = level.name.replace(/^Prépa /, "");
  const year = name.match(/ (\d(?:re|e) année)$/);
  return year ? year[1] : name;
}

function LevelGroup({
  label,
  levels,
  open,
}: {
  label: string;
  levels: Level[];
  open: boolean;
}) {
  if (levels.length === 0) return null;
  return (
    <details open={open} className="plain group">
      <summary className={`${row} text-mute hover:bg-hover hover:text-ink`}>
        <Icon
          name="chevron"
          size={16}
          className="-rotate-90 text-stone transition-transform group-open:rotate-0"
        />
        {label}
      </summary>
      <ul>
        {levels.map((level) => (
          <li key={level.code}>
            <Link
              href={levelPath(level.code)}
              className={`${row} pl-7 text-mute hover:bg-hover hover:text-ink`}
            >
              <span className="grid h-5 min-w-7 place-items-center rounded px-1 text-[11px] font-semibold text-ink bg-selected">
                {level.code}
              </span>
              <span className="truncate">
                {shortName(level)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </details>
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
          <p className="px-3 pb-0.5 pt-1 text-[11px] font-semibold uppercase tracking-[0.04em] text-stone">Modération</p>
          <Link href="/signalements" className={link}>
            Mes signalements
          </Link>
          <Link href="/questions" className={link}>
            Mes questions
            {waiting > 0 && (
              <span className="ml-auto rounded-full bg-accent px-1.5 text-[11px] font-semibold leading-[18px] text-accent-ink">
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
  const declared = levels.find(
    (level) => level.code === account?.declaredLevel,
  );
  return (
    <div className="flex min-h-full flex-col px-2.5 py-3 text-sm">
      <Brand className="px-2 pb-3.5 pt-1" />
      <Link
        href={account ? "/exercices/nouveau" : "/inscription"}
        className="mx-0.5 mb-3.5 flex h-9 items-center justify-center gap-1.5 rounded-lg bg-accent font-semibold text-accent-ink hover:brightness-110"
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
                      className={`ml-auto text-xs font-semibold ${item.hot ? "text-accent-text" : "text-stone"}`}
                    >
                      {item.count}
                    </span>
                  ) : null}
                </Link>
              </li>
            );
          })}
        </ul>

        <p className="mb-1 mt-5 px-2 text-xs font-medium text-stone">Niveaux</p>
        {LEVEL_TRACKS.map(({ track, label }, index) => (
          <LevelGroup
            key={track}
            label={label}
            levels={levels.filter((level) => level.track === track)}
            open={declared ? declared.track === track : index === 0}
          />
        ))}
        {topics.length > 0 && (
          <details className="plain group">
            <summary className={`${row} text-mute hover:bg-hover hover:text-ink`}>
              <Icon
                name="chevron"
                size={16}
                className="-rotate-90 text-stone transition-transform group-open:rotate-0"
              />
              Chapitres
            </summary>
            <ul>
              {topics.map((topic) => (
                <li key={topic.slug}>
                  <Link
                    href={chapterPath(topic.slug)}
                    className={`${row} pl-7 text-mute hover:bg-hover hover:text-ink`}
                  >
                    {topic.name}
                  </Link>
                </li>
              ))}
            </ul>
          </details>
        )}
      </nav>

      <div className="mt-auto border-t border-hairline pt-3">
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
            className="fixed inset-y-0 left-0 z-40 w-[84%] max-w-80 overflow-y-auto bg-sidebar shadow-2xl"
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
