"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";

/** Barre d'onglets : filet sous la barre, défilement horizontal quand elle déborde.
 * L'onglet actif est ramené dans la vue, et un fondu à droite signale la suite sur mobile. */
export function Tabs({
  label,
  className = "",
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  const strip = useRef<HTMLElement>(null);

  useEffect(() => {
    const container = strip.current;
    const active = container?.querySelector<HTMLElement>('[aria-current="page"]');
    if (!container || !active) return;
    // Centré, sans faire défiler la page elle-même.
    container.scrollLeft = active.offsetLeft - (container.clientWidth - active.offsetWidth) / 2;
  }, []);

  return (
    <nav
      ref={strip}
      aria-label={label}
      className={`flex overflow-x-auto border-b border-hairline-strong [scrollbar-width:none] max-md:[mask-image:linear-gradient(to_right,#000_88%,transparent)] ${className}`}
    >
      {children}
    </nav>
  );
}

/** Onglet : gris au repos, encre et souligné quand il est actif. */
export function FilterChip({
  href,
  label,
  title,
  active,
}: {
  href: string;
  label: string;
  title?: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      title={title}
      aria-current={active ? "page" : undefined}
      className={`-mb-px shrink-0 whitespace-nowrap border-b-2 px-3 py-1 font-medium leading-8 ${
        active ? "border-ink text-ink" : "border-transparent text-mute hover:text-ink"
      }`}
    >
      {label}
    </Link>
  );
}
