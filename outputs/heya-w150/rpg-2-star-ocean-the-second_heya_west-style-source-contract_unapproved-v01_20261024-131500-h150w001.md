# Heya west static — style/source contract (UNAPPROVED v01)

Task: `content.char.heya.static-west` (batch 150, producer DeepSeek via the accepted adapter job).
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
  reference. Hues are chosen by eye; no pixels are sampled or resampled.
- Bible identity overrides the sheet's inconsistencies (white head-veil omitted so the low coil stays readable;
  long dark-red shawl reduced to the canonical bag). The sheet is not an approval.
- Continuity source: Heya south v01 manifest
  `game/assets/characters/heya-native-v01/south/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json`
  (raw sha256 `d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c`), committed at `dc8ad3b4`.
  Same palette, layer vocabulary, outline rule and serializer; **no pixels are copied or mirrored**.
- Direction reference: `docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md`
  (Sea of Stars: broad coherent clusters, readable silhouettes, upper-left light, restrained palette).

## Native geometry and export

- Native canvas 80x112 px; pivot (40,104); body rows 8..103; display scale 0.5 = **48 logical px**.
- Binary alpha, transparent one-pixel border, declared palette (<=40 entries, 24..48 used), >=8 genuine visible
  role layers, hidden `guides` layer.
- Editable layered source: deterministic `.pxo` (Pixelorama) and `.ora` (OpenRaster); flat `.png` composite;
  `.json` palette and manifest with raw sha256 hashes.
- Fresh staging output `outputs/heya-w150/staging/west/`; installation only through `python3
  tools/wb_safe_replace.py` when destination bytes differ (unique verified backups).

## West view rules

- West = nose toward **screen LEFT**, so the character's **LEFT side faces the camera**. Reauthored in forward
  coordinates with the Lin Que `P` pen (`s=-1`); not a rotation, squash, recolour or mirror of south.
- One visible hazel eye; level brow; nose leads the face silhouette; ear near the back of the head.
- Low braided coil at the nape reads as one plaited, banded auburn mass behind/below the near ear at the back of
  the head (rows 24..40), never a high bun (hair crown ends by row 30).
- Cool grey-white scarf wraps the neck and streams a long tail **back** so it does not hide the open coat front;
  only scarf colours `f1..f3`.
- The dark-red emergency bag is on the character's LEFT (near) hip, fully visible, with brass hardware; the
  cross-body strap runs from the far/right shoulder to that near hip.
- The open coat front exposes the charcoal underdress placket (4 px) between the ivory lapel and the bag; the
  pale apron and botanical hem motif stay readable. The near left arm, pale cuff and dark glove rest on the bag;
  the far arm is occluded in strict profile.
- The herb sprig is at the character's far right chest, with only its tips protruding past the near front edge
  (explicit readability choice). Brown boots: near boot brown, far boot darker and set slightly ahead.

## Protected properties and non-goals

- Protected: 44-year-old mature face and restrained closed-lip smile; low auburn braided coil; grey-white scarf;
  ivory coat/apron/charcoal dress; dark-red bag on character LEFT; dark gloves/brown boots; 80x112 density-2
  source, 48 logical px, pivot (40,104).
- Non-goals: no runtime/default selection, no other characters or directions, no motion, no scoring/ledger edit,
  no GUI save/reopen claim, no native-diagnostic-clean claim, no art approval.

## Completion evidence planned

- Author `preview/build/install/check` with hard gates, deterministic rebuild, south-package unchanged.
- Independent checker (does not import the author) with corrupt-hash, tampered-pixel, visible-guide,
  wrong-direction, high-bun, missing-scarf, wrong-hip-bag and teeth negative controls.
- Native Pixelorama PXO/ORA export equality; application diagnostics reported separately and not claimed clean.
- Checked-runner 640x360 en/zh bright-city and dark-ruins fit captures with Dummy audio at unchanged scale.
- This contract, a QA note under `docs/qa/`, and a raw-hash receipt. Native-diagnostic and GUI-unverified status
  remain separate from exact pixel production credit.
