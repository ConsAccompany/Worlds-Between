# Lin Que four-direction static sources — producer QA note (UNAPPROVED v01)

Run `20261022-222500-3d61c74e`, base `0d44b398648abbbcfb3483dd4df4a7966511f7ea`. Producer: Claude. Status: **UNAPPROVED**. This is source production only: no runtime wiring, no animation, no default adoption, no art approval.

## Author tool

`tools/rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py`
raw sha256 `0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82`

- `build` writes new files only and refuses to overwrite different bytes. `check` rebuilds each direction twice in memory and compares the result with the files on disk.
- It reuses the Jiang south v01 author (L pen, compose, gates, outline rule) and, through it, the male v8pair PNG/PXO/ORA serializers. Jiang's palette and layer globals are rebound in memory only. The Jiang tool is hash-pinned at `35005f3c…a599db69b4`, and no Jiang file is written.
- The concept sheet `outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png` (sha256 `24007e14…de7fb352`) was used as an identity reference only. No pixels were sampled from it.

## Outputs

`game/assets/characters/lin-que-native-v01/{south,west,north,east}/` holds the native PNG, layered PXO, layered ORA, palette JSON and manifest for each direction. The folder root holds the batch manifest `…four-direction-batch-manifest…-a6ff0b1b.json` and a `.gdignore`. Raw hashes are listed in `outputs/lin58d/claude/…four-direction-output-paths-rawhashes…-04f4b712.json`. The four separate ×6 previews are QA-only files, not sources. Codex removed the unrequested combined preview and its author block; static source pixels are unchanged and were rebuilt/checked.

The manifest schema copies the Jiang directions keys: actor_id, content_id `content.char.lin-que.static-DIR`, direction, status, canvas [80,112], pivot [40,104], body_rows [8,103], display_scale 0.5, logical_height_px 48, portrait_ref and files png/pxo/ora/palette → {file, rawsha256}. `south_baseline.preserved_byte_exact` is `null` because this is the first Lin Que set.

## Producer checks (author `check` exit 0, `LIN_QUE_FOUR_DIRECTION_V01_ALL_OK`)

| dir | colours | genuine visible role layers (≥12 texels) | body rows | hard failures |
|---|---|---|---|---|
| south | 36 | 11 | 8..103 | none |
| west | 36 | 11 | 8..103 | none |
| north | 30 | 11 | 8..103 | none |
| east | 35 | 11 | 8..103 | none |

Every direction passed the inherited Jiang hard gates: binary alpha, transparent border, pin inside the feet span, all colours declared, PNG decode equals compose, ORA mimetype first and stored, ORA/PXO recompose equals PNG, PXO layer names, no male or Jiang PXO metadata, guides hidden with no overlap, and a deterministic rebuild. North has no eye or mouth colours in its face layer, and the other three directions do. East differs from mirrored west by 930 texels (the gate requires ≥200).

There are 11 role layers (cape, boots, trousers, coat, belt, arms, firearm, face, scarf, hair, goggles) plus hidden `guides`.

## Authored asymmetry

- **South:** the holster and firearm are on the character's right hip (screen left). The scarf knot and tail are on the character's left. There is a chest pocket on the right.
- **East:** shows the holster with a silver slide, black grip and thigh strap, plus a sideburn and a short scarf tail on the far side.
- **West:** shows the long scarf tail streaming back, a pouch, the gun grip peeking out behind the back, and a longer nape.
- **North:** the cape covers the back and carries a pale diamond motif and a trimmed hem. It also shows the goggle-strap buckle, layered nape spikes and the scarf tail on screen left.

## Not done / limitations

- The independent checker (`…lin-que_native-static-verify…`, present in the tree and not authored here) was **not** invoked. Native app (Pixelorama) open and Godot import/runtime verification belong to the coordinator and were not run.
- Self-review at ×4 shows these known weaknesses for creator or follow-up review:
  - The hair mass reads somewhat helmet-like, with too little layered spike breakup at the crown and sides.
  - The cape flare is barely visible in south and side views.
  - The firearm is small at native scale.
  - The side-view torso is narrow.
- There are no idle or walk frames, and no default adoption. Creator art approval has not been given.
- No Git, ledger, Bible, registry or default edits were made.
