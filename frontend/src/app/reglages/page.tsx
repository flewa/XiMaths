import type { Metadata } from "next";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ProseSection } from "@/components/Prose";
import { DeleteAccountForm, PasswordForm, PreferencesForm, ThemeChoice } from "@/components/Settings";
import { fetchLevels, fetchMe } from "@/lib/api";
import { THEME_COOKIE, type Theme } from "@/lib/site";

export const metadata: Metadata = { title: "Réglages", robots: { index: false } };

export default async function SettingsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchLevels()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, levels] = data;
  if (!me) redirect("/connexion?suivant=/reglages");
  const theme = ((await cookies()).get(THEME_COOKIE)?.value ?? "system") as Theme;

  return (
    <div className="max-w-[640px]">
      <h1>Réglages</h1>
      <p className="mt-2 text-body">
        {me.username} · {me.email}
        {me.google_linked && <span className="text-mute"> · compte Google lié</span>}
      </p>

      <ProseSection title="Préférences">
        <PreferencesForm me={me} levels={levels} />
      </ProseSection>

      <ProseSection title="Apparence">
        <ThemeChoice current={theme} />
      </ProseSection>

      <ProseSection title="Mot de passe">
        <PasswordForm hasPassword={me.has_password} />
      </ProseSection>

      <ProseSection title="Mes données">
        <p>
          Toutes tes données (compte, contributions, points, sessions) dans un fichier JSON, lisible et
          réutilisable.
        </p>
        <p>
          <a href="/api/auth/export" download className="underline underline-offset-4">
            [↓] Télécharger mes données
          </a>
        </p>
      </ProseSection>

      <ProseSection title="Supprimer mon compte">
        <DeleteAccountForm hasPassword={me.has_password} />
      </ProseSection>
    </div>
  );
}
