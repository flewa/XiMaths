import { pdfPath } from "@/lib/fiches-pdf";

import { smallSecondaryButtonClass } from "./Form";
import { Icon } from "./Icon";

/** « Télécharger en PDF » sous le titre d'une fiche publiée qui a son PDF. */
export function PdfLink({ slug, published }: { slug: string; published: boolean }) {
  const href = pdfPath(slug);
  if (!href || !published) return null;
  return (
    <p className="print-hidden mt-4">
      <a href={href} className={smallSecondaryButtonClass} data-umami-event="fiche-pdf" data-umami-event-fiche={slug}>
        <Icon name="download" size={16} />
        Télécharger en PDF
      </a>
    </p>
  );
}
