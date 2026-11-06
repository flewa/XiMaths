/** Étiquette. `strong` : corail, pour ce qui doit ressortir ; sinon discrète. */
export function Tag({ children, strong = false }: { children: React.ReactNode; strong?: boolean }) {
  return (
    <span
      className={`inline-block whitespace-nowrap rounded-md px-1.5 text-[13px] font-medium leading-6 ${
        strong ? "bg-accent-soft text-accent-text" : "bg-surface-card text-mute"
      }`}
    >
      {children}
    </span>
  );
}
