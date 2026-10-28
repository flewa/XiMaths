// Service worker de XiMaths : notifications push seulement, sans cache hors ligne,
// pour ne jamais servir une page périmée. Il est enregistré depuis /reglages.

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch {
    data = {};
  }
  event.waitUntil(
    self.registration.showNotification(data.title || "XiMaths", {
      body: data.body || "",
      icon: "/icons/icon-192.png",
      badge: "/icons/badge-96.png",
      lang: "fr",
      // Une notification remplace la précédente au lieu de s'empiler.
      tag: "ximaths",
      data: { url: data.url || "/notifications" },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL(event.notification.data?.url || "/notifications", self.location.origin);
  // Seulement des pages du site.
  if (target.origin !== self.location.origin) return;
  event.waitUntil(
    (async () => {
      const windows = await self.clients.matchAll({ type: "window" });
      for (const client of windows) {
        try {
          await client.focus();
          await client.navigate(target.href);
          return;
        } catch {
          // Fenêtre qui n'est pas contrôlée par ce service worker : on en ouvre une autre.
        }
      }
      await self.clients.openWindow(target.href);
    })(),
  );
});
