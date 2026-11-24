import QRCode from "qrcode";

import { SITE_URL } from "@/lib/site";

/** Bas de la version imprimée d'une fiche (et de son PDF) : d'où elle vient, et un QR code
 * qui ramène sur le site. Invisible à l'écran. */
export async function PrintSource({ path, practicePath }: { path: string; practicePath: string | null }) {
  const url = `${SITE_URL}${path}`;
  const qr = await QRCode.toString(url, {
    type: "svg",
    margin: 0,
    errorCorrectionLevel: "M",
    color: { dark: "#111111", light: "#ffffff" },
  });
  const host = SITE_URL.replace(/^https?:\/\//, "");
  return (
    <section aria-hidden="true" className="print-only mt-10 border-t border-hairline-strong pt-5" style={{ breakInside: "avoid" }}>
      <div className="flex items-center gap-5">
        <div className="size-24 shrink-0" dangerouslySetInnerHTML={{ __html: qr }} />
        <div className="text-sm leading-relaxed text-body">
          <p className="font-semibold text-ink-deep">XiMaths : des exercices de maths corrigés par d&apos;autres étudiants</p>
          <p>
            Cette fiche en ligne : <strong>{host}{path}</strong>
          </p>
          {practicePath && (
            <p>
              Des exercices sur ce chapitre : <strong>{host}{practicePath}</strong>
            </p>
          )}
          <p>De la L1 au M2 et en prépa. Gratuit et sans publicité.</p>
        </div>
      </div>
    </section>
  );
}
