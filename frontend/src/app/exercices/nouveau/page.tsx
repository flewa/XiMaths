import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { ExerciseForm } from "@/components/ExerciseForm";
import { VerifyEmailNotice } from "@/components/AccountControls";
import { fetchLevels, fetchMe, fetchTopics } from "@/lib/api";

export const metadata: Metadata = { title: "Publier un exercice" };

export default async function NewExercisePage() {
  let data;
  try {
    data = await Promise.all([fetchMe(), fetchLevels(), fetchTopics()]);
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  const [me, levels, topics] = data;
  if (!me) redirect("/connexion?suivant=/exercices/nouveau");

  return (
    <>
      <h1>Publier un exercice</h1>
      <p className="mt-2 text-body">
        +5 points quand un autre membre le résout pour la première fois, puis +3 pour chaque nouveau membre qui le
        résout.
      </p>
      <div className="mt-6">
        {me.email_verified ? (
          <ExerciseForm levels={levels} topics={topics} defaultLevel={me.declared_level} />
        ) : (
          <VerifyEmailNotice email={me.email} action="publier un exercice" />
        )}
      </div>
    </>
  );
}
