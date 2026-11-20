import { Icon } from "./Icon";

// Champs : fond légèrement relevé, filet discret, filet corail au focus.
export const inputClass =
  "w-full rounded-lg border border-hairline bg-surface-soft px-3 py-2 text-ink outline-none transition-colors placeholder:text-stone focus:border-accent";

// Trois tailles de bouton sur tout le site : petit (32 px), moyen (40 px, par défaut) et grand
// (48 px, pour l'action unique d'un écran d'accueil).
const button = "inline-flex items-center justify-center gap-1.5 rounded-lg py-1.5 text-center";
const small = "min-h-8 px-3 text-sm";
const medium = "min-h-10 px-4 text-sm";
const large = "min-h-12 px-6 text-base";
const primary =
  "bg-accent font-semibold text-accent-ink hover:brightness-110 disabled:bg-surface-card disabled:text-ash disabled:hover:brightness-100";
const secondary = "bg-surface-card font-medium text-ink hover:bg-surface-dark-elevated disabled:text-ash";

export const primaryButtonClass = `${button} ${medium} ${primary}`;
export const largePrimaryButtonClass = `${button} ${large} ${primary}`;
export const secondaryButtonClass = `${button} ${medium} ${secondary}`;
export const smallSecondaryButtonClass = `${button} ${small} ${secondary}`;
export const smallOutlineButtonClass = `${button} ${small} border border-hairline-strong font-medium text-ink hover:bg-hover`;
export const dangerButtonClass = `${button} ${medium} bg-danger font-semibold text-white hover:brightness-110 disabled:bg-surface-card disabled:text-ash`;

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

export function SubmitButton({
  pending,
  danger = false,
  children,
}: {
  pending: boolean;
  danger?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button type="submit" disabled={pending} className={danger ? dangerButtonClass : primaryButtonClass}>
      {pending ? "Un instant…" : children}
    </button>
  );
}
