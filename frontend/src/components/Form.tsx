import { Icon } from "./Icon";

// Champs : fond légèrement relevé, filet discret, filet corail au focus.
export const inputClass =
  "w-full rounded-lg border border-hairline bg-surface-soft px-3 py-2 text-ink outline-none transition-colors placeholder:text-stone focus:border-accent";

export const primaryButtonClass =
  "inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg bg-accent px-4 py-1.5 text-center text-[15px] font-semibold text-accent-ink hover:brightness-110 disabled:bg-surface-card disabled:text-ash disabled:hover:brightness-100";

export const secondaryButtonClass =
  "inline-flex min-h-9 items-center justify-center gap-1.5 rounded-lg bg-surface-card px-4 py-1.5 text-center text-[15px] font-medium text-ink hover:bg-surface-dark-elevated";

export function Field({
  label,
  htmlFor,
  hint,
  children,
}: {
  label: string;
  htmlFor?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={htmlFor} className="block font-medium">
        {label}
      </label>
      {children}
      {hint && <p className="text-sm text-mute">{hint}</p>}
    </div>
  );
}

export function FormMessage({ error, success }: { error?: string | null; success?: string | null }) {
  if (error) {
    return (
      <p role="alert" className="flex gap-2 rounded-lg bg-danger/10 px-3 py-2 text-danger-text">
        <Icon name="alert" className="mt-0.5" />
        {error}
      </p>
    );
  }
  if (success) {
    return (
      <p role="status" className="flex gap-2 rounded-lg bg-surface-soft px-3 py-2">
        <Icon name="check" className="mt-0.5 text-success" />
        {success}
      </p>
    );
  }
  return null;
}

/** Case à cocher avec son libellé, à la couleur du site. */
export function Checkbox({
  checked,
  onChange,
  name,
  children,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
  name?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex cursor-pointer gap-2.5">
      <input
        type="checkbox"
        name={name}
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="shrink-0"
      />
      <span>{children}</span>
    </label>
  );
}

export function SubmitButton({ pending, children }: { pending: boolean; children: React.ReactNode }) {
  return (
    <button type="submit" disabled={pending} className={primaryButtonClass}>
      {pending ? "Un instant…" : children}
    </button>
  );
}
