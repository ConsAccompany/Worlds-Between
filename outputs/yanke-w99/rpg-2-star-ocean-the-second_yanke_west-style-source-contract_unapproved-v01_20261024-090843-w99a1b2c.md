# Yanke west static v01: bounded style/source contract (UNAPPROVED)

Task `content.char.yanke.static-west`. Written before authoring. Production contract only; no art approval, no runtime adoption, no motion claim.

## Base and task-local starting meters

- Tested base revision: `234cfabeacd48a9ebc80b2608af448feb535af69` (Yanke south committed; task still `todo`, owner `claude`).
- Task-local canonical starting meters supplied by the coordinator: production **62.1%**, content **694/1881**; inspection **21.6%**; creator approval **7.8%**. This producer does not edit the ledger, registry, Bible, index or defaults; no score transition is claimed.

## Inherited source contract (unchanged from Yanke south v01)

- Canvas 80x112, opaque body rows 8..103 (96 source px at density 2), display scale 0.5 = **48 logical px**. Pivot (40,104), inside the row-103 feet span.
- Binary alpha, transparent 1-px border, hidden `guides` layer, declared palette <=40 entries and 24..48 used colours.
- 12 visible role layers plus guides, same names/order and outline colours as south: `hammer, boots, trousers, shirt, apron, harness, grip, belt, arms, face, hair, beard`.
- Same Jiang/Lin `finish` outline pass and male v8pair PNG/PXO/ORA serializers, imported from the hash-pinned Yanke south author.
- `isolated_texels <= 24`, all six identity colour families visible, >=8 genuine visible role layers, each anchor layer (`hammer, grip, harness, trousers, apron, hair, beard, face`) >=12 visible texels, steel tool mass >=120, one visible eye.
- South package must remain byte-identical; the west author checks the south manifest and all reused tool pins.

## West is authored, not mirrored

A character facing west (nose toward screen LEFT) shows the character's **LEFT** side to the south camera. Forward coordinates use the existing Lin `P` pen with `s = -1` (`screen x = 40 - f`), so this is a true profile, not a horizontal flip, squash or recolour of the frontal south source. The independent checker rejects a west image whose alpha silhouette is within 400 texels of south or of mirrored south, and it requires one eye in the profile face.

## Identity and view decisions

| anchor | west visibility |
| --- | --- |
| face | strict profile to screen left: one brown eye, thick brow, nose protruding past the forehead, ear mid-head, cheerful open smile with teeth; broad jaw |
| hair | short dark-brown curls, upper-front sheen, fuller curl volume at the back of the skull; no ponytail |
| beard | thick short beard plus moustache and sideburn wrapping the jaw; mouth kept clear for the smile |
| shirt | cream rolled-sleeve work shirt at collar, chest sliver and near sleeve |
| apron | olive work apron: bib, skirt, stitched pocket on the near/front face, uneven worn hem; near arm may occlude part of it |
| harness | broad leather strap over the near (left) shoulder, front branch and back branch, brass buckle; far strap edge peeks at the back shoulder |
| belt | broad leather belt with front brass buckle; red work rag at the character's RIGHT (far) hip peeks behind at the back hip |
| trousers | dark-brown baggy work trousers; near leg in front, far leg darker and set slightly ahead; olive knee patch on the near knee |
| boots | heavy brown leather boots with cuff, brass buckle, broad toe and thick sole; near boot overlaps the darker far boot |
| tool | notched heavy steel tool head on a wooden handle slung over the character's RIGHT (far) shoulder: the steel head and notch read above/behind the upper back at screen right; the far handle end emerges over the near (left) shoulder at screen front (screen left) |
| near arm | near (left) arm hangs down the front side: cream rolled sleeve, bare forearm, leather bracer, relaxed fist |
| far arm | occluded by the torso |

## Profile gate adaptation (declared, not a silent weakening)

The south hard gate `stocky_shoulders_ge_34` measures frontal shoulder spread and is not meaningful in strict profile. The west author replaces it with `stocky_profile_depth_ge_20`: the composite opaque span at chest rows 38..46 must be >=20 source px deep. Every other south hard gate and threshold is retained unchanged. The independent checker reports both the profile depth and the difference from south / mirrored south explicitly.

## Required evidence

- Author `build`/`check`: deterministic rebuild, disk equals rebuild, all reused pins, south package unchanged, west-not-mirror control.
- Independent checker (does not import the author): retained south checks adapted to west, profile eye count, facing, not-mirror control, corrupt-hash and tampered-PNG controls, plus a malformed-source (wrong-direction manifest) control.
- Fresh Pixelorama PXO/ORA flat and split-layer export equality with source bytes unchanged; application diagnostic cleanliness reported separately and honestly (known inherited errors retained).
- Four EN/ZH city/ruins fit captures through the existing source-fit harness and checked Godot runner with Dummy audio, test-only overlay at 640x360, `runtimeAdopted:false`, `artApproved:false`.
- Fresh staging outputs under `outputs/yanke-w99/`; no replacement of existing bytes is expected because the west package is new. Any differing replacement would go through `tools/wb_safe_replace.py` with hash-verified backups.
