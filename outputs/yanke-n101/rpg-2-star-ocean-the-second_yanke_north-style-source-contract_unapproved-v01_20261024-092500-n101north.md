# Yanke north static v01: bounded style/source contract (UNAPPROVED)

Task `content.char.yanke.static-north` (batch101, owner `claude`, 2 frozen task-map points). Written before
authoring. Production contract only; no art approval, no runtime adoption, no motion claim, no score transition.

## Base and scope

- Tested base revision: `f8e628c6e568cd6c1f724038432472df1dc34f46` (Yanke south and west source packages committed;
  north task still `todo`).
- Dependency `content.char.yanke.static-south` is done. West is a sibling source reference, not a substitute.
- Write scope: `game/assets/characters/yanke-native-v01/north/`, `outputs/yanke-n101/`,
  `tools/*yanke*north*`, `docs/qa/*yanke*north*`. Shared ledger, Bible, registry, Git index and defaults are not
  touched by this producer.
- Canonical meters are coordinator-owned and not read or edited here; the task map value is 2 points (frozen).
  This note claims no score transition.

## Inherited source contract (unchanged from Yanke south v01)

- Canvas 80x112, opaque body rows 8..103 (96 source px at density 2), display scale 0.5 = **48 logical px**.
  Pivot (40,104), inside the row-103 feet span.
- Binary alpha, transparent 1-px border, hidden `guides` layer, declared palette <=40 entries and 24..48 used
  colours.
- 12 visible role layers plus guides, same names/order/outlines as south: `hammer, boots, trousers, shirt, apron,
  harness, grip, belt, arms, face, hair, beard`.
- Same Jiang/Lin `finish` outline pass and male v8pair PNG/PXO/ORA serializers, imported from the hash-pinned
  Yanke south author. Reused tool pins and the south package bytes are verified unchanged.
- `isolated_texels <= 24`, all six identity colour families visible, >=8 genuine visible role layers, each anchor
  layer (`hammer, grip, harness, trousers, apron, hair, beard, face`) >=12 visible texels, steel tool mass >=120,
  frontal stocky shoulder span >=34 source px. The south `face_has_eye` gate is replaced for north by
  `north_face_no_eyes_or_mouth` (declared, not a silent weakening): a back view must not paint a front face.

## North is a true back view, not a mirror

North means the character faces away from the camera: the viewer sees the back of the head/hair, ears, nape, back
of the shirt and harness, seat of the trousers, heels and soles. There is **no painted front face** (no eyes, nose
or mouth) and the raster is **not** a horizontal mirror of west or south. The independent checker rejects:

- any eye/iris/mouth colour in the composite or the `face` layer;
- an alpha silhouette within 400 texels of south, west, mirrored south or mirrored west;
- a `face` layer that is not skin-only ears/nape;
- a manifest that is not `content.char.yanke.static-north` / direction `north`.

## Identity and view decisions (Bible character-07, concept UNAPPROVED)

| anchor | north visibility |
| --- | --- |
| hair | short dark-brown curls read as a full back-of-head mass with upper-left sheen, right-side shadow and curl lumps; nape tapered over the neck |
| beard | thick beard peeks as short side tufts below the ears on both jaw edges; no moustache/mouth is painted |
| face | ears plus nape skin only; no eyes, nose, mouth or front cheek plane |
| shirt | cream work shirt across the broad back, shoulder seam, centre back seam and rolled sleeves |
| apron | olive work apron side skirts peek beyond the hips, with a tied bow and tails at the centre back below the belt |
| harness | two broad leather shoulder straps down the back with a horizontal back strap, central brass ring and brass buckles |
| belt | broad leather belt, belt loops, side brass fitting, red work rag at the character's RIGHT hip (screen right in a back view) |
| trousers | dark-brown baggy trousers: seat, centre seat seam, two back patch pockets, olive side-knee patch edges, cuffed hems |
| boots | heavy leather boots from behind: cuffs, heel counters, brass outer buckles, thick soles |
| tool | notched heavy steel head slung over the character's RIGHT shoulder (screen right, above the shoulder); wooden handle runs diagonally across the back to the character's LEFT hip (screen lower left), passing behind the belt with a leather wrap and brass ferrule |
| arms | both arms down at the sides: cream rolled sleeves, bare forearms, leather bracers, relaxed fists |

## Required evidence

- Author `build`/`check`: deterministic rebuild, stage/disk equals rebuild, all reused pins, south/west packages
  unchanged, north-not-mirror and no-front-face gates.
- Independent checker that does not import the author: retained south checks adapted to north, zero-eye/zero-mouth
  proof, back-only `face` layer, not-south/west-or-mirror controls, corrupt-hash, tampered-PNG and wrong-direction
  controls.
- Fresh Pixelorama PXO/ORA flat and split-layer export equality with source bytes unchanged; application
  diagnostic cleanliness reported separately and honestly (inherited diagnostics retained).
- Four EN/ZH city/ruins test-only source-fit captures through the existing generic fit harness and checked Godot
  runner with Dummy audio at 640x360, `runtimeAdopted:false`, `artApproved:false`.
- Fresh staging under `outputs/yanke-n101/north/`; installation only via `python3 tools/wb_safe_replace.py` with
  hash-verified metadata-preserved backups if different bytes already exist.
