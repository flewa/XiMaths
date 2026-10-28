import katex from "katex";
import "katex/dist/katex.min.css";
import { useEffect, useMemo, useState } from "react";
import { continueRender, delayRender } from "remotion";

/** Formule LaTeX rendue par KaTeX, comme sur le site. Le rendu attend ses polices. */
export function Tex({
  latex,
  size,
  color,
  display = false,
}: {
  latex: string;
  size: number;
  color?: string;
  display?: boolean;
}) {
  const html = useMemo(
    () => katex.renderToString(latex, { displayMode: display, throwOnError: false, strict: false }),
    [latex, display],
  );
  const [handle] = useState(() => delayRender(`KaTeX : ${latex}`));
  useEffect(() => {
    document.fonts.ready.then(() => continueRender(handle));
  }, [handle]);
  return <span style={{ fontSize: size, color, lineHeight: 1.25 }} dangerouslySetInnerHTML={{ __html: html }} />;
}
