# Heya west walk/stop source QA note (UNAPPROVED, h167ww01)

- Task: `content.char.heya.walk-west` (batch167), owner DeepSeek, date 2026-10-24.
- Status: **UNAPPROVED technical source and checks only**; not integrated, not a runtime default, no art/motion acceptance.
- Scope: west walk/run cycle + phase-aware stop source for Heya. Dependency `content.char.heya.static-west` is DONE and its
  static PNG/PXO/ORA/manifest/palette are pinned byte-exact (raw SHA-256) and unchanged by this work.
- Starting canonical meters (coordinator snapshot, not changed by this note): production 62.8%, inspection 21.6%,
  approval 7.8%. This producer does not update the shared ledger or claim a meter change.

## Identity and layer roles

44-year-old clinician: auburn braided coil LOW at the nape, grey-white medical scarf with long near-front tail, ivory open
clinician coat, pale apron, charcoal underdress, dark-red emergency bag with brass clasps on the near left hip, herb sprig,
dark gloves, brown leather boots with folded cuff and brass eyelet. Heya west static/portrait remain UNAPPROVED.

13 role layers (excluding hidden `guides`): head = `face/hair/braid` (coil bobs with the head, no secondary sway); torso =
`dress/coat/apron/belt/strap/bag/herb/scarf` (bob only, no cloth secondary motion); arm-like = `arms` (near arm sheared
about the shoulder); legs = `boots`. There is no trousers layer. Near boot = static columns `x >= 37`; far limb = the
complete boot silhouette recoloured through the pinned Heya DARK table (`r1->r2`, `r2->r3`, `r3`, brass eyelet kept) in
the `far-limbs` cel. The A-line dress hem is torso-only and is not lifted, so a lifted boot can pass behind the static hem
(disclosed static-texel limit, not a repaint).

## Build and source checks

Command: `python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-west-source-author_unapproved-hww167-v01_20261024-144500-h167ww01.py build|check`
(venv `/home/kel/projects/worlds-between/tooling/venv/bin/python`). Build wrote 91 new files; rebuild **91/91** and
`DETERMINISTIC True`; source checks **21/21 PASS**; output `RESULT PASS []`. The check was rerun after build and wrote a
second PASS report. No existing static or previous tool bytes were replaced.

Contact (author `contact_report`, independently re-derived by the checker):

- each foot grounded 4 of 12 phases; flight phases p4, p5, p10, p11;
- planted world slip at 40 ms boundaries max **0.8 source texel** (0.4 logical) = integer rounding of 11.2;
- 60 fps held-frame excursion **10.667 src / 5.333 logical** (disclosed frame quantization, not footlock);
- all **12** stop-entry bridges inclusive endpoint: grounded-foot slip **0**, bridge endpoint idle f00 == neutral PNG;
- total 41 frames: static 1 + idle 4 + walk 12 + stop 2x12; walk 40 ms/frame (480 ms cycle), stop settle 120 ms inclusive.

## Independent check

Command: `python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-west-independent-check_v01_20261024-144500-h167ww01.py --out outputs/heya-ww167/independent-3`
Result: **PASS 36/36**, including **15/15 negative controls rejected** (tampered PNG/PXO, malformed stop JSON, wrong
duration/pivot/direction, bridge near/far boot slide, off-neutral endpoint, unchanged-bitmap walk, wrong identity).

Native Pixelorama `--headless --export`: **41/41 frames RGBA-exact**, exit 0, no timeout, source PXO unchanged.
Native export equality is **not** application cleanliness: the log contains 4 `ERROR: Condition
"!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.` diagnostics, so
`application_clean=false`; **GUI SaveAs/reopen is NOT verified**.

## Normal-speed source-bound fit

Command: `python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-west_normal-speed-fit_v01_20261024-144500-h167ww01.py`
Checked Godot runner, Xvfb 640x360, OpenGL3, Dummy audio: **PASS**, 6 captures, exact frame hashes and target states,
pivot `[40,104]`, scale 0.5, 48 logical px, texture `[80,112]`; marker
`HEYA_HWW167_WEST_WALK_NORMAL_SPEED_PASS captures=6`. This is a test-only source-fit overlay, not ordinary actor adoption
and not human motion review.

## Failures retained / limitations

- `outputs/heya-ww167/independent-1/` is a preserved failed checker run (34/35) from an over-strict endpoint assumption
  that compared the halfway s2 foot to neutral instead of the bridge endpoint idle f00. The checker was corrected; no
  acceptance threshold was weakened. The exact failed result JSON is retained.
- Pixelorama application diagnostics above (4 errors) are reported separately from export equality.
- Side gait is not footlocked/slip-free: held-frame world excursion and integer rounding remain.
- Far limb is a recoloured complete boot silhouette; the dress hem is static; no cloth secondary motion.
- Heya west static/portrait remain UNAPPROVED; no art, fluidity or human motion acceptance, no runtime/default adoption.
- Supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only.

## Next step

Coordinator independent author/check, full native/independent and normal-speed fit reruns with the exact commands in
`outputs/heya-ww167/provider-receipt.json`; then decide integration/commit of the explicit candidate files there. The
shared ledger/Bible/registry/Git index were not touched.
