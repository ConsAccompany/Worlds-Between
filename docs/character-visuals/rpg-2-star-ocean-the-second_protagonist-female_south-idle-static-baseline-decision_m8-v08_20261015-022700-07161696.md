# Female south idle: static still-frame baseline decision (selout v8)

M8, 2026-10-14 (file stamp UTC, 2026-10-15). This file records a user decision. It is not an automated result.

## Decision

The user reviewed the two real Godot 1280×720 selout v8 captures, the bright science city and the bright outskirts, and replied:

> 够了，可作为静止帧基准

(Enough; it may serve as the still-frame baseline.)

**What is approved:** the female protagonist's **south-facing idle static frame**, selout v8, as the **visual baseline** at **48 logical px**. Later frames and facings should match its palette, materials, value structure and outline treatment.

**What is not approved:**

- any walk or idle animation, or any exploration animation (animation acceptance stays 0);
- the north, east or west facings;
- replacing the runtime sprite: v8 is not wired into the playable game;
- runtime-sprite acceptance for any of the 52 variants, including this one: exploration sprites stay **0/52**;
- any environment or scene-quality gate: **0/11**;
- any human timed playtest: **0/2**.

## Approved artifact

- [selout v8 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png): sha256 `ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd`. 80×112 cell, 43×96 visible body, 2,419 opaque texels, 32 colours.
- [v8 manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json): sha256-text-lf-v1 `3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed` (first recorded as raw sha256 `0fa7937d3d4f68f209b30e611542ae1a130a82ee2327fb98b0ca19dc77fb5992` of the CRLF Windows working copy; same content, see the amendment below).

The decision applies to this exact PNG and this exact manifest content. If either hash changes, the decision does not carry over to the new file.

## Hash amendment (2026-10-14): line-ending independent text lock

The original manifest lock was a raw SHA-256 of the Windows working copy, which had CRLF line endings. Git stores the file with LF (`core.autocrlf=true`), so a clean LF checkout failed the lock even though the content was identical. The manifest and QA report are text files, so they are now locked with `sha256-text-lf-v1`: SHA-256 after each CRLF pair is replaced by LF, with nothing else normalized. The [hash algorithm decision](../rpg-2-star-ocean-the-second_content-hash-algorithm-decision_text-lf-v1_m8-v01_20261014-224905-85c51d63.md) has the details.

- The CRLF working copy that hashed to `0fa7937d…5992` at approval time still does. After CRLF→LF it is byte-identical to the blob committed in `ff8acd8` (Git object `dd24f1e231f5fa905f159a6553a4071be4cf3d6a`), whose SHA-256 is `3ba35811…10ed`. The new value locks the same content.
- The QA report was already stored with LF, so its value `513ab659…631a` is unchanged under the new algorithm.
- The PNG and the three capture hashes are binary, exact-byte locks and are unchanged.
- The approval scope is unchanged. Counters stay **0/52**, **0/11** and **0/2**.

## Evidence the user reviewed

| Scene | Capture | sha256 |
| --- | --- | --- |
| Science city (bright), reviewed | [city v8](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | `0b8e67ac75539fdac46e7843687d660d0dfa98697f7bf229b0079437351d9e65` |
| Outskirts (bright), reviewed | [outskirts v8](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | `b4cedaddc7832850e2904e798e92c36ca479966e8c59453f1bb05e11d881c12f` |
| Survey annex room 2 (dark), same run, linked only | [annex v8](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | `da444d274b21a529859b306af612d46859087ef2785bc0d66f9e19f9682d5b0c` |

- [QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json): sha256 `513ab6595fd3bedee02d8477e9a2646c7d98b40f19de8791d147e746e3ea631a`.
- [v8 QA note](../qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md).

The user's reply named the two bright scenes. The dark annex capture comes from the same run and is linked for completeness; the reply does not cover it.

## Provenance

- The v8 manifest and QA report keep `art_approved: false` and `human_reviewed: false`. Those values were written when the files were generated, before the user replied. They are left unchanged, because rewriting them would break the recorded hashes. This file is the record of the decision.
- The asset inventory's `runtime-sprite.protagonist-female` item stays unchecked. This decision approves a static baseline frame, not a runtime sprite.

## History kept as it was

- **v1:** chosen by the user as closer than inkline; not approved.
- **v2:** closer still in the user's view; not approved.
- **v3:** internal review found it barely changed; not approved and not offered.
- **v4:** technical candidate, not reviewed by the user; not approved.
- **v5:** user replied "更接近了，继续精修" (closer, keep refining); not approved.
- **v6:** user replied "明亮场景对比度仍不足" (bright-scene contrast still insufficient); not approved. Its status does not change.
- **v7:** slate coat, 369 texels over v6. It had a technical QA note only and no user verdict. Codex's visual review found that the coat shift was subtle and the lower body still merged with warm paving. Not approved.
- **v8:** cloth/leather, 793 texels over v7. Approved by the user as the static still-frame baseline (this record).
