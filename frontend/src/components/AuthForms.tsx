"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import type { Level } from "@/lib/api";
import { apiPost } from "@/lib/client-api";

import { Field, FormMessage, SubmitButton, inputClass, secondaryButtonClass } from "./Form";

export function LoginForm({ next }: { next: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setPending(true);
    const result = await apiPost("/auth/login", {
      login: form.get("login"),
      password: form.get("password"),
    });
    setPending(false);
    if (!result.ok) return setError(result.error);
    router.push(next);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Pseudo ou email" htmlFor="login">
        <input id="login" name="login" required autoComplete="username" className={inputClass} />
      </Field>
      <Field label="Mot de passe" htmlFor="password">
        <input
          id="password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
          className={inputClass}
        />
      </Field>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Se connecter</SubmitButton>
      <p className="space-x-4 text-sm text-mute">
        <Link href="/mot-de-passe-oublie" className="underline underline-offset-4">
          Mot de passe oublié ?
        </Link>
        <Link href="/inscription" className="underline underline-offset-4">
          Créer un compte
        </Link>
      </p>
    </form>
  );
}

/** Lien vers la connexion Google : une simple navigation, le serveur fait l'aller-retour. */
export function GoogleButton({ next }: { next: string }) {
  return (
    <a href={`/api/auth/google/start?next=${encodeURIComponent(next)}`} className={`${secondaryButtonClass} text-center`}>
      [G] Continuer avec Google
    </a>
  );
}

export function ForgotPasswordForm() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const result = await apiPost("/auth/password-reset", { email: new FormData(event.currentTarget).get("email") });
    setPending(false);
    if (result.ok) setSent(true);
    else setError(result.error);
  }

  if (sent) {
    return (
      <FormMessage success="Si un compte existe avec cette adresse, un lien vient d'y être envoyé. Il est valable 3 jours." />
    );
  }
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Adresse email" htmlFor="email">
        <input id="email" name="email" type="email" required autoComplete="email" className={inputClass} />
      </Field>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Recevoir un lien</SubmitButton>
    </form>
  );
}

export function ResetPasswordForm({ uid, token }: { uid: string; token: string }) {
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    const result = await apiPost("/auth/password-reset/confirm", {
      uid,
      token,
      password: new FormData(event.currentTarget).get("password"),
    });
    setPending(false);
    if (result.ok) setDone(true);
    else setError(result.error);
  }

  if (done) {
    return (
      <div className="space-y-4">
        <FormMessage success="Mot de passe changé." />
        <Link href="/connexion" className="underline underline-offset-4">
          Se connecter
        </Link>
      </div>
    );
  }
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Nouveau mot de passe" htmlFor="password" hint="8 caractères au moins ; une phrase est plus sûre qu'un mot.">
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          className={inputClass}
        />
      </Field>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Changer le mot de passe</SubmitButton>
    </form>
  );
}

export function SignupForm({ levels }: { levels: Level[] }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setPending(true);
    const result = await apiPost("/auth/signup", {
      username: form.get("username"),
      email: form.get("email"),
      password: form.get("password"),
      declared_level: form.get("declared_level") || null,
    });
    setPending(false);
    if (!result.ok) return setError(result.error);
    router.push("/");
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Pseudo" htmlFor="username" hint="Public. Lettres, chiffres, points et tirets.">
        <input
          id="username"
          name="username"
          required
          minLength={3}
          maxLength={30}
          pattern="[\w.\-]+"
          autoComplete="username"
          className={inputClass}
        />
      </Field>
      <Field label="Email" htmlFor="email" hint="Jamais affiché. Un lien de confirmation t'y sera envoyé.">
        <input id="email" name="email" type="email" required autoComplete="email" className={inputClass} />
      </Field>
      <Field label="Mot de passe" htmlFor="password" hint="8 caractères au moins.">
        <input
          id="password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          className={inputClass}
        />
      </Field>
      <Field label="Ton niveau" htmlFor="declared_level" hint="Sert à te proposer des exercices et des relectures.">
        <select id="declared_level" name="declared_level" defaultValue="" className={inputClass}>
          <option value="">Je préfère ne pas le dire</option>
          {levels.map((level) => (
            <option key={level.code} value={level.code}>
              {level.name}
            </option>
          ))}
        </select>
      </Field>
      <FormMessage error={error} />
      <SubmitButton pending={pending}>Créer mon compte</SubmitButton>
      <p className="text-sm text-mute">
        Déjà inscrit ?{" "}
        <Link href="/connexion" className="underline underline-offset-4">
          Se connecter
        </Link>
      </p>
    </form>
  );
}

const VERIFICATIONS = {
  principale: { path: "/auth/verify-email", success: "Adresse confirmée : tu peux publier, résoudre et voter." },
  academique: {
    path: "/auth/academic/verify",
    success: "Adresse académique confirmée : le badge « Étudiant vérifié » apparaît sur ton profil.",
  },
};

export function VerifyEmail({ token, kind = "principale" }: { token: string; kind?: keyof typeof VERIFICATIONS }) {
  const router = useRouter();
  const [state, setState] = useState<{ ok: boolean; message: string } | null>(null);
  const sent = useRef(false);

  useEffect(() => {
    // Un seul envoi, même quand React monte l'effet deux fois en développement.
    if (sent.current) return;
    sent.current = true;
    const { path, success } = VERIFICATIONS[kind];
    apiPost(path, { token }).then((result) => {
      setState(result.ok ? { ok: true, message: success } : { ok: false, message: result.error });
      if (result.ok) router.refresh();
    });
  }, [token, kind, router]);

  if (!state) return <p className="text-mute">Vérification en cours…</p>;
  return (
    <div className="space-y-4">
      <FormMessage error={state.ok ? null : state.message} success={state.ok ? state.message : null} />
      <Link href="/" className="text-sm underline underline-offset-4">
        Voir les exercices
      </Link>
    </div>
  );
}
