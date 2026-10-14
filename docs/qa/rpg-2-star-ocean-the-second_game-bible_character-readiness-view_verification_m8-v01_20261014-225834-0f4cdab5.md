# Game Bible character sprite readiness view — verification

Recorded 2026-10-14. This note covers a read-only display of an existing factual checklist. Nothing is approved here.

## What changed

- **Server** (`tools/rpg-2-star-ocean-the-second_game-bible_server_v05_20261013-222437-3d5b8a9f.js`): one new read-only `GET /character-readiness` entry in the existing `routes` table. It serves `game/data/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json` through the existing file loader, with the same `no-store` and `nosniff` headers. No other route changed.
- **Widget** (`outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`): the Production page (制作) has a new section, **角色精灵就绪清单 · 逐变体**, placed after the existing visual acceptance card. It loads the checklist when the page is first opened and reloads it when the tab becomes visible again. It shows:
  - the checklist's own summary: source portraits approved 9 / concept 43; readiness states 45 / 5 / 2; art acceptance 0/52; MVP combat 0/5; displays 0/52; intake stage 0 for all 52;
  - a filter (all / protagonist / main / side / situational / only variants with a hair review prompt);
  - one collapsible row per variant (52) with the hair/identity anchor quoted from the registry, the source portrait status, path and link, readiness state, and G1–G5 plus the display gate, each with its checklist status;
  - the 13 potential hairstyle confusion groups, each labelled **复核提示** and **待人工复核**, plus the three vague anchors and the seven robot variants without hair. These are marked as prompts, not decisions;
  - the path-check totals (0 missing, 0 untracked, 3 registry discrepancies).
- **Styles** (`outputs/rpg-2-star-ocean-the-second_game-bible_styles_v01_20261013-195526-6c13fa09.css`): rules for the new section only, plus narrow-screen rules inside the existing media query.
- **Test**: `tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js`.

The checklist, visual registry, asset inventory, progress state and all art are unchanged. The existing counters on the Production page (source portraits 9/52, displays 0/52, exploration sprites 0/52, scene quality 0/11, stages 6/9) still come from the inventory and progress files, as before.

## Safety

- Every checklist string goes through the widget's existing `esc()` before insertion. Status values are translated only through a fixed lookup table. An unknown value (for example `accepted`) is shown as-is and is never turned into an approval label.
- Portrait links are only created for paths matching `outputs/<filename>.png`, and they point to the existing `/assets/` route. Any other path is shown as text with no link.
- The widget rejects a response unless `schema_version` is 1 and `kind` is `character_sprite_production_readiness_checklist`. If the checklist can't be read, only this section shows an error and the rest of the page is unchanged.

## How to verify

1. Automated check, run from the repo root:

   ```
   node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
   ```

   It starts the v05 server on a free local port, so a panel already running on 18727 is not touched. It then checks that the route serves the file byte-for-byte (sha256), checks the headers, and confirms that traversal and non-GET probes return 404/405. It runs the served `bible.js` against a DOM stub and checks for 52 rows, 13 prompt groups, 9 approved source portraits and 52 pending art-acceptance badges. It also checks that the rest of the Production page is byte-identical whether or not the checklist loads, that the existing counters are unchanged, and that hostile names, IDs, anchors, concerns and portrait paths are escaped or unlinked. Expected last line: `RESULT PASS (7 checks)`.
2. Manual check: **restart the panel** so the edited v05 server is running (a process started before this change returns 404 for `/character-readiness`). Then open <http://127.0.0.1:18727/>, go to **制作**, and scroll to **角色精灵就绪清单 · 逐变体**. Expect 52 rows ("显示 52 / 52"). The filter **仅含发型复核提示** should show 37. **发型潜在混淆 · 13 组复核提示** opens to 13 dashed cards marked 待人工复核.

## Evidence from this change

- `node --check` passes for the app and the server.
- The automated check above passes (`RESULT PASS (7 checks)`).
- Headless Chromium at 430×900 against a temporary v05 instance on port 18799: 52 rows, 37 with the review filter, a row stays open across a filter change, and the hair section has 13 prompt cards. The only console error was a 404 that isn't from the page's own requests, consistent with the browser's automatic `/favicon.ico` request (the server has never had a favicon route). Screenshots were checked visually and kept outside the repo.
