import Link from "next/link";

/** Barre d'onglets : filet sous la barre, défilement horizontal sur mobile. */
export function Tabs({
  label,
  className = "",
  children,
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <nav
      aria-label={label}
      className={`flex overflow-x-auto border-b border-hairline-strong [scrollbar-width:none] ${className}`}
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
      className={`-mb-px shrink-0 whitespace-nowrap border-b-2 px-4 py-1 font-medium leading-8 ${
        active ? "border-ink text-ink" : "border-transparent text-mute hover:text-ink"
      }`}
    >
      {label}
    </Link>
  );
}
