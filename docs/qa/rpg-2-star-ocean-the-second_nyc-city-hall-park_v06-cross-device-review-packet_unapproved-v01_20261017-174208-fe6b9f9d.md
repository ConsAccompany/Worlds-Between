# NYC City Hall Park v06: cross-device review packet

Status: **UNAPPROVED. Generated source. Opt-in only, off by default.** This packet is for environment review only.

- Codex looked at the real 640×360 captures. v06 is materially richer than v05, and the heroine and the landmark read. It stays unapproved.
- About **80% of visible pixels** derive from an AI-generated nonruntime reference that was palette-reduced and recomposed (70.4% unchanged position, 4.4% moved, 5.5% recomposed). The native share is 19.7%. It is **not hand-painted** and must not be presented as hand-authored art.
- The game shows v06 only with `-- --city-hall-park-v06` or a test override. The default city plate, its navigation and old saves are unchanged.

Counts are unchanged: meter 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2. Zero-change receipt: `closeout-20261017-214522-66a7bf2b`.

Auth: Claude Code with Opus 5.5, signed in through claude.ai firstParty on Max. `ANTHROPIC_API_KEY` was absent, and there was no paid fallback.

## Where to look

**Any device (GitHub, pinned to commit `1548c9e`).** Repository: ConsAccompany/Worlds-Between. Base: `https://github.com/ConsAccompany/Worlds-Between/blob/1548c9ec7dca2e7c4d95d06e5dad4a0e89ed80fb/`

| what | path after the base |
|---|---|
| **the one review capture:** zh entry, actual Godot 640×360 | `outputs/nyc-chp-v06_20261017-165253-4519dffe/rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-zh-entry-640x360_unapproved-v06_20261017-165253-4519dffe.png` |
| editable source, Pixelorama (named layers + hidden guides) | `game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-layers_unapproved-v06_20261017-165253-4519dffe.pxo` |
| editable source, OpenRaster | `game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-layers_unapproved-v06_20261017-165253-4519dffe.ora` |
| flat 640×360 | `game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/rpg-2-star-ocean-the-second_nyc-city-hall-park_flat_unapproved-v06_20261017-165253-4519dffe.png` |
| generated source (AI reference, nonruntime) | `outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_style-alignment-reference_nonruntime-v01_20261016-225515-5ee8060c.png` |
| QA note (evidence, flaws, sync addendum) | `docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-candidate-640x360_qa-note_unapproved-v06_20261017-165253-4519dffe.md` |

`raw.githubusercontent.com/ConsAccompany/Worlds-Between/<full sha>/<path>` serves the exact bytes. The run's other 17 captures are committed as evidence but are not queued.

**Game Bible, Production view, "跨设备视觉审查队列" card: one new item.**
- #9 is the zh entry capture.
- Its stored badge reads "未批准 · 未接入运行时（默认关闭）· 生成源".
- The rendered card shows the flag-derived badges "未批准 · 未接入运行时 · 未验收" and "已在 GitHub（1548c9e）".
- The caption states the generated source, the opt-in flag and the open objections.

The eight existing items and the character v11 links are unchanged.

The private Site was not opened or redeployed in this session, so whether the Site shows #9 is **not verified**. It may need Codex's signed-in browser.

## Evidence (commit 1548c9e)

| file | git blob | sha256 | bytes |
|---|---|---|---|
| zh entry capture | 5de77658 | 8a2ae132cd425c4a0fa2fd9915d7c41f969115e465bef09f9d0ee10d0af990df | 289798 |
| capture manifest (18 captures) | 5416cc04 | 7c207aee07fec15ebdc8f78f28fba5145f721c46ca9a83e6f59bd2f37f73f552 | 4371 |
| `.pxo` | 9159892d | 3ba6ad20aa3f120104fcb69583dc905421437e99e823c4044ef202285eb7057c | 480064 |
| `.ora` | c28fcb16 | e4c839b87bf6ed6d965a685d7fc5d9dd485350f9595d28e28ec8b60687b5c89c | 723205 |
| flat PNG | 826a95d6 | 29b6cad4600bfe8912248dc76a5dd314383c8926b12db3d72f073e411c469d4a | 273721 |
| scene manifest (status UNAPPROVED, per-layer origin) | 7d19699e | a60c84c6d613a6d6ed8833c448bc218e9f9e3ca5a55d8c964f1af306e54cef4a | 8087 |
| generated reference | 47ecc828 | 4a029b723174212db0ea2fd1dc02c6b3d0801c70479bbbab23067762c780e01c | 3398821 |
| runtime `city_hall_park_v06_scene.gd` | 5f2abe61 | f5e1ac2b41923d892558e3a54700bee92f8d54af9aa8333e72daf3e14ae21e75 | 9196 |

After the push:
- `git ls-remote` showed `refs/heads/main` = `1548c9ec7dca2e7c4d95d06e5dad4a0e89ed80fb`.
- A fresh bare clone from GitHub had tree `fe190dd7…` and served the zh entry blob `5de77658…` with sha256 `8a2ae132…`.

## Verified before commit (fresh clones of the exact staged trees)

v06 commit `1548c9e` (tree `fe190dd7`; the tests ran on tree `65abb460`, which differs only by the QA-note addendum):
- **Author check:**
  - autocrlf=true with Pixelorama 1.2.3 headless: PASS 28/28. The v05-baseline gate is skipped because v05 is absent; it is not counted as passed.
  - autocrlf=false without Pixelorama: PASS.
  - Worktree with v05 present: 29/29.
- **Godot harness:** `CHP6_GODOT_CHECK_OK` 86/0, 1,008 moved frames, 0 off the mask.
  - 12 of 17 captures are byte-identical, including both entries and the current-runtime reference.
  - The other 5 differ only inside the hero's box (walk phase or reveal dither).
- **Export pack:** `CHP6_EXPORT_CHECK_OK` 10/10, run from the pack only.
- **Smokes:**
  - default: m1, m2, m7, m8 city navigation, reentry and integration, and canopy silhouette;
  - `--city-hall-park-v06`: m8 integration (it logged the legacy migration (82,260)→(82,203.5)), reentry and navigation.
- **Old saves:** the harness compares the save file before and after load, and it is not rewritten.

Queue commit (this packet, Bible state, review-queue test, one server allowlist line, receipt):
- builder `--check` contentEqual and bytesEqual, 33 canon checks;
- meter `CHECK OK 40.8%`;
- review queue 7/7: 9 items, #9 served byte-identical through the exact nested allowlist;
- canon 5/5, M2 travel 5/5, meter 7/7, readiness 7/7, selout-v2 14/14, site preview PASS, hash portability 5/5.

## Outstanding visual objections (unchanged, not fixed here)

1. The wide north promenade is a flat, regular band of repeated courses. It exists to keep the hotspot canon coordinates.
2. Seams: native flags meet the reference pavers with a change of grain, and the west link, terrace walk and report link are rectangular blocks.
3. The City Hall dome is vertically compressed (about 0.68) and its finial is cut by the header. The dome is still the reference's enlarged form.
4. The fountain is the reference's tazza, not the restored Jacob Wrey Mould fountain.
5. About 80% generated source. That contradicts the 2026-10-16 direction note, which said the reference was not to be pasted or downsampled. This is why v06 can only ever be a reference-transfer candidate.

Smaller items from the QA note also remain: simple native props, soft imported detail at 2×, an SE elm crown cut at the screen edge, the "in the bowl" read north of the fountain, and markers drawn over the art.

## What was not done

- No art revision and no v07.
- No acceptance, counter or meter change.
- No Game Bible app change.
- No Site deploy.
- v05 stays local and unsynced.
- The worktree's other-session edits in `scifi_exploration_area.gd` (v05 branch, Yonkers fixtures), the Bible app/server (GIF allowlist), the progress JSON (other receipts) and elsewhere were left unstaged.
