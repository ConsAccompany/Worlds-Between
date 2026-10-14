# Premium exploration asset validator · usage and schema · M8 v01

**Status:** this is a tooling note. The validator is read-only: it writes no files and changes no manifest, registry, runtime script or approval field. A pass means only that the automated metadata and pixel checks passed. It does **not** mean the art is acceptable, and it does not move any registry stage. Only the user can grant art acceptance (see §9 of the [asset intake checklist](rpg-2-star-ocean-the-second_character-visuals_asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md)). No production manifest exists yet, so the schema below is a **proposal**. The pilot frame count is still the proposal from the [feasibility review](rpg-2-star-ocean-the-second_exploration-walk-pipeline_feasibility-review_m8-v01_20261014-163221-c4e19a7d.md), and the production frame count has not been decided.

- Tool: `tools/rpg-2-star-ocean-the-second_premium-exploration-asset-validator_m8-v01_20261014-164502-c988a0a6.py`
- Tests: `tests/premium-exploration-validator/rpg-2-star-ocean-the-second_premium-exploration-asset-validator_tests_m8-v01_20261014-164502-91f41578.py`
- Dependency: Pillow only.

## Command

```
python -B tools/rpg-2-star-ocean-the-second_premium-exploration-asset-validator_m8-v01_20261014-164502-c988a0a6.py <manifest.json> [more manifests] [--format text|json] [--repo-root DIR] [--registry FILE]
```

- `--registry` defaults to the M8 visual registry (`game/data/character-visuals/…2a5d1b3c.json`).
- The report goes to stdout. To save it, redirect stdout to a file outside `game/`.
- Exit codes:
  - `0`: every automated check passed.
  - `1`: at least one check failed. This includes a missing or malformed manifest or registry.
  - `2`: usage error.

Run the tests:

```
python -B tests/premium-exploration-validator/rpg-2-star-ocean-the-second_premium-exploration-asset-validator_tests_m8-v01_20261014-164502-91f41578.py
```

## Manifest schema (one visual variant per manifest)

```json
{
  "schema_version": 1,
  "project": "rpg-2-star-ocean-the-second",
  "visual_id": "protagonist-female",
  "frame_counts": {"idle": {"south": 4, "west": 4, "north": 4, "east": 4},
                   "walk": {"south": 8, "west": 8, "north": 8, "east": 8}},
  "master": {"path": "game/assets/…_<stamp>-<id>.png", "sha256": "<64 hex>"},
  "scale": 0.5,
  "cell_size": [80, 112],
  "ground_pin": [40, 104],
  "frames": [{
    "visual_id": "protagonist-female", "action": "walk", "direction": "south", "phase": 1,
    "path": "game/assets/characters/…/rpg-2-star-ocean-the-second_protagonist-female_premium-walk-south-phase-01_m8-pilot-v01_20261015-101500-1a2b3c4d.png",
    "sha256": "<64 hex>", "source_size": [80, 112],
    "alpha_bounds_inclusive": [27, 9, 52, 104], "alpha_threshold": 64,
    "contact_points": [{"foot": "left", "point": [36, 104]}],
    "west_authoring": null, "identity_reference": "outputs/…png",
    "stage": "generated-concept", "review_receipt": null
  }]
}
```

The numbers in the example (4 + 8 frames, an 80×112 cell, pin (40,104)) are the pilot proposal and are only examples. The validator reads `frame_counts` from each manifest and accepts any positive count. It never assumes 20 or 48.

## Failures (automated)

- **Manifest structure**
  - The manifest is not strict JSON. Duplicate keys and NaN/Infinity count as malformed.
  - A required top-level or frame field is missing, or has the wrong type.
  - `schema_version` is not 1, or `project` is not the project slug.
- **`frame_counts`**
  - It is missing (no default is assumed).
  - It lacks `idle` or `walk`. Extra actions are allowed.
  - Any action is missing one of the four directions, or has a direction other than those four.
  - A count is not a positive integer.
- **Frames vs declared counts**
  - A frame is missing, duplicated, extra or undeclared.
  - Phases are not contiguous: they must run 1..N, and a single-frame set uses phase 0.
- **Variant-level fields**
  - `master`, `scale`, `cell_size` or `ground_pin` is missing or malformed.
  - The pin lies outside the cell.
  - A frame carries its own `scale`, `cell_size`, `ground_pin`, `anchor`, `pin`, `offset`, `pivot`, `origin` or `foot_anchor*`.
  - Two manifests in one run declare the same `visual_id`.
- **Paths**
  - A frame or master path is not repository-relative with forward slashes, or contains `.` or `..`.
  - The path is not under `game/assets/`, resolves outside it, does not exist, or differs in letter case from the file on disk.
  - `identity_reference`, or a non-null `review_receipt`, does not exist inside the repository.
- **Names**
  - A frame filename does not match `rpg-2-star-ocean-the-second_<visual-id>_<kind>-<action>-<direction>[-phase-NN]_<milestone-version>_<YYYYMMDD-HHMMSS>-<8 lowercase hex>.png`.
  - The `visual_id`, action, direction or phase in the name disagrees with the record.
  - The timestamp is not a valid date and time.
  - Two paths in a run share a filename.
  - The frame's or master's 8-hex ID is used by any other file in the repository. Godot `.import`/`.uid` sidecars are ignored. The scan skips `.git`, `work`, `.godot`, `__pycache__`, `.playwright-cli` and `node_modules`.
- **Hash**
  - `sha256` is not 64 hex characters in a single case, or does not match the file (frame or master).
- **Pixels**
  - The file is not a PNG by signature and decoder.
  - The PNG is multi-frame (APNG).
  - The mode is not `RGBA`.
  - The size differs from `source_size` or from `cell_size`.
  - Any corner pixel has alpha above 0.
  - No pixel reaches `alpha_threshold`. The threshold must be an integer from 1 to 255, and a pixel counts as visible when its alpha is at least the threshold.
  - The measured alpha bounds differ from `alpha_bounds_inclusive`.
- **Contact points**
  - `contact_points` is not a list of exactly `{"foot": "left"|"right", "point": [x, y]}`, or lists a foot twice.
  - A point lies outside the cell.
- **Authoring and approval**
  - A west frame lacks `west_authoring` set to `independent` or `mirrored_east`.
  - The manifest has an `approval`, `approved`, `approval_status`, `art_approval` or `review_status` key at any depth.
  - `stage` is empty, or contains approval wording (approve, accept, sign-off, 验收, 批准, 通过).
  - The visual registry is missing or unreadable, `visual_id` is not in it, or its `direction_order` is not south/west/north/east.

## Reported facts and warnings (never failures)

- Per frame:
  - format, mode and size;
  - corner alpha;
  - opaque and partial-alpha pixel counts;
  - low-alpha pixels below the threshold;
  - pixels with alpha above 0 on the cell border;
  - measured alpha bounds and their height;
  - contact points, with the alpha value under each point.
- Per action and direction:
  - frames found;
  - alpha-bounds height range;
  - visible height in logical px (bounds height × `scale`);
  - contact feet by phase.

  The approved display height is 48 logical px, but the tolerance is undecided, so this height is reported and not judged.
- West vs east: whether each west frame is a pixel-exact mirror of the matching east frame. This is a warning that needs user acceptance, including when `west_authoring` disagrees with the pixels.
- Warnings are also given when:
  - frames have identical file content;
  - `identity_reference` differs from the registry `source_portrait`;
  - a manifest filename does not follow the naming rule.

## Limitations

- These pixel checks are not run, because the schema has no layer masks or pose table for them:
  - locked-layer identity (M1);
  - accessory ownership (M2);
  - torso registration (M3);
  - palette subset (M7);
  - turn consistency (M8).
- Gait plausibility, foot sliding and runtime snapping (M5, M9) need engine capture.
- Identity, direction fidelity, and halos on light or dark ground need human review.
- A combined image is caught only when its size differs from `cell_size`, or when it is multi-frame. A collage drawn inside a single cell-sized canvas cannot be detected.
- Mirror detection is exact-pixel only. A near-mirror that has been lightly edited is reported as not mirrored.
- Interpretations of the checklist, to be confirmed:
  - A single-frame action may omit the phase token or use `phase-01`, while its record says phase 0.
  - The master must live under `game/assets/`.
  - Approval wording in `stage` is detected with a keyword list, so false positives are possible.
- The registry is read but never updated. Stage progression and the batch gate stay manual.
- Existing repository files already share some IDs (for example, five `outputs/` files use `6e24b8a1`). Such a shared ID is reported only when a manifest's frame or master uses it.
- No existing manifest follows this schema. A smoke run on the Liang Xu concept manifest and the Liang Xu native animation manifest failed as expected, with missing `frame_counts`, `master`, `scale`, `cell_size`, `ground_pin` and other fields.
