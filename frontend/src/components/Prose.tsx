/** Page de texte : sections titrées. */
export function ProseSection({ title, id, children }: { title: string; id?: string; children: React.ReactNode }) {
  return (
    <section id={id} className="mt-10 scroll-mt-20">
      <h2>{title}</h2>
      <div className="mt-3 space-y-3 text-body">{children}</div>
    </section>
  );
}

/** Liste à puces. */
export function Bullets({ items }: { items: React.ReactNode[] }) {
  return (
    <ul className="space-y-1">
      {items.map((item, index) => (
        <li key={index} className="flex gap-2">
          <span aria-hidden="true" className="mt-[0.6em] size-1.5 shrink-0 rounded-full bg-stone" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
