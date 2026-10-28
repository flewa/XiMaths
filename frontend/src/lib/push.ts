/** Clé VAPID publique (base64 « url », sans remplissage) en octets, pour pushManager.subscribe. */
export function base64UrlToBytes(value: string) {
  const base64 = (value + "=".repeat((4 - (value.length % 4)) % 4)).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i += 1) bytes[i] = raw.charCodeAt(i);
  return bytes;
}

/** Mêmes octets ? Pour comparer la clé d'un abonnement existant à celle du serveur. */
export function sameBytes(a: ArrayBuffer | null, b: Uint8Array) {
  if (a === null || a.byteLength !== b.length) return false;
  const bytes = new Uint8Array(a);
  return bytes.every((value, index) => value === b[index]);
}

/** iPhone et iPad, iPadOS compris, qui se présente comme un Mac tactile. */
export function isAppleMobile(userAgent: string, platform: string, maxTouchPoints: number) {
  return /iPad|iPhone|iPod/.test(userAgent) || (platform === "MacIntel" && maxTouchPoints > 1);
}
