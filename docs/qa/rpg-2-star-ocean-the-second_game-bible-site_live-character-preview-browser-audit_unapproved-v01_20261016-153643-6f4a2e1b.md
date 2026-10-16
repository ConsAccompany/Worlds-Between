# Game Bible Site character preview browser audit (2026-10-16)

Status: UI defect confirmed; no visual asset or MVP gate accepted.

- The private production Site showed GitHub source `4bf778f` and the correct 35% completion meter. Its Production tab rendered **one** `.visual-sample` figure: the older city sample.
- The cloud Game Bible `characterVisualReview.previews` array contained **nine** records, including the unapproved female battle v08 and Liang Xu south v01 static pilots. These records did not appear in the production DOM.
- Read-only inspection of the private Site source checkout confirmed `public/bible.js` renders `citySample` but contains no `characterVisualReview.previews` rendering loop. This explains the single live figure.
- Opening the female battle v08 preview through its state URL under the Site's `/assets/` path returned **404**. The same committed image opened successfully from `raw.githubusercontent.com/ConsAccompany/Worlds-Between/main/outputs/` as a 1280×720 image.
- The private Site source has no `public/assets` directory. The nine preview records use `/assets/...` paths; a live renderer needs either an actual packaged asset directory or verified GitHub raw image URLs.
- A local, incomplete Site patch exists in `tools/rpg-2-star-ocean-the-second_game-bible-site_production-preview-figures-patch_v01_20261016-113125-8c141468.js`. Before using it, check the actual Site source and resolve both the missing figure render and the `/assets/` URL mismatch. Do not deploy this partial patch as-is.

This was a read-only browser inspection. The Site remains private. The female exploration south selout v8 is the only creator-approved static baseline; the battle v08 and Liang Xu v01 images remain unapproved and nonruntime. Accepted sprites, science scenes and human playtests remain 0/52, 0/11 and 0/2; the weighted estimate stays 35%.

## Follow-up: Site source repair (2026-10-16, not deployed)

- The partial helper was refined before use. It no longer passes `/assets/` paths through: each preview is rendered inline after the city sample, and its image resolves to `raw.githubusercontent.com/ConsAccompany/Worlds-Between/<state commit>/outputs/<file>.png` (`main` if the commit is unknown). Paths that are not flat outputs PNGs get no image. Badges come from `staticBaselinesAndPilots` (`creatorApproved`/`runtimeIntegrated`) or `artAccepted`, not caption text: battle v08 and Liang Xu v01 read "未批准 · 未接入运行时 / Unapproved · nonruntime", and the other seven read "审查截图 · 未验收 / Review capture · not accepted".
- Private Site source commit `f5dc623` (`public/bible.js`, `public/bible.css`) equals the helper output. The focused check `tests/game-bible-site-preview-figures/…a29ef51f.js` passes: the unpatched `e4ad7f0` client reproduces the 1-figure DOM, and the patched client renders city + 9 previews. `npm run build` passes.
- A headless Chromium render of the built client against live GitHub state `4bf778f` showed 10 figures, 10 images decoded (the previews at 1280×720), no `/assets/` URLs and no HTTP ≥400 responses. All 9 pinned URLs and the 7 fallback-snapshot URLs at `09d3689` returned `200 image/png`.
- Not deployed or pushed; the Site stays private. Counters are unchanged: sprites 0/52, scenes 0/11, playtests 0/2, meter 35%.
