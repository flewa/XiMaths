import Link from "next/link";

import { Icon } from "./Icon";

/** Les onglets de l'espace de l'équipe. La modération (/moderation) et l'administration
 * (/administration) sont deux pages, mais un seul espace : un administrateur y passe de l'une
 * à l'autre sans changer de menu. Un modérateur ne voit que les onglets de modération. */
export type TeamTab = "apercu" | "signalements" | "messages" | "appels" | "copies" | "membres" | "exercices" | "journal";

export type TeamCounts = { reports: number; messages: number; appeals: number };

const chip = "inline-flex shrink-0 items-center rounded-lg px-3 font-medium";
const chipActive = "bg-selected text-ink-deep";
const chipIdle = "text-mute hover:bg-hover hover:text-ink";

function tabsFor(staff: boolean, counts: TeamCounts) {
  const moderation = [
    { value: "signalements", label: "Signalements", href: "/moderation?file=signalements", count: counts.reports },
    { value: "messages", label: "Messages", href: "/moderation?file=messages", count: counts.messages },
    { value: "appels", label: "Appels", href: "/moderation?file=appels", count: counts.appeals },
  ];
  const journal = { value: "journal", label: "Journal", href: "/moderation?file=journal", count: 0 };
  if (!staff) return [...moderation, journal];
  return [
    { value: "apercu", label: "Vue d'ensemble", href: "/administration", count: 0 },
    ...moderation,
    { value: "copies", label: "Copies", href: "/administration?vue=copies", count: 0 },
    { value: "membres", label: "Membres", href: "/administration?vue=membres", count: 0 },
    { value: "exercices", label: "Exercices", href: "/administration?vue=exercices", count: 0 },
    journal,
  ];
}

/** Titre et onglets, communs aux deux pages. Rien n'est coupé : les onglets passent à la ligne
 * sur grand écran et deviennent un menu sur téléphone. */
export function TeamHeader({ staff, counts, active }: { staff: boolean; counts: TeamCounts; active: TeamTab }) {
  const tabs = tabsFor(staff, counts);
  const current = tabs.find((tab) => tab.value === active);
  const waiting = tabs.reduce((sum, tab) => sum + tab.count, 0);
  return (
    <>
      <h1>{staff ? "Gestion du site" : "Modération"}</h1>
      {/* Le principe, une fois, sur le premier onglet : répété partout, il prenait un demi-écran
          sur téléphone avant chaque liste. */}
      {active === (staff ? "apercu" : "signalements") && (
        <p className="mt-2 max-w-[70ch] text-body">
          Chaque décision est prise par un humain, motivée, envoyée à la personne concernée, contestable en appel et
          inscrite au journal. Tu ne tranches jamais ce qui te concerne : un autre membre de l&apos;équipe le fait.
        </p>
      )}
      {/* Sur téléphone, huit onglets prenaient trois lignes : un menu qui affiche l'onglet ouvert.
          Sur grand écran, ils tiennent sur une ligne. */}
      <details className="plain group relative mt-6 sm:hidden">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-3 rounded-lg border border-hairline px-4 text-sm font-medium text-ink [&::-webkit-details-marker]:hidden">
          <span>
            {current?.label ?? "Sections"}
            {waiting > 0 && <span className="ml-2 text-xs font-semibold text-accent-text">{waiting} en attente</span>}
          </span>
          <Icon name="chevron" size={16} className="text-mute transition-transform group-open:rotate-180" />
        </summary>
        <ul className="mt-1.5 rounded-lg border border-hairline bg-surface-soft p-1.5">
          {tabs.map((tab) => (
            <li key={tab.value}>
              <Link
                href={tab.href}
                aria-current={tab.value === active ? "page" : undefined}
                className={`flex min-h-10 items-center justify-between rounded-md px-3 text-sm ${tab.value === active ? chipActive : chipIdle}`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="rounded-full bg-accent px-1.5 text-xs font-semibold leading-[18px] text-accent-ink">
                    {tab.count}
                  </span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </details>
      <nav aria-label="Espace de l'équipe" className="mt-7 flex flex-wrap gap-1.5 border-b border-hairline pb-3 max-sm:hidden">
        {tabs.map((tab) => (
          <Link
            key={tab.value}
            href={tab.href}
            aria-current={tab.value === active ? "page" : undefined}
            className={`${chip} min-h-10 text-sm ${tab.value === active ? chipActive : chipIdle}`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1.5 rounded-full bg-accent px-1.5 text-xs font-semibold leading-[18px] text-accent-ink">
                {tab.count}
              </span>
            )}
          </Link>
        ))}
      </nav>
    </>
  );
}

/** Filtres d'une liste, en pastilles qui passent à la ligne. */
export function ChipLinks({ label, items }: { label: string; items: { href: string; label: string; active: boolean }[] }) {
  return (
    <nav aria-label={label} className="mt-5 flex flex-wrap gap-1.5">
      {items.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          aria-current={item.active ? "page" : undefined}
          className={`${chip} min-h-8 text-sm ${item.active ? chipActive : chipIdle}`}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
