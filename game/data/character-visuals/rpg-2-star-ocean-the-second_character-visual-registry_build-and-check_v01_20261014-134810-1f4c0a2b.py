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
        "south": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_exploration-sprite-south_m8-draft_20261014-133644-a01be730.png",
        "north": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-male_exploration-sprite-north_m8-draft_20261014-133644-d04e0b63.png",
    },
    "protagonist-female": {
        "south": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_protagonist-female_exploration-sprite-south_m8-draft_20261014-133644-b02ce841.png",
    },
    "liang-xu": {
        "south": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-sprite-south_m8-draft_20261014-133644-c03dfa52.png",
        "north": "game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-sprite-north_m8-draft_20261014-133644-e05f1c74.png",
    },
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
                    "production_status": "directional_draft" if visual_id in SAMPLES else "not_started",
                    "review_status": "pending",
                    "directions": SAMPLES.get(visual_id, {}),
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
    print(f"visual variants={len(entries)} approved source={approval_counts['approved']} concept source={approval_counts['concept']} draft directions={sum(len(e['exploration']['directions']) for e in entries)}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("registry source and sample files: PASS")


if __name__ == "__main__":
    main()
