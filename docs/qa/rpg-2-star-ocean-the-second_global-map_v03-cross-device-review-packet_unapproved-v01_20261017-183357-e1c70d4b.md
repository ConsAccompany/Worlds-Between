# Global map v03: cross-device review packet

Status: **UNAPPROVED technical candidate.** Since commit `ec8b8f5` the live world map draws this v03 art, but the map-art gate is open and nothing is accepted.

- Codex looked at the real 640×360 zh/en globe, Northeast, Chicago flight card and Washington car card captures. v03 shows both flight endpoints more clearly, and land, lake and coast values separate better than in v02.
- **Not all-pass.** `scifi-world-map_background-visual-check` still fails `button geometry scifi.city`. It fails identically with the parent commit's (4b06aef) map scripts, so v03 did not cause it, but it is still a failing check.
- No design, route or travel-rule change.

Counts are unchanged: meter 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2. The zero-change receipt is `closeout-20261017-223616-134c30b6`.

Auth: Claude Code with Opus 5.5, signed in through claude.ai firstParty on Max. `ANTHROPIC_API_KEY` was absent, and there was no paid fallback.

## Where to look

**Any device (GitHub, pinned to commit `ec8b8f5`).** Repository: ConsAccompany/Worlds-Between.

The review image (Game Bible queue #10), the Chicago flight card in zh:

<https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/ec8b8f564ff80d137df903b1b11186fd01bf4215/outputs/rpg-2-star-ocean-the-second_global-map_native-art_us-great-lakes-card-chicago-air-zh-640x360_test-only-v03_20261017-175314-e8b8f8af.png>

Other committed captures are under the base `https://github.com/ConsAccompany/Worlds-Between/blob/ec8b8f564ff80d137df903b1b11186fd01bf4215/`. They are evidence, not queued:

| what | path after the base |
|---|---|
| Chicago flight card, en | `outputs/rpg-2-star-ocean-the-second_global-map_native-art_us-great-lakes-card-chicago-air-en-640x360_test-only-v03_20261017-175314-e8b8f8af.png` |
| globe, zh | `outputs/rpg-2-star-ocean-the-second_global-map_native-art_globe-zh-640x360_test-only-v03_20261017-175314-e8b8f8af.png` |
| Northeast, en | `outputs/rpg-2-star-ocean-the-second_global-map_native-art_us-northeast-en-640x360_test-only-v03_20261017-175314-e8b8f8af.png` |
| Washington car card, zh | `outputs/rpg-2-star-ocean-the-second_global-map_native-art_us-northeast-card-washington-car-zh-640x360_test-only-v03_20261017-175314-e8b8f8af.png` |
| QA note (evidence, defects, sync addendum) | `docs/qa/rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v03_20261017-175314-e8b8f8af.md` |

The other seven captures stay local; the committed capture manifest pins their sha256.

**Game Bible, Production view, "跨设备视觉审查队列" card: one new item.**
- #10 is the zh Chicago flight card.
- Its stored badge reads "未批准 · 技术候选 · 已接入运行时（地图美术未验收）".
- The rendered card shows the flag-derived badges "未批准 · 已接入运行时 · 未验收" and "已在 GitHub（ec8b8f5）". It is the queue's only runtime item, because the live map now draws it.
- The caption names the inherited failing check and the open defects.

Items #1–#9 are unchanged.

The private Site was not opened or redeployed in this session, so whether the Site shows #10 is **not verified**.

## Evidence (commit ec8b8f5, tree 3ac8b2f4)

| file | git blob | sha256 | bytes |
|---|---|---|---|
| Chicago flight card zh (queue #10) | 3a0d6fd2 | a1a5b1678c74c2dd8d9732371050e9ba0c43d851315336e2542bc5a210aff6bf | 97546 |
| Chicago flight card en | fd6ea432 | 4c6c705e71489585ff09f530e813f883ef62a9d95c90d050e08a4bce7f54eb0b | 94783 |
| globe zh | a3400ea1 | f48d9c90ab846468bed2127b95f9d38b49833b64e8b586915bf4451c4944033d | 63386 |
| Northeast en | 251bfaaf | 249ae409a57de4399e0f6aef98787939325d6b7495199aeede87577226ed54e5 | 101464 |
| Washington car card zh | f18baa45 | b438cb3751bb75efcefdd1835ce39e998d4ccbf9564346a5c424ab8489dd1889 | 126415 |
| capture manifest (12 captures) | 4eea032c | 40e7594a329b1642c1f34de30c4614f82ed533458ad0a553f8938adb12d41fe9 | 3066 |
| v03 relief JSON (runtime) | 2cdc4902 | 69e26698c3568210114de1e9bf73a1877d9dd745d07c13de70855e16bbccc3e7 | 196647 |
| `scifi_world_map.gd` | 5d39c0b8 | ad451eb52008a0e4545f8a86f6f2ed3cc836b3579e60669e2e6d63371f2b3e36 | 87702 |

After the push, `origin/main` was `ec8b8f564ff80d137df903b1b11186fd01bf4215`. The raw URL above returned HTTP 200, a 640×360 PNG of 97546 bytes, with blob `3a0d6fd2…` and sha256 `a1a5b167…`.

## Verified before the push

These tests ran on HEAD 4b06aef plus exactly the 26 synced files, exported to a temp copy with `autocrlf=true`.

- **Capture tool:** `NATIVE_MAP_ART_OK 1873 checks, 12 captures`. All 12 captures were byte-identical to the local run.
- **Source check:** `SOURCE_CHECK_OK 40 checks`. Its rebake comparison was fixed to use sha256-text-lf-v1; with raw bytes it failed in this CRLF checkout.
- **Headless:**
  - earth smoke 212;
  - integration regression 107;
  - travel core OK;
  - whole-hour travel 246;
  - export data 24;
  - US migration 32;
  - commerce 149;
  - M2, M6 and M6 restart OK.
- **Windowed:** route card 117/117, status backing 203/203.
- **Failing (inherited):** background-visual-check, `button geometry scifi.city`. It also fails with HEAD's map scripts.

## Open defects (from the v03 QA note)

1. The card body, degree labels, scale bar and stock buttons are still a planning UI.
2. The strip is small (192×58 px of map) and names no mode. The Chicago plate covers part of southern Lake Michigan.
3. The card is tight: 4 px spare on the Chicago card.
4. In the zoomed (1.5×) Washington card, the strip shows a car trip and the fallback drops lines. Label overlaps there predate v03 but are slightly larger.
5. The bigger plates cover more of New Jersey, and the en globe badge covers more of Western Europe.
6. The sea step widened less than the lake step.
7. Unchanged from v02: the straight car connector, relief at 1:1 only at default zoom, and procedural dither.
8. The v01, v01r1 and v02 capture tools fail against this tree by design.
