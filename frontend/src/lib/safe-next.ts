/** Seules les adresses internes sont acceptées comme destination après connexion ou inscription :
 * « //exemple.com » mènerait hors du site. */
export function safeNext(next: string | undefined) {
  return next && next.startsWith("/") && !next.startsWith("//") ? next : "/";
}
