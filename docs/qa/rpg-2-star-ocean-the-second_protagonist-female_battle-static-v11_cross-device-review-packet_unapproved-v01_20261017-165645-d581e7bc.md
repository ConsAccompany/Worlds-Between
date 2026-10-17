# Female battle static v11: cross-device review packet

Status: **UNAPPROVED, NONRUNTIME.** This packet is for creator feedback only.

- Codex looked at the real 640×360 captures and judged the static identity legible enough to show the creator. That is not art approval.
- It is not a complete character sprite. It is not permission to start animation.
- The only creator-approved item is the 0.65 battle display proportion.
- The game does not use this sprite. No runtime scene or script references it, and battle still draws its existing sprite.

Counts are unchanged by this packet: meter 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2.

Auth: Claude Code with Opus 5.5, signed in through claude.ai firstParty on Max. `ANTHROPIC_API_KEY` was absent.

## Where to look

**Any device (GitHub, pinned to commit `53a912f`).** The repository is ConsAccompany/Worlds-Between. These blob links open the images in the browser. Base: `https://github.com/ConsAccompany/Worlds-Between/blob/53a912fc6e80eacd5acfd2b6f6a2554813f6f944/`

| what | path after the base |
|---|---|
| **bright**: archive arena (brightest behind the figure) | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-archive-640_unapproved-v11_20261017-023937-0b43cdb2.png` |
| **dark**: outskirts arena (darkest behind the figure) | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts-640_unapproved-v11_20261017-023937-0ec09d0b.png` |
| ruins arena | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-640_unapproved-v11_20261017-023937-b6af9a1c.png` |
| city-terrace arena | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-city-terrace-640_unapproved-v11_20261017-023937-fe093ca6.png` |
| editable source, Pixelorama (19 layers + hidden guides) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_editable-layers_unapproved-v11_20261017-023937-e2debcc6.pxo` |
| editable source, OpenRaster | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_editable-layers_unapproved-v11_20261017-023937-4d57e12a.ora` |
| flat 68×72 sprite | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v11_20261017-023937-873fe1e6.png` |
| QA note (evidence + limitations) | `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v11-identity-density-pass_qa-note_unapproved-v01_20261017-023937-6f0c3b18.md` |

The `raw.githubusercontent.com/ConsAccompany/Worlds-Between/<full sha>/<path>` form serves the exact bytes.

**Game Bible, Production view, "跨设备视觉审查队列" card.** Two new items:
- #7 is the bright archive capture.
- #8 is the dark outskirts capture.

Both carry the "未批准 · 未接入运行时 · 未验收" badge and a "已在 GitHub（53a912f）" badge. This view runs on the local panel server (`127.0.0.1`).

The private Site was not opened or redeployed in this session. Whether the Site already shows #7 and #8 is not verified.

## Evidence (commit 53a912f, all bytes unchanged from the v11 run)

| file | git blob | sha256 | bytes |
|---|---|---|---|
| capture archive 640 | a3ae3e40 | c9e529a9b0eff29f1887530852e7d7e2f8820bd41f7066021b425acc7c9d0357 | 315286 |
| capture outskirts 640 | 054353ff | 6e4a5f4227774c289f752f0490cd4ab6b9b1d1fc887c1c86bee877b3a8b65d9a | 326495 |
| capture ruins 640 | f4c9c970 | 51ff11303368db4bca434be8c88a3470d83e094a994c7da0a2363e69399c6234 | 336965 |
| capture city-terrace 640 | bc59a88d | cb88f9cb43f719ecd73024fd36947db2db39603b814460bc06016f4a85dfd808 | 313639 |
| capture manifest archive (`…-11e14503.json`) | 482fe0aa | 34a1038583b308e22743dbe3099b473f696ceec8b63fd160268d3772c93780d8 | 4491 |
| capture manifest outskirts (`…-6ad0b2a3.json`) | 40e0455a | 0be1f9d3f2b99a8573bcf98e79736ace8bd1c8eeb20c0df69f29af788220f09e | 4499 |
| capture manifest ruins (`…-3b6a06d2.json`) | cd2f0198 | 57c2535f36904e485f124207b3d07977a3c78f3c200254f6676a404455eb23a1 | 4483 |
| capture manifest city-terrace (`…-83496a11.json`) | e7cd7f97 | 0161c30970c5c737e5e86c54acb92a1166efaf2d52bf7f48260f250bb99cf3e8 | 4511 |
| sprite PNG | 70ce1234 | cca1683392af7cd9d6c8305b64d2527b1573bc582cf2d011ec3bd876bc4b24c3 | 2129 |
| `.pxo` | 40595308 | 73aacdf0474f912a65d4deb8bfed3c9cad03a632dbdcd85c4d17f799e32fda86 | 11749 |
| `.ora` | 70758ba6 | 21e09b9aced48ae5003c0c01c1bc2eee3c4527089a6dce01123065806307cd32 | 11997 |
| sprite manifest (`…-3e18a8af.json`, `art_approved: false`, `runtime_integrated: false`) | 7c7ff205 | b6ec32906e010570592516e6a268f1806a21d8497113be2a2ec0b10141656dd6 | 19697 |
| QA note (with sync addendum) | a48a0772 | 1359b1a99f685654318493047be1d035bb0b045dfef8fb42b45f1f2a072a9c1f | 11114 |

All 12 asset files match the hashes recorded in the QA note at the time of the run. Each capture manifest's `captureSha256` and `candidateSha256` match the tracked capture and sprite.

After the push, all 13 files were downloaded from raw GitHub at the full SHA: HTTP 200 each, and the bytes equalled the commit blob.

These stay local and hash-pinned only, with hashes in the QA note:
- the v11 author tool `…-c4a17e52.py`;
- the capture script `…-5b81c0d4.gd`;
- the measure tool `…-9d2e61f7.py`.

## Visible limitations

These come from the QA note and are restated so the creator sees them next to the images.

- **Size.** She still reads slimmer and lighter than the three wide, big-headed companions. At the approved proportion her height and silhouette box are the same as v10's. The added detail (face, hand, forearm, hair, boots, pack) mostly reads at 2× and above; at 1× it reads as colour blocks.
- **Lower-body contrast.** The cooler lower body (no orange left) loses 1.6–3.7 |ΔL| against the floor compared with v10. On outskirts, 33% of boot pixels are within 20 L of the ground, mostly the sole band inside the contact shadow.
- **Small details.** At 1×:
  - the hair still reads mid-brown;
  - the face's 2×2 eye reads as one dark dot;
  - the 3×3 sleeve insignia is only a colour placement;
  - the pale hair tie reads as a separate bead at 8×.
- **Boots** are two-tone: dark shaft, lit foot.
- **Arena values.** All four arena floors are mid-value. "Dark" means outskirts; there is no night or truly dark field.
- **Party scene.** The captures show four people with an empty fifth slot and an idle sentry. No attack telegraph is captured.
- **Test overlay.** The candidate is drawn above the companions; in the real battle draw order, fighter 0 draws beneath them.
- **Reproducing the captures** needs the uncommitted `battle_arena.gd` arena-override work (`battleArenaScriptSha256Bytes` in each capture manifest) and the local capture script. There is no clean-clone rerun.

## What changed in Git

1. **`53a912f`** adds the 13 files above, by explicit path.
2. **The follow-up commit** that adds this packet changes three things:
   - **Game Bible state.** Only `environmentVisualReview.crossDeviceReviewQueue` changes. It gains items #7 and #8, both `creatorApproved` / `runtimeIntegrated` / `artAccepted` false, `committed-at-53a912f`, with exact blob and sha256. `asOf`, the header text and `siteRendering` now say eight captures, using the current counts.
   - **Review-queue test.** It now expects 8 items. It checks the v11 items, their tracked editable source and that no runtime reference exists. It realigns its stale counter assertions to the recorded 3/12 scenes and 40.8%, which another stream's Yonkers acceptance had already moved before this session.
   - **This packet.**

Nothing else changed: the shared Game Bible app and server, the progress ledger (no receipt added), the map, City Hall, Chicago, Washington, battle mechanics and character art.
