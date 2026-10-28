import { Audio } from "@remotion/media";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { Fragment } from "react";
import type { ReactNode } from "react";
import { AbsoluteFill, staticFile, useCurrentFrame } from "remotion";
import { Backdrop } from "./components/Backdrop";
import { Captions } from "./components/Captions";
import { Phone } from "./components/Phone";
import { zoomFade } from "./components/zoomFade";
import { Goal, Leaderboard, Skills } from "./scenes/Boards";
import { Chat, Chips, Cta } from "./scenes/Cards";
import { Handwriting } from "./scenes/Handwriting";
import { Proof } from "./scenes/Proof";
import { Reviewers } from "./scenes/Reviewers";
import { StreakBreak, Weeks } from "./scenes/Streak";
import { Timer } from "./scenes/Timer";
import { Title } from "./scenes/Title";
import { ACCENTS } from "./theme";
import { sceneFrames, TRANSITION, type VideoProps } from "./timing";
import { VIDEOS, type Visual } from "./videos";

function SceneVisual({
  visual,
  duration,
  first,
  continued,
}: {
  visual: Visual;
  duration: number;
  first: boolean;
  continued: boolean;
}) {
  switch (visual.kind) {
    case "title":
      return (
        <Title text={visual.text} kicker={visual.kicker} accent={visual.accent} size={visual.size} instant={first} />
      );
    case "phone":
      return (
        <Phone
          shot={visual.shot}
          focus={visual.focus}
          label={visual.label}
          tap={visual.tap}
          accent={ACCENTS.green}
          continued={continued}
        />
      );
    case "reviewers":
      return <Reviewers title={visual.title} verdicts={visual.verdicts} continued={continued} />;
    case "timer":
      return <Timer minutes={visual.minutes} label={visual.label} extra={visual.extra} instant={first} />;
    case "proof":
      return (
        <Proof
          headline={visual.headline}
          title={visual.title}
          lines={visual.lines}
          marks={visual.marks}
          stamp={visual.stamp}
          instant={first}
        />
      );
    case "handwriting":
      return <Handwriting lines={visual.lines} source={visual.source} preview={visual.preview} />;
    case "streakBreak":
      return <StreakBreak days={visual.days} duration={duration} />;
    case "weeks":
      return <Weeks mode={visual.mode} />;
    case "skills":
      return <Skills chapters={visual.chapters} next={visual.next} />;
    case "chat":
      return <Chat text={visual.text} verdict={visual.verdict} duration={duration} instant={first} />;
    case "leaderboard":
      return <Leaderboard rows={visual.rows} duration={duration} instant={first} />;
    case "goal":
      return (
        <Goal
          title={visual.title}
          done={visual.done}
          target={visual.target}
          deadline={visual.deadline}
          continued={continued}
        />
      );
    case "chips":
      return (
        <Chips
          title={visual.title}
          items={visual.items}
          accent={visual.accent}
          marks={visual.marks}
          colors={visual.colors}
        />
      );
    case "cta":
      return <Cta prompt={visual.prompt} line={visual.line} />;
  }
}

/** Poussée lente de la caméra pendant toute la scène : rien n'est jamais tout à fait figé. */
function Drift({ duration, children }: { duration: number; children: ReactNode }) {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ transform: `scale(${1 + (0.035 * frame) / duration})`, transformOrigin: "50% 42%" }}>
      {children}
    </AbsoluteFill>
  );
}

export function XiVideo({ videoId, timings, music }: VideoProps) {
  const video = VIDEOS.find((candidate) => candidate.id === videoId);
  if (!video || !timings) return null;
  return (
    <AbsoluteFill>
      <Backdrop />
      <TransitionSeries>
        {video.scenes.map((scene, index) => {
          const timing = timings[index];
          const duration = sceneFrames(timing);
          const captions = scene.captions ?? (scene.visual.kind !== "title" && scene.visual.kind !== "cta");
          const timingIn = linearTiming({ durationInFrames: TRANSITION });
          // Deux scènes de même nature se suivent : la seconde prolonge la première.
          const continued = index > 0 && video.scenes[index - 1].visual.kind === scene.visual.kind;
          return (
            <Fragment key={index}>
              {/* Une suite se fond dans la scène d'avant ; un écran de téléphone arrive par le bas ;
                  le reste se succède en fondu zoomé. */}
              {index > 0 &&
                (continued ? (
                  <TransitionSeries.Transition presentation={fade()} timing={timingIn} />
                ) : scene.visual.kind === "phone" ? (
                  <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timingIn} />
                ) : (
                  <TransitionSeries.Transition presentation={zoomFade()} timing={timingIn} />
                ))}
              <TransitionSeries.Sequence durationInFrames={duration} name={`${index + 1}. ${scene.visual.kind}`}>
                <AbsoluteFill>
                  <Drift duration={duration}>
                    <SceneVisual visual={scene.visual} duration={duration} first={index === 0} continued={continued} />
                  </Drift>
                  {captions && <Captions words={timing.words} />}
                  {timing.audio && <Audio src={staticFile(timing.audio)} />}
                </AbsoluteFill>
              </TransitionSeries.Sequence>
            </Fragment>
          );
        })}
      </TransitionSeries>
      {music && <Audio src={staticFile(music)} volume={0.12} loop />}
    </AbsoluteFill>
  );
}
