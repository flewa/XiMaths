import { Composition } from "remotion";
import { fontsReady, FPS, HEIGHT, WIDTH } from "./theme";
import { calculateMetadata, type VideoProps } from "./timing";
import { VIDEOS } from "./videos";
import { XiVideo } from "./XiVideo";

// Les polices se chargent avant la première image.
void fontsReady;

export function Root() {
  return (
    <>
      {VIDEOS.map((video) => (
        <Composition
          key={video.id}
          id={video.id}
          component={XiVideo}
          width={WIDTH}
          height={HEIGHT}
          fps={FPS}
          durationInFrames={FPS * 30}
          defaultProps={{ videoId: video.id, timings: null, music: null } satisfies VideoProps}
          calculateMetadata={calculateMetadata}
        />
      ))}
    </>
  );
}
