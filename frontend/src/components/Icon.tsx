/** Icônes au trait, dessinées sur une grille de 20 px. Décoratives : le texte voisin dit tout. */
const PATHS = {
  home: <path d="M3.5 9 10 3.5 16.5 9v7.5h-4.25v-5h-4.5v5H3.5z" />,
  grid: <path d="M3.75 3.75h5v5h-5zM11.25 3.75h5v5h-5zM3.75 11.25h5v5h-5zM11.25 11.25h5v5h-5z" />,
  browse: <path d="M4 5h12M4 10h12M4 15h7" />,
  book: <path d="M10 5.5C8.5 4.3 6.3 4 3.5 4.25v11c2.8-.25 5 .05 6.5 1.25 1.5-1.2 3.7-1.5 6.5-1.25v-11C13.7 4 11.5 4.3 10 5.5zm0 0v11" />,
  // Une page et sa coche : un théorème démontré.
  proof: <path d="M5 3.5h10v13H5zM7.5 10.25l1.75 1.75 3.25-3.5" />,
  timer: (
    <>
      <circle cx="10" cy="11" r="6.25" />
      <path d="M10 8v3.25l2 1.5M8 2.75h4" />
    </>
  ),
  review: <path d="M3.5 4.5h13v9h-8l-3.5 3v-3H3.5z" />,
  bell: (
    <>
      <path d="M5.5 13.5V9a4.5 4.5 0 0 1 9 0v4.5l1.25 1.5H4.25z" />
      <path d="M8.5 17h3" />
    </>
  ),
  trophy: (
    <path d="M6.5 3.5h7v4a3.5 3.5 0 0 1-7 0zM10 11v3.5M7 16.5h6M13.5 5H16v1.25A2.75 2.75 0 0 1 13.25 9M6.5 5H4v1.25A2.75 2.75 0 0 0 6.75 9" />
  ),
  chart: <path d="M4 16h12M6.5 13V9.5M10 13V5.5M13.5 13V8" />,
  plus: <path d="M10 4.5v11M4.5 10h11" />,
  gear: (
    <>
      <circle cx="10" cy="10" r="2.5" />
      <path d="M10 2.75v2M10 15.25v2M2.75 10h2M15.25 10h2M4.9 4.9l1.4 1.4M13.7 13.7l1.4 1.4M4.9 15.1l1.4-1.4M13.7 6.3l1.4-1.4" />
    </>
  ),
  user: (
    <>
      <circle cx="10" cy="7" r="3.25" />
      <path d="M3.75 17a6.25 6.25 0 0 1 12.5 0" />
    </>
  ),
  menu: <path d="M3.5 6h13M3.5 10h13M3.5 14h13" />,
  close: <path d="m5 5 10 10M15 5 5 15" />,
  chevron: <path d="m7 8 3 3 3-3" />,
  flag: <path d="M5 17V3.5M5 4h9l-1.75 3.5L14 11H5" />,
  shield: <path d="M10 3 4.5 5v4.5c0 3.5 2.4 6.2 5.5 7.5 3.1-1.3 5.5-4 5.5-7.5V5z" />,
  logout: <path d="M8 4.5H4.5v11H8M12 6.5 15.5 10 12 13.5M15.5 10H8" />,
  alert: (
    <>
      <circle cx="10" cy="10" r="7" />
      <path d="M10 6.5v4.25M10 13.5v.01" />
    </>
  ),
  check: <path d="m5 10.5 3.25 3.25L15 7" />,
  search: (
    <>
      <circle cx="9" cy="9" r="5.5" />
      <path d="m13 13 3.5 3.5" />
    </>
  ),
  camera: (
    <>
      <path d="M3.5 7h3l1.5-2h4l1.5 2h3v8.5h-13z" />
      <circle cx="10" cy="11" r="2.75" />
    </>
  ),
  share: <path d="M10 12.5V3M6.5 6.5 10 3l3.5 3.5M4.5 10.5v6h11v-6" />,
  phone: (
    <>
      <rect x="6" y="2.5" width="8" height="15" rx="1.75" />
      <path d="M9.25 14.75h1.5" />
    </>
  ),
} as const;

export type IconName = keyof typeof PATHS;

export function Icon({ name, size = 18, className = "" }: { name: IconName; size?: number; className?: string }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 ${className}`}
    >
      {PATHS[name]}
    </svg>
  );
}
