# Male protagonist south idle, high-density static pilot v02: QA note

Status: **UNAPPROVED, NONRUNTIME.** This is one bounded refinement of the v01 south-facing exploration idle still at the approved 48 logical px. It is not wired into the game, has no animation and covers no other direction. Counters do not change: runtime sprites **0/52**, scene visuals **3/12**, overall meter **40.8%**. v01 is unchanged and stays available for comparison. Nothing was staged, committed or pushed. No Game Bible, progress, runtime or shared file was edited.

Session check (2026-10-17): `claude auth status` reported `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. No quota or auth error occurred. No paid API, credits or image generation were used.

## What was read

- Global `~/.codex/AGENTS.md` naming: `[project-slug]_[character-or-area]_[asset-purpose]_[episode-or-variant]_[YYYYMMDD-HHMMSS]-[unique-id].[ext]`.
- `git status`.
- The v02 dispatch `docs/coordination/…protagonist-male_south-idle-hd-static-v02-visual-fix-dispatch_v01_20261017-032100-9ab467d0.md`.
- The v01 QA note (`…qa-note_unapproved-nonruntime-v01_20261017-030935-6f26047a.md`).
- The four v01 bright and dark Godot captures (`…unapproved-v01_20261017-071541-bb1bc7e3.png`), viewed at 1:1 and x2/x3.
- The approved female selout v8 PNG (`ccf9d2a2…`).
- The male identity sheet `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png`.

## Resumed work (interrupted session)

An earlier session started v02 at 03:37 local and stopped before any capture or QA note. It left:
- a build tool;
- a built draft (PNG `ff5f4d9a…`, 42×96, 2550 texels).

I checked that draft before changing anything: its own `check` passed, and v01 matched the hashes the earlier session had recorded. I then captured it in real Godot. At 1:1 the bedroll end and a detached steel canteen floated off his right shoulder with no pack between them, so the pack still did not read as a pack.

I made one targeted fix: a leather pack body behind the viewer-right arm, described below. Everything else from the draft was kept. I re-stamped the tool and assets to 20261017-160419. The draft tool, assets and first captures were moved (not deleted) to `%TEMP%\wb-male-v02\superseded-draft-033736\`, with a `sha256.txt`. They are not shipped.

## What changed from v01 (one coherent pass)

| v01 review point | v02 change |
| --- | --- |
| Pack/bedroll not distinct; scarf and bedroll merge into one teal neck patch | The bedroll is now slate-teal (bluer and darker than the scarf; scarf `s` vs bedroll `t` ΔE76 31.4). It has a spiral end and sits over the viewer-right shoulder, as in the sheet's front view. Under it, a **brown leather pack body** shows behind the viewer-right arm: a lit top band, a flap with a strap and steel buckle, and a flap shadow line. A steel canteen is strapped to the pack's outer side, and a pack corner shows behind the left shoulder. The 2-texel harness straps run down the chest. Scarf/bedroll 4-neighbour contacts: **0**, minimum gap 3 px. Pack: 142 texels. |
| Teal neck patch | The scarf is now a compact wrap inside a dark stand collar with a short front point (83 texels; v01 had 104). |
| Weak dark-room contrast | The coat is darker (charcoal-brown) and the trousers cooler (olive-grey). The lit planes stay on the left. |
| Narrow, lanky read | The visible width goes from 32 px to **42 px** (v8: 43). The extra width comes from gear and an A-stance (relaxed leg out, left boot turned out), not from scaling. The adult proportions and 96-texel height are unchanged. |
| Rigid coat skirt | The skirt now flares, with one fold per panel, leather inner edges, a stitched hem trim and an angled hem. The back panel shows between the legs. |
| "Two horns" hair | The crown is broad and uneven with small tufts and no tall corner spikes. It has outward temple flicks, partings and highlight strokes. Hair is 31 px wide against a 14 px face, and the tool finds 5 small crown points. It stays short and wide, clearly not her ponytail. |
| Sparse micro detail | Added buttons, eyelets, buckles, a stitched hem and cloth specks. Isolated single texels: 39 → **80** (v8: 145). |

The face, both arms and the lower-torso clusters are carried over from v01 unchanged.

## Files (all new, untracked)

| File | sha256 |
| --- | --- |
| Runtime-candidate PNG `game/assets/characters/protagonist-male/south-idle-high-density-static-pilot-unapproved-v02/rpg-2-star-ocean-the-second_protagonist-male_south-idle-high-density-static-pilot_unapproved-v02_20261017-160419-d61ac77e.png` (80×112, binary alpha) | `667972e4f09c238554786dc7fc31b9100021a50f9c1c7e8da339b13f51041555` |
| Pixelorama `…static-pilot-editable_unapproved-v02_20261017-160419-b50d5763.pxo` (pxo v7, 14 role layers + hidden locked guides) | `47ce5fea983e39aa0fe4abc68abd545943b821bbaa01231396fc6ecdfc28ba08` |
| OpenRaster `…static-pilot-editable-layers_unapproved-v02_20261017-160419-e3f07c16.ora` | `01fdb4dec1c335d4a7893efc7ad549ea7afeaacc3c059c883eab9b2d10d0a58b` |
| Palette `…-palette_unapproved-v02_20261017-160419-ef5463a0.json` | sha256-text-lf-v1 `a94e9c9b1863e21921d10025ec2cda4700538d4fcfca1ec8069a9e915d066b5e` (LF, equals raw) |
| Manifest `…-manifest_unapproved-v02_20261017-160419-d5863708.json` | sha256-text-lf-v1 `19a4702600ec04515e1e3efbd142a86612cd9df134bff33ddf40abc6ff32f7a1` |
| `.gdignore` (same folder) | empty |
| Build/check tool `tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-high-density-static-pilot-build-and-check_unapproved-v02_20261017-160419-b2b36e92.py` | `f8c89c481cf5cbb1329297fe42cca400d11f544977b5974eaf73b52729301ea1` |
| Godot capture tool `tools/…static-pilot-godot-capture_unapproved-v02_20261017-160419-5c0e83d1.gd` | `76b8f2f5a276a5312c5e162470c628eaedb6839fe8798cd6d1cc60766bcdddbb` |
| x4 nearest preview `outputs/rpg-2-star-ocean-the-second_protagonist-male_south-idle-hd-static-pilot-x4-nearest-preview_unapproved-v02_20261017-160419-4a009931.png` | `d7bc59fc26c3bfceb831132feee11771dda8262a4a8c6f4945e591acd69a1964` |

Layers, bottom to top: coat-back, pack, bedroll, legs, boots, coat-skirt, torso-coat, harness, sash, arm-hip, arm-hanging, head-face, hair, scarf, guides. The guides layer is hidden and locked: #ff00ff border, ticks on rows 8 and 103, and the pin. The literal 56×96 `MAP`/`ROLE` grids in the tool are the only source. No image generation, resampling, filtering, quantization or dithering was used, and no v8 texel or palette entry was copied.

## Technical evidence

`python -I -B <tool> check` ended with **PASS** (exit 0). It covered:

- **Rebuild:** the PNG, .pxo, .ora and palette are byte-equal to a fresh, deterministic rebuild. The manifest file hashes and all 12 reference locks are current, and the PNG decodes exactly to the grids.
- **Hard gates:**
  - binary alpha;
  - transparent border;
  - **39 colours** (cap 48; v8 has 32), all declared, none unused;
  - visible body **42×96**, cell rows 8–103: 96 texels, which is 48 logical px at 0.5. Alpha bounds x 22–63.
  - sole on row 103, pin (40,104) inside the feet span. This is the same cell, pin and sole as v01.
- **Layers:** the 14 role layers do not overlap and reassemble the sprite exactly.
- **.ora structure:**
  - the mimetype entry comes first and is stored;
  - only the guides layer is hidden;
  - the visible layers recompose to the PNG;
  - each layer equals its role blob;
  - mergedimage equals the PNG.
- **Pixelorama 1.2.3 CLI, for both .pxo and .ora:**
  - two flattened exports, each RGBA-equal to the PNG and byte-identical to the other;
  - split-layers 14/14 exact, guides not exported;
  - inputs left unchanged.
  - Every run used its own temporary `APPDATA`. In the real `%APPDATA%\pixelorama`, only `.running` changed. That is the heartbeat of another session's open GUI, which I left alone.
- **v01 unchanged:** the 7 v01 asset and tool locks match. I also checked separately, with `sha256sum`, the v01 captures, report, preview and QA note against the hashes recorded before this work started. All are unchanged.
- **P4 ramp steps (reported only, not a hard gate):** minimum adjacent L\* step 7.43 (coat C→c), with B→C at 7.92. These are below v01 (9.31) and v8 (11.87). See flaw 2.

**Godot 4.7.2 windowed capture** (`--path game -s <abs tool path>`, exit 0).

- Settings: 640×360 canvas, canvas_items, 1280×720 window, sprite scale 0.5, nearest, no shadow.
- Scenes and spot: the same as v01, v8 and Liang (hero placeholder x+36), with `hero_appearance = "male"`.
- Placement: v02 is placed by its foot pin (cell x 40), because the gear makes its alpha bounds asymmetric. v8 keeps its reviewed bounds-centred placement.
- Gates passed:
  - SHA locks for the v02, v8 and v01 PNGs;
  - v02 window **42×96** at 1:1, (734,412) in the city and (228,428) in the annex;
  - texel fidelity 2618/2618;
  - v8 43×96, fidelity 2419/2419, not touching the v02 window.
- v01 measurement: v01 was also drawn at the same pin spot in an extra, unsaved frame (32×96, 2336/2336) and measured on the same backdrop. Its numbers reproduce the v01 report exactly.
- Side effects: `git status` before and after the run differs only by the five outputs below.

| Capture (all `outputs/`, 1280×720) | sha256 |
| --- | --- |
| `rpg-2-star-ocean-the-second_protagonist-male_south-idle-hd-static-pilot-city-bright-h48_unapproved-v02_20261017-160532-94d51b35.png` | `9b643f3529e7d44d7ddc99f9be799d35b517a2ef4520646132f1c0ad4b448082` |
| `…south-idle-hd-static-pilot-with-female-v8-city-bright-h48_unapproved-v02_20261017-160532-94d51b35.png` | `266ad5cc9d65876505cbff014e5f884328c57b6218652b7a93955dcb1768c4fd` |
| `…south-idle-hd-static-pilot-survey-annex-room2-dark-h48_unapproved-v02_20261017-160532-94d51b35.png` | `35ce6380bdcc9f4662254e2acdba6115a6eaebefa75e3559c856371a15a3d854` |
| `…south-idle-hd-static-pilot-with-female-v8-survey-annex-room2-dark-h48_unapproved-v02_20261017-160532-94d51b35.png` | `1e4afe915f415b859009ab68da24d413a95dd105c63992a4c599ce01c05dadc4` |
| Report `…south-idle-hd-static-pilot-city-bright-annex-dark-capture-report_unapproved-v02_20261017-160532-94d51b35.json` | `8adf0c0007c0606a477094e315927b0601b639e371dd45ac7bc964ebabe285f1` |

Capture stamps are local time (Godot run at 16:05:32). The v01 capture stamps were UTC.

Contrast against the 8 px ring median, ΔE76 mean (min in brackets where relevant). The v01 and v8 figures were measured in the same run and on the same backdrop.

| Region | City v01 | City **v02** | Annex v01 | Annex **v02** |
| --- | --- | --- | --- | --- |
| Whole figure | 34.1 (3.8) | **38.8** (2.7) | 25.0 (8.4) | **27.9** (11.9) |
| v8 whole figure (benchmark) | 43.9 | 43.9 | 30.1 (6.9) | 30.1 (6.9) |
| Hair | 33.8 | 37.4 | 17.1 | 19.4 |
| Face skin | 29.3 | 28.5 | 42.6 | 43.5 |
| Scarf | 37.3 | 37.8 | 45.2 | 44.5 |
| Bedroll | 33.9 | 39.9 | 30.2 | 32.3 |
| Pack leather (new) | – | 30.9 | – | 20.9 |
| Canteen metal (new) | – | 22.7 | – | 26.8 |
| Coat | 25.4 | 38.5 | **12.9** | **22.7** |
| Shirt | 21.8 (3.6) | 20.6 (2.7) | 40.3 | 40.0 |
| Trousers | 25.5 | 34.0 | **13.1** | **19.4** |
| Boots | 32.3 | 31.6 | 18.7 | 18.6 |

## Visual judgement (mine; not approval)

At normal 1280×720 size he now reads as a traveller carrying a backpack. A blue-teal bedroll sits on a brown pack behind his right shoulder, with a steel canteen on its side. That makes him distinct both from the runtime placeholder and from the heroine, whose ponytail and longer blue coat stay the dominant cues on her side. The scarf reads as a scarf and no longer as a teal collar. The hair reads as short, tousled and wide, with no horns. His width now matches hers (42 vs 43) without bulking up his body. In the dark annex, the coat and trousers separate from the floor clearly better than in v01 (coat ΔE 12.9 → 22.7). His whole-figure contrast moves closer to v8 in both scenes, and his darkest-texel minimum in the annex is better than v8's.

## Remaining flaws (candid)

1. **The dark room is still below v8.** Hair (19.4), boots (18.6), trousers (19.4) and pack leather (20.9) still depend on the 1-texel ink against the warm floor. Below the face, scarf and shirt he reads as a dark silhouette. His whole figure is 27.9 against v8's 30.1.
2. **Coat ramp too compressed.** The darkest steps (7.4 and 7.9 L\*) are tighter than in v01 or v8, so the coat's shadow panels read as near-flat black at 1:1. The lit left panel carries most of the form. Opening this ramp would cost some dark-room separation.
3. **Shirt in the bright city.** The cream shirt is still close to the pale paving (min ΔE 2.7). Only the coat enclosing it separates it.
4. **Width partly comes from gear.** About 9 px of the 42 px width is pack, bedroll and canteen on the viewer-right side (pin at x 40; the bounds run 18 px left and 23 px right of it). The body itself is still slimmer than hers. He looks slightly right-heavy, which is expected from a one-shoulder pack.
5. **Same-side gear.** Her teal shoulder roll is also on the viewer-right. His differs in colour and shape and follows the sheet, but the creator may still want it checked.
6. **Small details.** The canteen is a 3×7 steel block: at 1:1 it reads as "metal gear", not specifically as a canteen. The emblem and buckles are still at the limit of legibility.
7. **Face and arms are carried over from v01.** The heavy-lidded face can read stern or sleepy at 1:1. This pass did not address it.
8. **Detail and palette versus v8.** Micro detail is still below v8 (80 vs 145 isolated texels). The palette has 39 colours against v8's 32: the canteen metal and the slate bedroll ramp add colours.
9. **Coverage.** This is one static south frame only. No animation, other direction, runtime swap or 1920×1080 sampling was attempted.
10. **Shared tree.** The captures ran on the shared working tree, where `scifi_exploration_area.gd` carries another session's uncommitted opt-in hooks. Those hooks are inactive in the default city plate.

## For Codex and the creator

- Does the backpack (bedroll + pack + canteen) now read at 1280×720?
- Is the darker coat still the sheet's field coat?
- Should the face and arms get their own pass?
- Should the coat ramp be opened up at some cost to the dark room?
