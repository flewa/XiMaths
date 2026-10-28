/** Page de texte : sections titrées par un libellé gras au-dessus d'un filet. */
export function ProseSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="border-b border-hairline pb-2 font-bold">{title}</h2>
      <div className="mt-3 space-y-3 text-body">{children}</div>
    </section>
  );
}

/** Liste à puces ASCII. */
export function Bullets({ items }: { items: React.ReactNode[] }) {
  return (
    <ul className="space-y-1">
      {items.map((item, index) => (
        <li key={index} className="flex gap-2">
          <span className="shrink-0 text-mute">[+]</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function DraftNotice() {
  return (
    <p className="mt-4 border-l-2 border-hairline-strong pl-3 text-sm text-mute">
      [!] Version de travail, à faire valider par un juriste avant l&apos;ouverture au public.
    </p>
  );
}
