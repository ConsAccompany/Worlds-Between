"""Build the Godot preload registry from native animation manifests."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = {
    "protagonist-male": "rpg-2-star-ocean-the-second_protagonist-male_native-animation-manifest_m8-v01_20261014-141005-29a4674f.json",
    "protagonist-female": "rpg-2-star-ocean-the-second_protagonist-female_native-animation-manifest_m8-prototype_20261014-140955-d7d64ca7.json",
    "liang-xu": "rpg-2-star-ocean-the-second_liang-xu_native-animation-manifest_m8-v01_20261014-181000-c09d742e.json",
    "zhao-ling": "rpg-2-star-ocean-the-second_zhao-ling_native-exploration-manifest_m8-v01_20261014-142000-b123903c.json",
    "ji-cheng": "rpg-2-star-ocean-the-second_ji-cheng_native-exploration-manifest_m8-prototype_20261014-142157-a4836b01.json",
}
ANIMATION_DIR = ROOT / "game" / "assets" / "characters" / "native-animation"
OUTPUT = ROOT / "game" / "scripts" / "character_directional_motion.gd"
DIRECTIONS = ("south", "west", "north", "east")


def main() -> None:
    lines = [
        "extends RefCounted",
        "",
        "# Generated from native-animation manifests. These are prototypes, not accepted art.",
        "const TEXTURES := {",
    ]
    for character_id, manifest_name in MANIFESTS.items():
        manifest = json.loads((ANIMATION_DIR / manifest_name).read_text(encoding="utf-8"))
        frames = manifest["frames"]
        expected_count = 19 if character_id in ("protagonist-male", "protagonist-female", "liang-xu") else 20
        assert len(frames) == expected_count, (character_id, len(frames))
        indexed = {(f["action"], f["direction"], int(f["phase"])): f for f in frames}
        assert len(indexed) == len(frames), character_id
        lines.append(f'\t"{character_id}": {{')
        actions = ("walk", "attack", "hit") if expected_count == 19 else ("walk",)
        for action in actions:
            lines.append(f'\t\t"{action}": {{')
            for direction in DIRECTIONS if action == "walk" else ("south",):
                phase_count = 4 if action == "walk" else (2 if action == "attack" else 1)
                paths = []
                for phase in range(1, phase_count + 1):
                    frame = indexed[(action, direction, phase)]
                    path = Path(frame["path"])
                    assert path.parts[:2] == ("game", "assets"), path
                    assert (ROOT / path).is_file(), path
                    resource_path = "res://" + path.relative_to("game").as_posix()
                    paths.append(f'preload("{resource_path}")')
                lines.append(f'\t\t\t"{direction}": [{", ".join(paths)}],')
            lines.append("\t\t},")
        lines.append("\t},")
    lines += [
        "}",
        "",
        "",
        "static func texture_for(character_id: String, action: String, direction: String, phase: int = 1) -> Texture2D:",
        "\tvar actions: Dictionary = TEXTURES.get(character_id, {})",
        "\tvar directions: Dictionary = actions.get(action, {})",
        "\tvar frames: Array = directions.get(direction, [])",
        "\tif phase < 1 or phase > frames.size():",
        "\t\treturn null",
        "\treturn frames[phase - 1] as Texture2D",
        "",
    ]
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {sum(19 if character_id in ('protagonist-male', 'protagonist-female', 'liang-xu') else 16 for character_id in MANIFESTS)} separate frame preloads")


if __name__ == "__main__":
    main()
