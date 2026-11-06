import { SITE_URL } from "@/lib/site";

/** Données structurées schema.org, lues par les moteurs de recherche. `<` est échappé :
 * un titre d'exercice ne peut pas fermer la balise script. */
export function JsonLd({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}

/** Fil d'Ariane : [libellé, chemin] du plus général au plus précis. */
export function breadcrumb(items: [string, string][]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map(([name, path], index) => ({
      "@type": "ListItem",
      position: index + 1,
      name,
      item: `${SITE_URL}${path}`,
    })),
  };
}
