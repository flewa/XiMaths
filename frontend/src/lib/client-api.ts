// Appels d'écriture depuis le navigateur, via le proxy /api du front.
// Django exige l'en-tête X-CSRFToken, recopié du cookie csrftoken.

export type ApiResult<T> =
  | { ok: true; data: T }
  /** body : la réponse JSON de l'erreur, quand elle porte plus qu'un message. */
  | { ok: false; status: number; error: string; body?: unknown };

const FIELD_LABELS: Record<string, string> = {
  username: "pseudo",
  email: "email",
  password: "mot de passe",
  title: "titre",
  statement: "énoncé",
  difficulty: "difficulté",
  body: "solution",
  feedback: "commentaire",
  note: "ce qui change",
};

function readCookie(name: string) {
  return document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(`${name}=`))
    ?.slice(name.length + 1);
}

async function csrfToken() {
  if (!readCookie("csrftoken")) {
    await fetch("/api/auth/csrf", { credentials: "same-origin" });
  }
  return readCookie("csrftoken") ?? "";
}

function errorMessage(status: number, body: unknown) {
  if (status === 429) return "Trop de tentatives : réessaie dans quelques minutes.";
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // Erreurs de validation de Django Ninja : [{ loc: [..., "champ"], msg }]
    const fields = detail.map((error: { loc: string[] }) => {
      const field = error.loc.at(-1) ?? "";
      return FIELD_LABELS[field] ?? field;
    });
    return `Vérifie ces champs : ${[...new Set(fields)].join(", ")}.`;
  }
  return "Une erreur est survenue. Réessaie.";
}

async function apiRequest<T>(method: string, path: string, body?: unknown): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`/api${path}`, {
      method,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": await csrfToken() },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!response.ok) {
      // Réponse sans JSON : message générique.
      const errorBody = await response.json().catch(() => null);
      return {
        ok: false,
        status: response.status,
        error: errorMessage(response.status, errorBody),
        body: errorBody,
      };
    }
    const data = response.status === 204 ? undefined : await response.json();
    return { ok: true, data: data as T };
  } catch {
    return { ok: false, status: 0, error: "Le serveur ne répond pas. Réessaie." };
  }
}

export function apiPost<T = unknown>(path: string, body?: unknown) {
  return apiRequest<T>("POST", path, body);
}

export function apiPut<T = unknown>(path: string, body: unknown) {
  return apiRequest<T>("PUT", path, body);
}
