"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { Level, Me } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { THEME_COOKIE, type Theme } from "@/lib/site";

import { AsciiCheckbox, Field, FormMessage, SubmitButton, inputClass } from "./Form";

export function PreferencesForm({ me, levels }: { me: Me; levels: Level[] }) {
  const router = useRouter();
  const [level, setLevel] = useState(me.declared_level ?? "");
  const [tiersTemps, setTiersTemps] = useState(me.tiers_temps);
  const [visible, setVisible] = useState(me.leaderboard_visible);
  const [emails, setEmails] = useState(me.email_notifications);
  const [digest, setDigest] = useState(me.weekly_digest);
  const [challenge, setChallenge] = useState(me.daily_challenge_notifications);
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const saved = await apiPost("/auth/preferences", {
      declared_level: level,
      tiers_temps: tiersTemps,
      leaderboard_visible: visible,
      email_notifications: emails,
      weekly_digest: digest,
      daily_challenge_notifications: challenge,
    });
    setPending(false);
    setResult(saved.ok ? { success: "Réglages enregistrés." } : { error: saved.error });
    if (saved.ok) router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5">
      <Field label="Niveau déclaré" htmlFor="declared_level" hint="Il choisit ton fil d'accueil et tes pairs dans les classements.">
        <select id="declared_level" value={level} onChange={(event) => setLevel(event.target.value)} className={inputClass}>
          <option value="">Aucun</option>
          {levels.map((item) => (
            <option key={item.code} value={item.code}>
              {item.name}
            </option>
          ))}
        </select>
      </Field>
      <fieldset className="space-y-2">
        <legend className="font-medium">Entraînement et classements</legend>
        <AsciiCheckbox checked={tiersTemps} onChange={setTiersTemps}>
          Tiers-temps <span className="text-mute">· durée ×1,33 dans tous les modes chronométrés</span>
        </AsciiCheckbox>
        <AsciiCheckbox checked={visible} onChange={setVisible}>
          Apparaître dans les classements <span className="text-mute">· et montrer mes points sur mon profil</span>
        </AsciiCheckbox>
      </fieldset>
      <fieldset className="space-y-2">
        <legend className="font-medium">Emails</legend>
        <AsciiCheckbox checked={emails} onChange={setEmails}>
          Ce qui me concerne directement{" "}
          <span className="text-mute">· retrait d&apos;un contenu, décision de modération, question à mon sujet</span>
        </AsciiCheckbox>
        <AsciiCheckbox checked={digest} onChange={setDigest}>
          Résumé hebdomadaire <span className="text-mute">· un email le lundi, s&apos;il s&apos;est passé quelque chose</span>
        </AsciiCheckbox>
        <p className="text-sm text-mute">Jamais d&apos;email entre 22 h et 8 h : ils partent à 8 h.</p>
      </fieldset>
      <fieldset className="space-y-2">
        <legend className="font-medium">Notifications</legend>
        <AsciiCheckbox checked={challenge} onChange={setChallenge}>
          Défi du jour <span className="text-mute">· une notification à son ouverture, dans mon niveau déclaré</span>
        </AsciiCheckbox>
      </fieldset>
      <FormMessage error={result.error} success={result.success} />
      <SubmitButton pending={pending}>Enregistrer</SubmitButton>
    </form>
  );
}

const THEMES: { value: Theme; label: string }[] = [
  { value: "system", label: "Comme le système" },
  { value: "light", label: "Clair" },
  { value: "dark", label: "Sombre" },
];

function saveThemeCookie(value: Theme) {
  document.cookie =
    value === "system"
      ? `${THEME_COOKIE}=; path=/; max-age=0; samesite=lax`
      : `${THEME_COOKIE}=${value}; path=/; max-age=31536000; samesite=lax`;
}

/** Le thème est une préférence d'affichage : un cookie du navigateur, pas un réglage du compte. */
export function ThemeChoice({ current }: { current: Theme }) {
  const router = useRouter();
  const [theme, setTheme] = useState(current);

  function choose(value: Theme) {
    setTheme(value);
    saveThemeCookie(value);
    router.refresh();
  }

  return (
    <fieldset className="space-y-2">
      <legend className="sr-only">Thème</legend>
      {THEMES.map((option) => (
        <label key={option.value} className="flex gap-2">
          <input
            type="radio"
            name="theme"
            value={option.value}
            checked={theme === option.value}
            onChange={() => choose(option.value)}
            className="shrink-0"
          />
          <span>{option.label}</span>
        </label>
      ))}
    </fieldset>
  );
}

export function PasswordForm({ hasPassword }: { hasPassword: boolean }) {
  const [result, setResult] = useState<{ error?: string; success?: string }>({});
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    setPending(true);
    const saved = await apiPost("/auth/password", {
      current_password: form.get("current_password") ?? "",
      new_password: form.get("new_password"),
    });
    setPending(false);
    if (saved.ok) formElement.reset();
    setResult(saved.ok ? { success: "Mot de passe changé." } : { error: saved.error });
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {hasPassword ? (
        <Field label="Mot de passe actuel" htmlFor="current_password">
          <input
            id="current_password"
            name="current_password"
            type="password"
            required
            autoComplete="current-password"
            className={inputClass}
          />
        </Field>
      ) : (
        <p className="text-body">Ton compte a été créé avec Google : tu peux aussi choisir un mot de passe.</p>
      )}
      <Field label="Nouveau mot de passe" htmlFor="new_password">
        <input
          id="new_password"
          name="new_password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          className={inputClass}
        />
      </Field>
      <FormMessage error={result.error} success={result.success} />
      <SubmitButton pending={pending}>{hasPassword ? "Changer" : "Choisir"} le mot de passe</SubmitButton>
    </form>
  );
}

export function DeleteAccountForm({ hasPassword }: { hasPassword: boolean }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setPending(true);
    const deleted = await apiPost("/auth/delete", {
      confirmation: form.get("confirmation"),
      password: form.get("password") ?? "",
    });
    setPending(false);
    if (!deleted.ok) return setError(deleted.error);
    // Session fermée côté serveur : l'accueil se recharge en visiteur.
    router.push("/");
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 border-l-2 border-danger pl-4">
      <p className="text-body">
        Tes données personnelles sont effacées. Tes exercices et solutions restent publiés, sans ton pseudo,
        comme le prévoit leur licence. C&apos;est définitif.
      </p>
      <Field label="Écris SUPPRIMER pour confirmer" htmlFor="confirmation">
        <input id="confirmation" name="confirmation" required autoComplete="off" className={inputClass} />
      </Field>
      {hasPassword && (
        <Field label="Mot de passe" htmlFor="delete_password">
          <input
            id="delete_password"
            name="password"
            type="password"
            required
            autoComplete="current-password"
            className={inputClass}
          />
        </Field>
      )}
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Supprimer mon compte</SubmitButton>
    </form>
  );
}
