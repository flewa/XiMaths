"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import type { AppNotification } from "@/lib/api";
import { apiPost } from "@/lib/client-api";
import { dateFormat, relativeTime } from "@/lib/labels";

import { secondaryButtonClass } from "./Form";

export function NotificationList({ initial, now }: { initial: AppNotification[]; now: string }) {
  const router = useRouter();
  const [items, setItems] = useState(initial);
  const unread = items.filter((item) => !item.read).length;

  async function markAllRead() {
    const result = await apiPost("/notifications/read");
    if (result.ok) {
      setItems(items.map((item) => ({ ...item, read: true })));
      router.refresh();
    }
  }

  if (items.length === 0) {
    return <p className="mt-6 text-body">Rien pour l&apos;instant.</p>;
  }
  return (
    <>
      {unread > 0 && (
        <button type="button" onClick={markAllRead} className={`mt-6 ${secondaryButtonClass}`}>
          Tout marquer comme lu
        </button>
      )}
      <ul className="mt-6 divide-y divide-hairline border-y border-hairline">
        {items.map((item) => (
          <li key={item.id} className={item.read ? "" : "bg-surface-soft"}>
            <Link
              href={item.url || "#"}
              onClick={() => {
                if (!item.read) void apiPost(`/notifications/${item.id}/read`);
              }}
              className="block px-2 py-3 hover:bg-surface-card"
            >
              <span className="flex gap-2">
                <span className={`shrink-0 ${item.read ? "text-stone" : "font-bold"}`}>{item.read ? "[ ]" : "[•]"}</span>
                <span>
                  <span className={item.read ? "" : "font-bold"}>{item.title}</span>
                  {item.body && <span className="block whitespace-pre-line text-sm text-body">{item.body}</span>}
                  <time
                    dateTime={item.created_at}
                    title={dateFormat.format(new Date(item.created_at))}
                    className="block text-sm text-mute"
                  >
                    {relativeTime(item.created_at, now)}
                  </time>
                </span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
