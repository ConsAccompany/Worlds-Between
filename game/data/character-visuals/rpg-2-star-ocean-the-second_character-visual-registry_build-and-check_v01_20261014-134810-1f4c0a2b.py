"""Build and validate a source-aware visual registry without approving artwork."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name(
    "rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json"
)
INVENTORY = ROOT / "outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json"
CORE_HAIR = ROOT / "outputs/rpg-2-star-ocean-the-second_core-cast_hairstyle-manifest_v02_20261013-161317-4f5a6c7d.md"
REMAINING = ROOT / "outputs/rpg-2-star-ocean-the-second_remaining-companions_character-sheet-manifest_v01_20261013-194808-b6d7ee1d.md"

SAMPLES = {
    "protagonist-male": {
        "south": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-south_m8-v01_20261014-135316-4438515e.png",
        "west": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-west_m8-v01_20261014-135316-2d359882.png",
        "north": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-north_m8-v01_20261014-135316-2fa1bb39.png",
        "east": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-east_m8-v01_20261014-135316-a23d4672.png",
    },
    "protagonist-female": {
        "south": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-south_m8-prototype_20261014-135400-3bacea6e.png",
        "west": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-west_m8-prototype_20261014-135400-b023f47c.png",
        "north": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-north_m8-prototype_20261014-135400-daa6122c.png",
        "east": "game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-female_native-idle-east_m8-prototype_20261014-135400-39d3f522.png",
    },
    "liang-xu": {
        "south": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-south_m8-v03_20261014-175132-e17b4c09.png",
        "west": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-west_m8-v03_20261014-175132-b52910e1.png",
        "north": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-north_m8-v03_20261014-175132-c742d602.png",
        "east": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-east_m8-v03_20261014-175132-d853a711.png",
    },
}
MOTION_MANIFESTS = {
    "protagonist-male": "game/assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-animation-manifest_m8-v01_20261014-141005-29a4674f.json",
    "protagonist-female": "game/assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-animation-manifest_m8-prototype_20261014-140955-d7d64ca7.json",
    "liang-xu": "game/assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-manifest_m8-v01_20261014-181000-c09d742e.json",
}


def markdown_rows(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| 角色") or line.startswith("| 编号"):
            continue
        cells = [value.strip() for value in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    characters = next(category for category in inventory["categories"] if category["id"] == "characters")
    portraits = next(group for group in characters["subcategories"] if group["id"] == "portraits")["items"]
    core_hair = {row[0]: row[1] for row in markdown_rows(CORE_HAIR) if len(row) >= 2}
    rest = {int(row[0]): row for row in markdown_rows(REMAINING) if len(row) >= 5 and row[0].isdigit()}
    motion = {visual_id: json.loads((ROOT / path).read_text(encoding="utf-8")) for visual_id, path in MOTION_MANIFESTS.items()}

    entries = []
    for ordinal, portrait in enumerate(portraits):
        visual_id = portrait["id"].removeprefix("portrait.")
        name = portrait["name"].split(" · ", 1)[0]
        source = "outputs/" + Path(portrait["file"]).name
        companion_number = ordinal - 1 if ordinal >= 2 else None
        if ordinal < 2:
            roster = "protagonist"
        elif ordinal <= 16:
            roster = "main"
        elif ordinal <= 31:
            roster = "side"
        else:
            roster = "situational"
        if companion_number is not None and companion_number >= 16:
            identity_note = rest[companion_number][3]
        else:
            identity_note = core_hair.get(name, "Source sheet needs visual review")
        entries.append(
            {
                "visual_id": visual_id,
                "companion_number": companion_number,
                "display_name_zh": name,
                "roster": roster,
                "region": portrait["board"],
                "identity_and_hair_anchor": identity_note,
                "source_portrait": {
                    "path": source,
                    "approval": portrait["stage"],
                    "exists": (ROOT / source).is_file(),
                },
                "exploration": {
                    "production_status": ("four_direction_native_walk_integrated" if visual_id.startswith("protagonist-") else "four_direction_native_walk_authored") if visual_id in SAMPLES else "not_started",
                    "review_status": "pending_motion_and_art_approval" if visual_id in SAMPLES else "pending",
                    "directions": SAMPLES.get(visual_id, {}),
                    **({"idle_frames": 4, "walk_frames": 16, "required_frames": 20, "walk_manifest": MOTION_MANIFESTS[visual_id]} if visual_id in SAMPLES else {}),
                },
                "runtime_display": {"production_status": "not_started", "review_status": "pending"},
                "combat": {"production_status": "not_started", "review_status": "pending"},
            }
        )

    approval_counts = {state: sum(item["source_portrait"]["approval"] == state for item in entries) for state in ("approved", "concept")}
    result = {
        "schema_version": 1,
        "scope": "protagonist male/female visual variants plus 50 companions",
        "source_of_truth": INVENTORY.relative_to(ROOT).as_posix(),
        "direction_order": ["south", "west", "north", "east"],
        "counts": {"visual_variants": len(entries), "approved_source_portraits": approval_counts["approved"], "concept_source_portraits": approval_counts["concept"]},
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failures = []
    if len(entries) != 52 or approval_counts != {"approved": 9, "concept": 43}:
        failures.append(f"unexpected roster/approval totals: {len(entries)}, {approval_counts}")
    if len({item["visual_id"] for item in entries}) != 52:
        failures.append("duplicate visual IDs")
    for item in entries:
        if not item["source_portrait"]["exists"]:
            failures.append("missing source " + item["source_portrait"]["path"])
        for direction, asset in item["exploration"]["directions"].items():
            if direction not in result["direction_order"] or not (ROOT / asset).is_file():
                failures.append(f"invalid direction sample {item['visual_id']} {direction}: {asset}")
    for visual_id, manifest in motion.items():
        frames = manifest["frames"]
        walks = {(f["direction"], int(f["phase"])) for f in frames if f["action"] == "walk"}
        if len(walks) != 16 or len(frames) != 19:
            failures.append(f"incomplete native motion {visual_id}")
        for frame in frames:
            if not (ROOT / frame["path"]).is_file():
                failures.append(f"missing native frame {frame['path']}")
    print(f"visual variants={len(entries)} approved source={approval_counts['approved']} concept source={approval_counts['concept']} native idle directions={sum(len(e['exploration']['directions']) for e in entries)} native walk frames={sum(e['exploration'].get('walk_frames', 0) for e in entries)}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("registry source and sample files: PASS")


if __name__ == "__main__":
    main()
