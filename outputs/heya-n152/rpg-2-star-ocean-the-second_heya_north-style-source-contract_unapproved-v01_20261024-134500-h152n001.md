# Heya north static — style/source contract (UNAPPROVED v01)

Task: `content.char.heya.static-north` (batch 152, producer DeepSeek).
Status: `UNAPPROVED`, `approval=false`, `artApproved=false`, `runtimeAdopted=false`. This is a production
contract, not a creator or art approval.

## Source identity and approval status

- Subject: Heya / 赫娅, Bible character-26 / companion #26, female, 44-year-old clinician who respects a
  patient's bodily autonomy. Restrained patient closed-lip smile; mature, calm presence.
- Canonical anchors: auburn braided coil **LOW at the nape**; cool grey-white **medical scarf**; ivory open
  clinician coat over pale grey-white apron and charcoal underdress; dark-red **emergency bag on the character's
  LEFT**; dark gloves; brown leather boots.
- Identity reference: `outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png`
  (raw sha256 `918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0`), **UNAPPROVED** identity
  reference. Hues are inherited from the committed Heya palette; no pixels are sampled or resampled.
- Continuity sources:
  - south manifest `.../south/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json`
    (raw sha256 `d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c`), committed at `dc8ad3b4`.
  - west manifest `.../west/rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json`
    (raw sha256 `75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752`), closeout at `6d727227`.
  - Same exact 35-entry palette, layer vocabulary, outline rule and serializers; **no pixels are copied,
    mirrored or upscaled**.
- Direction reference: `docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md`
  (Sea of Stars: broad coherent clusters, readable silhouettes, upper-left light, restrained palette).

## North view rules

- North = **rear view**: nose away from camera, so **no eyes, nose or mouth** are drawn. The protected restrained
  patient smile belongs to the character and remains in the south/west views; it is not invented on the back of
  the head.
- Character's **LEFT is SCREEN LEFT** in a true rear view. The dark-red emergency bag therefore sits on the
  screen-left hip; the cross-body strap runs from the screen-right shoulder down across the back to it.
- The auburn braided coil is **centred low at the nape** (rows 24..35), banded and clearly below the crown; the
  35-entry palette's `h1..h4` colours only. Hair crown `h1..h4`, ends by row 32; never a high bun.
- The grey-white medical scarf wraps the neck (rows 34..41) and its long tail falls down the screen-left back to
  row 62, fringed; only `f1..f3`.
- The ivory coat is closed across the back with shoulder yoke and centre seam; a lower back vent reveals the
  charcoal underdress (>=12 texels). The pale apron is worn in front, so only its waist ties, back bow, tails and
  side wrap edges are visible (`v1..v3`).
- Dark-red bag with brass clasps, leather handle and rolled bandage on the screen-left hip; slim leather belt
  with a small medicine pouch at the screen-right back; small herb sprig tucked at the screen-right back waist.
- Both ivory sleeves, pale cuffs and dark gloves are visible from behind; screen-left hand rests on the bag.
  Brown boots seen from behind with folded cuffs, brass eyelets, stacked heels and soles.
- Ears and nape/neck only on the face layer; no `e1/e2/m1` face colours.

## Native geometry and export

- Native canvas 80x112 px; pivot (40,104); body rows 8..103; display scale 0.5 = **48 logical px**.
- Binary alpha, transparent one-pixel border, declared palette (<=40 entries, 24..48 used), >=8 genuine visible
  role layers, hidden `guides` layer.
- Editable layered source: deterministic `.pxo` (Pixelorama) and `.ora` (OpenRaster); flat `.png` composite;
  `.json` palette and manifest with raw sha256 hashes.
- Fresh staging output `outputs/heya-n152/staging/north/`; installation only through `python3
  tools/wb_safe_replace.py` when destination bytes differ (unique verified backups).

## Protected properties and non-goals

- Protected: 44-year-old clinician identity; low auburn braided coil; grey-white scarf; ivory coat/apron/charcoal
  dress; dark-red bag on the character's LEFT; dark gloves/brown boots; exact palette; 80x112 density-2 source,
  48 logical px, pivot (40,104).
- Non-goals: no runtime/default selection, no other characters or directions, no motion, no scoring/ledger edit,
  no GUI save/reopen claim, no native-diagnostic-clean claim, no art approval.

## Completion evidence planned

- Author `preview/build/install/check` with hard gates, deterministic rebuild, south and west packages unchanged,
  and exact palette identity.
- Independent checker (does not import the author) with corrupt-hash, tampered-pixel, visible-guide, wrong-direction
  (eyes added), high-bun, missing-scarf, wrong-hip-bag, hidden-dress and flipped-south controls.
- Native Pixelorama PXO/ORA export equality; application diagnostics reported separately and not claimed clean.
- Checked-runner 640x360 en/zh bright-city and dark-ruins fit captures with Dummy audio at unchanged scale.
- This contract, a QA note under `docs/qa/`, and a raw-hash receipt. Native-diagnostic and GUI-unverified status
  remain separate from exact pixel production credit.
