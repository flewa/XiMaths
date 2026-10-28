/**
 * Étiquette. `strong` : la puce sombre du design, pour ce qui doit ressortir ;
 * sinon le texte entre crochets, à la façon d'une page de manuel.
 */
export function Tag({ children, strong = false }: { children: React.ReactNode; strong?: boolean }) {
  if (strong) {
    return (
      <span className="inline-block rounded-sm bg-surface-dark px-2 text-sm leading-6 text-on-dark">
        {children}
      </span>
    );
  }
  return <span className="text-mute">[{children}]</span>;
}
