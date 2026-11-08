import type { Metadata } from "next";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ProfileForm } from "@/components/ProfileForm";
import { ProseSection } from "@/components/Prose";
import { PushSettings } from "@/components/PushSettings";
import {
  AcademicEmailForm,
  DeleteAccountForm,
  PasswordForm,
  PreferencesForm,
  ThemeChoice,
} from "@/components/Settings";
import { fetchBadges, fetchLevels, fetchMe, fetchProfileOptions, fetchPushKey, fetchTopics } from "@/lib/api";
import { DEFAULT_THEME, THEME_COOKIE, type Theme } from "@/lib/site";

export const metadata: Metadata = { title: "Réglages", robots: { index: false } };

export default async function SettingsPage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchLevels(), fetchPushKey(), fetchProfileOptions(), fetchBadges(), fetchTopics()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, levels, pushKey, profileOptions, badges, topics] = data;
  if (!me) redirect("/connexion?suivant=/reglages");
  const theme = ((await cookies()).get(THEME_COOKIE)?.value ?? DEFAULT_THEME) as Theme;

  return (
    <div className="max-w-[640px]">
      <h1>Réglages</h1>
      <p className="mt-2 text-body">
        {me.username} · {me.email}
        {me.google_linked && <span className="text-mute"> · compte Google lié</span>}
      </p>

      <section id="profil" className="mt-10 scroll-mt-20">
        <h2>Profil public</h2>
        <p className="mt-2 text-sm text-body">
          Ce que les autres voient sur{" "}
          <a href={`/membres/${encodeURIComponent(me.username)}`} className="underline underline-offset-4">
            ton profil
          </a>{" "}
          et dans les classements.
        </p>
        <div className="mt-5">
          <ProfileForm me={me} options={profileOptions} badges={badges} topics={topics} />
        </div>
      </section>

      <ProseSection title="Préférences">
        <PreferencesForm me={me} levels={levels} />
      </ProseSection>

      {pushKey && (
        <ProseSection title="Notifications sur cet appareil">
          <PushSettings publicKey={pushKey} />
        </ProseSection>
      )}

      <ProseSection title="Apparence">
        <ThemeChoice current={theme} />
      </ProseSection>

      <ProseSection title="Email académique">
        <AcademicEmailForm me={me} />
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
