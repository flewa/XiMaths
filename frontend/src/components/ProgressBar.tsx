/** Barre de progression fine ; la valeur est dite à côté, en texte. */
export function ProgressBar({ done, target, className = "" }: { done: number; target: number; className?: string }) {
  const ratio = target > 0 ? Math.min(1, done / target) : 0;
  return (
    <span aria-hidden="true" className={`inline-block h-1.5 w-40 overflow-hidden rounded-full bg-surface-card align-middle ${className}`}>
      <span className="block h-full rounded-full bg-accent" style={{ width: `${ratio * 100}%` }} />
    </span>
  );
}
