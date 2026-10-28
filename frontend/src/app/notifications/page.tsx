import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { ApiUnavailable, logApiError } from "@/components/ExerciseMeta";
import { NotificationList } from "@/components/NotificationList";
import { fetchNotifications } from "@/lib/api";

export const metadata: Metadata = { title: "Notifications", robots: { index: false } };

export default async function NotificationsPage() {
  let data;
  try {
    data = await fetchNotifications();
  } catch (error) {
    logApiError(error);
    return <ApiUnavailable />;
  }
  if (!data) redirect("/connexion?suivant=/notifications");
  return (
    <div className="max-w-[720px]">
      <h1>Notifications</h1>
      <p className="mt-2 text-body">
        Seulement ce qui te concerne. Les emails se règlent dans les{" "}
        <Link href="/reglages" className="underline underline-offset-4">
          réglages
        </Link>
        .
      </p>
      <NotificationList initial={data.items} now={new Date().toISOString()} />
    </div>
  );
}
