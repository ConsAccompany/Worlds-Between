# Female protagonist west static: produced native candidate

Task **content.char.protagonist-female.static-west**, 2-point production milestone only. Canonical ledger at base `86e0c54` had west/east todo and south/north already produced, so this does not duplicate the north milestone. `work/max0840-male` was clean at `5693ab6`; its old branch was preserved and a new `codex/female-west-static-v01-20261018` branch started at canonical `86e0c54`. Completed 2026-10-18T17:48:58-04:00 by Codex under creator authorization during the Max quota gap. No Claude/model calls, cloud credits or paid fallback.

## Scope and construction

One west-facing exploration **static frame**, **80x112 native source**, pivot **(40,104)**, body rows **8..103**, **48 logical pixels at 0.5 scale**, **binary alpha**, **27 colors, all an exact subset of approved south v8**. Visible bounds **[24,8,58,103]**, 2,273 opaque source texels. No other direction, animation, battle pose, runtime default, ledger or Site change.

The left-facing profile was authored from explicit coordinate clusters in new named role layers. No south geometry/texel positions were copied, mirrored, sheared or resampled. South v8 was decoded only for the unchanged source lock and palette verification, and viewed along with the existing female identity sheet as the reference. This preserves the high ponytail, brown hair, teal scarf/bedroll, storm-slate coat, cream cuff, spruce trousers, warm leather boots/pack/straps and metal canister language.

New profile proposals, not creator-approved canon: visible left nose/chin/ear and one eye; a thin high ponytail arc with free strands; rear pack with a foreshortened roll end; character-left canister on the near side; far-side scarf-tail glimpse; a relaxed near arm. No new gear was added. The frame is a static construction toward one complete heroine set and does not establish fluid motion.

## Editable source

The tracked north/v8 native-container writers are reused unchanged for format serialization and their source hashes are recorded. West export metadata is replaced explicitly so its PXO never retains a north-facing filename. Package contains **12 named visible role layers plus one hidden locked guide** in PXO, and the same named layers plus hidden guide in ORA. PNG, PXO, ORA and manifest remain under `outputs/female-west-static-v01`, not wired into a scene or registry.

Actual independent Pixelorama 1.2.3 headless processes reopened copied PXO and ORA with fresh APPDATA and LOCALAPPDATA. Every visible native exported layer matches its authored pixels; guide is excluded. No user editor window was selected or stopped. GUI Save As/re-saving was not tested and is not claimed.

**13/13 source/native gates passed**: current author/container hashes; approved v8 lock; artifact hashes; deterministic PNG reconstruction; cell/body/pivot/binary alpha; exact approved palette subset; exact PXO role cells/hidden locked guide; exact ORA layers/hidden guide; both actual native role exports. Native report: `outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-static-native-report_v01_20261018-174659-24062cc3.json`.

## Actual gameplay captures

The real bright city and dark public-facilities room 2 are each captured in Chinese and English. Only the test harness hides the placeholder and injects the new source Sprite2D at its existing ground pin; original scene/source files remain unchanged against the base Git objects. There are **12 separate captures**, not a collage: per scene/language, west native640, west1280, and approved south reference640. Reference captures are identified in filenames and report; they are not west candidates.

**14/14 capture checks passed**. Every native640 frame shows a **48-pixel** body at the same floor row with the placeholder hidden. Each 1280 frame shows **all 2,273/2,273 source texels exactly** (35x96 on-screen source bounds), proving the 2x source is displayed losslessly at the normal doubled window scale. The 640 native views and 1280 displays remain separate evidence. No glow, added outline, shadow, interpolation or scene makeover is used. No motion quality claim.

The first attempt revealed a stale Godot class cache after the clean branch switch. A normal editor import rebuilt the cache; the final capture run is clean, with no SCRIPT ERROR/ERROR/FAIL lines. A report-only NumPy boolean serialization issue in the native checker was corrected to built-in bools before its final clean run. No visual or test thresholds were widened.

Root independently viewed the actual native640 bright/dark captures and judged the west nose/chin, teal neck band, coat/boot separation and rear pack readable at gameplay scale. The thin high hair arc remains a proposed profile interpretation. This is acceptance as a **produced candidate for source review**, not creator art approval, a complete sprite set or motion approval.

## Reproduction and integrity

Author/build: `tools/rpg-2-star-ocean-the-second_protagonist-female_west-static-native-build-check_unapproved-v01_20261018-174421-618816ac.py`.
Native source/export check: `tools/rpg-2-star-ocean-the-second_protagonist-female_west-static-native-roundtrip-check_v01_20261018-174624-46045523.py`.
Real gameplay capture: `tools/rpg-2-star-ocean-the-second_protagonist-female_west-static-gameplay-capture_test-only-v01_20261018-174530-2c40ca51.gd`.
Final evidence check: `tools/rpg-2-star-ocean-the-second_protagonist-female_west-static-evidence-check_v01_20261018-174810-7be0f9a0.py`.

Use Godot 4.7.2, import after a fresh checkout, redirect APPDATA/LOCALAPPDATA to a new isolated profile, then run the capture script windowed with a fresh absolute output directory after `--`. The final evidence checker verifies current source hashes, the actual native report hash, PNG/PXO/ORA hashes, approved v8 lock, unchanged scene-source base hashes and every saved gameplay capture hash/fidelity record. Text source hashes use sha256-text-lf-v1; binary artwork/captures use raw SHA256; exact-byte JSON/text evidence is pinned LF across Windows checkouts.

Full accepted runtime sprites remain **0/52**. Accepted scene visuals remain **3/12** and human post-art plays **0/2**. Creator approval remains pending; root owns serialized integration, production credit and any review/approval ledger updates.
