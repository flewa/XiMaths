"use client";

import { useEffect } from "react";

import { SEEN_COOKIE } from "@/lib/site";

/** Note que l'explication de cette page a été vue : à la visite suivante, elle sera repliée. */
export function MarkSeen({ id }: { id: string }) {
  useEffect(() => {
    const current = document.cookie
      .split("; ")
      .find((part) => part.startsWith(`${SEEN_COOKIE}=`))
      ?.slice(SEEN_COOKIE.length + 1);
    const ids = new Set((current ? decodeURIComponent(current) : "").split(".").filter(Boolean));
    if (ids.has(id)) return;
    ids.add(id);
    document.cookie = `${SEEN_COOKIE}=${encodeURIComponent([...ids].join("."))}; path=/; max-age=31536000; samesite=lax`;
  }, [id]);
  return null;
}
