import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";
import { AbsoluteFill } from "remotion";

type Props = Record<string, never>;

/** La scène qui part grossit et s'efface ; celle qui arrive se pose en grandissant un peu. */
function ZoomFade({
  children,
  presentationDirection,
  presentationProgress,
}: TransitionPresentationComponentProps<Props>) {
  const entering = presentationDirection === "entering";
  const scale = entering ? 0.9 + 0.1 * presentationProgress : 1 + 0.15 * presentationProgress;
  const opacity = entering ? presentationProgress : 1 - presentationProgress;
  return <AbsoluteFill style={{ transform: `scale(${scale})`, opacity }}>{children}</AbsoluteFill>;
}

export const zoomFade = (): TransitionPresentation<Props> => ({ component: ZoomFade, props: {} });
