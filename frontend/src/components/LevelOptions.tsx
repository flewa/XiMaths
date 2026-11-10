import type { Level } from "@/lib/api";
import { LEVEL_TRACKS } from "@/lib/labels";

/** Les options d'un menu de niveaux, rangées par famille (université, prépas). */
export function LevelOptions({ levels }: { levels: Level[] }) {
  return LEVEL_TRACKS.map(({ track, label }) => {
    const group = levels.filter((level) => level.track === track);
    if (group.length === 0) return null;
    return (
      <optgroup key={track} label={label}>
        {group.map((level) => (
          <option key={level.code} value={level.code}>
            {level.name}
          </option>
        ))}
      </optgroup>
    );
  });
}
