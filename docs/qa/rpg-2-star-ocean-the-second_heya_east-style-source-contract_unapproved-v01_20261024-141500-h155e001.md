# Heya east static — style/source contract (UNAPPROVED v01)

Task: `content.char.heya.static-east` (batch 155, sole producer). Status: `UNAPPROVED`,
`approval=false`, `artApproved=false`, `runtimeAdopted=false`. This is a production contract, not creator
or art approval.

## Source identity and approval status

- Subject: Heya / 赫娅, Bible character-26 / companion #26, female, **44-year-old clinician** who respects a
  patient's bodily autonomy; mature, calm presence, restrained patient closed-lip smile.
- Canonical anchors: auburn **braid LOW at the nape**; cool grey-white **medical scarf**; ivory open clinician
  coat over pale grey-white apron and charcoal underdress; dark-red **emergency bag on the anatomical LEFT
  hip**; dark gloves; brown leather boots; small herb sprig.
- Identity reference: `outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png`
  (raw sha256 `918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0`), **UNAPPROVED** identity
  reference only. No pixels are sampled, mirrored, resampled or upscaled.
- Continuity: committed south, west and north packages; same 35-entry palette, layer vocabulary, outline rule
  and serializers. Their manifests are hash-pinned by the author and independent checker.
- Direction: `docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md`
  (Sea of Stars: broad coherent clusters, readable silhouettes, upper-left light, restrained palette).

## East view rules (not a mirrored west)

- East profile: **nose points screen RIGHT**; the character faces east. The character's **anatomical LEFT is the
  far side**, so the dark-red emergency bag sits on the **far left hip**: a partially exposed dark-red mass behind
  the back hip at screen LEFT with brass clasp, leather handle and rolled bandage. It is deliberately not the
  large near-side bag of the west view.
- **Upper-left lighting on screen is preserved**, so the back plane of head/coat (screen LEFT) is lit (`h1`,
  `w1`, `s1`) and the front plane (screen RIGHT) is shaded (`h3`, `w3`, `s3`). A horizontal mirror of west would
  move the highlight to the right and is rejected by a semantic gate.
- Mature 44-year-old face: one hazel eye, level brow, nose leading right, ear behind, restrained closed-lip
  smile (3–6 `m1` texels, no teeth), cheek/jaw/nasolabial shading. Face layer width <=20 px, rows 15..33.
- Auburn braid: one plaited coil **LOW at the nape**, behind/below the far ear at screen LEFT (rows 23..40,
  mean x <=37, min x <=30), alternating `h1`/`h3` bands and an `h4` tie; never a high bun (hair ends by row 30).
- Grey-white scarf: wrap at rows 33..41 with a knot at the near front (screen RIGHT) and the long tail down the
  far back (screen LEFT) to row >=52, fringed; only `f1..f3`.
- Ivory coat: open front with the charcoal placket in the gap at screen RIGHT; long back panel flaring to screen
  LEFT; standing collar; worn hem; pale apron over the near front of the skirt with botanical hem motif.
- Herb sprig on the anatomical **right chest = near front (screen RIGHT)**, tips past the coat front edge.
  Near right arm: ivory sleeve, pale cuff, dark glove. Far left arm is occluded by the torso; a glove hint may
  show at the far bag. Brown boots: near right boot forward, far left boot darker and set back; brass eyelet.

## Native geometry and export

- Native canvas 80x112 px; pivot (40,104); body rows 8..103; display scale 0.5 = **48 logical px**.
- Binary alpha, transparent one-pixel border, declared palette (<=40 entries, 24..48 used), >=8 genuine visible
  role layers, hidden `guides` layer; 35-entry palette inherited from Heya south v01.
- Editable layered source: deterministic `.pxo` (Pixelorama) and `.ora` (OpenRaster); flat `.png` composite;
  `.json` palette and `.json` manifest with raw sha256 hashes (no normalization).
- Fresh staging `outputs/heya-e155/staging/east/`; installation only through
  `python3 tools/wb_safe_replace.py` when destination bytes differ (unique verified backups).

## Protected properties and non-goals

- Protected: 44-year-old clinician identity; low auburn braided coil; grey-white scarf; ivory coat/apron/
  charcoal dress; **dark-red bag on the anatomical LEFT (far) hip**; upper-left screen light; dark gloves/brown
  boots/herb; exact palette; 80x112 density-2 source, pivot and 48 logical display.
- Non-goals: no runtime/default selector wiring, no animation/motion, no south/west/north edits, no ledger/
  Bible/registry edits, no Git index/commit, no GUI save/reopen claim, no diagnostic-clean claim from CLI
  export, no creator art approval.
