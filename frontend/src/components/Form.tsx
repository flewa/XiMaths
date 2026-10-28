// Champs : fond doux, filet, et une bordure d'encre au focus, sans halo.
export const inputClass =
  "w-full rounded-sm border border-hairline bg-surface-soft px-3 py-2 text-ink outline-none transition-colors placeholder:text-ash focus:border-ink focus:bg-canvas";

export const primaryButtonClass =
  "inline-block h-9 rounded-sm bg-ink px-5 font-medium leading-9 text-canvas active:bg-ink-deep disabled:bg-surface-card disabled:text-ash";

export const secondaryButtonClass =
  "inline-block h-9 rounded-sm border border-hairline-strong bg-canvas px-5 font-medium leading-[34px] text-ink active:bg-surface-card";

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
      <p role="alert" className="border-l-2 border-danger pl-3 text-danger-text">
        [x] {error}
      </p>
    );
  }
  if (success) {
    return (
      <p role="status" className="border-l-2 border-ink pl-3">
        [+] {success}
      </p>
    );
  }
  return null;
}

export function SubmitButton({ pending, children }: { pending: boolean; children: React.ReactNode }) {
  return (
    <button type="submit" disabled={pending} className={primaryButtonClass}>
      {pending ? "Un instant…" : children}
    </button>
  );
}
