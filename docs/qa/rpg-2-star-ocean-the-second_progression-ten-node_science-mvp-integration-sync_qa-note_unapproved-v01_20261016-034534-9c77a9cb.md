# Ten-node progression SCIENCE-MVP: selective integration sync — QA note

- Date: 2026-10-16 03:45 America/New_York (07:45 UTC)
- Worker: Claude Code, signed in to Claude Max (`claude auth status`: `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`). `ANTHROPIC_API_KEY` was unset. No API key, credits or paid fallback was used.
- Source note: [progression QA note](rpg-2-star-ocean-the-second_progression-ten-node_science-mvp-rules-slice_qa-note_unapproved-v01_20261016-005300-e36e5d2c.md) (first pass, Lv100 correction, stationed-UI and recruit follow-up).
- Status: **technical candidate, unapproved.** This sync claims no art, no approval and no meter gate. The meter stays at **35.0%**. Counters are unchanged: sprites 0/52, science scene visuals 0/11, human playtests 0/2.

## What the root had already checked (reported to this session)

- `PROGRESSION_TEN_NODE_OK checks=494`, exit 0.
- Catalog: 20 series / 200 career nodes, 51 identities / 510 personal nodes, and every node-10 gate exactly Lv100.
- The root viewed the zh/en 1280×720 growth overlays, including the stationed Merchant, and the text fits.

## Independent verification in this session

1. **Hashes.** All ten implementation files match the latest `sha256-text-lf-v1` values in the source note: the catalog, the four scripts, the new test, m4, m5 and the two merchant tests.
2. **Diff review.**
   - `app_state.gd`, `growth_rules.gd`, `growth_screen.gd` and `commerce_ledger.gd` contain only progression changes.
   - `GrowthRules.SERIES[*]["skills"]` keeps the stage-ordered action list that HEAD `battle_arena.gd` reads at lines 379 and 852.
   - Nothing else in `game/` reads the removed `stage_names` or `commerce_passive_skills` keys.
3. **Catalog recount** (read with Node):
   - 20 series; every series has exactly 2 nodes in each of its 5 stages (200 career nodes).
   - 51 identities × 10 nodes (510 personal nodes); every `.p10` is at Lv100, and 100 is the highest gate.
   - Nodes with an effect:
     - 9 career: `sword_slash`, `sword_arc`, `firearms_shot`, `firearms_burst`, `tactics_mark`, `tactics_rally`, `relics_echo`, `relics_delay`, `merchant_fair_quote`.
     - 4 personal: `hero.p01`, `character-01.p01`, `character-16.p01`, `character-31.p01`.
   - `counts.approvedNodeDesignsAuthored` is 0.
4. **Isolated run of the exact commit tree.** A temporary index was built as HEAD `cae25fa` plus only the files listed under "Committed" below, except this note and the two PNGs. It was exported under `%LOCALAPPDATA%\Temp\wsc-sync\tree`, so the working tree and the real index were not touched. `battle_arena.gd` in that tree equals HEAD apart from line endings, so its dirty art hunks were excluded. Godot 4.7.2 ran `--import`, then each test with `--headless --path game --script`. All exited 0, and no log contains `SCRIPT ERROR` or `Parse Error`:

   | Test | Result |
   |---|---|
   | progression ten-node rules/save/UI smoke | `PROGRESSION_TEN_NODE_OK checks=494` |
   | m1, m2, m3, m4, m5, m6, m6_restart, m7 smoke | all `*_OK` |
   | m8 city integration / navigation / re-entry | all `*_OK` |
   | merchant city-commerce path | `checks=109` |
   | merchant Fair Quote rank/settlement/UI | `checks=92` |
   | commerce weekly settlement | `checks=149` |

   In the same tree, which has the HEAD Game Bible app and server, these Node checks also passed:
   - builder `--check`: `contentEqual: true`, `bytesEqual: true`, 24 canon checks;
   - Game Bible builder canon test: `RESULT PASS (5 checks)`;
   - M2 global-travel Game Bible test: `RESULT PASS (5 checks)`;
   - meter CLI `check`: `CHECK OK 35.0%`;
   - meter test: `RESULT PASS (6 checks)`.

   They also pass in the working tree.

## Game Bible status correction (narrow; no builder change)

The builder carries `creatorDecisions` and `openQuestions` verbatim from the tracked state and checks them. Editing those two curated keys therefore cannot be overwritten by a rebuild, and no builder change was needed. `--check` reproduces the edited file byte for byte.

These edits were made by script in `outputs/…game-bible_state_v01_20261013-195422-b8c16d42.json`:

- **`creatorDecisions.status`.** The skills clause now says that the ten-node structure (20 × 10 career, 51 × 10 personal, rank cap 5) is a runtime technical candidate (unapproved), but the naming and design of the 710 nodes are not done. AI, combos, reputation, price propagation and endgame scenes stay "尚未实现". The `技术候选` and `尚未实现` phrases that the M2 test asserts are kept, and so are `runtimeImplemented: "partial"` and `runtimeEvidence`.
- **New `creatorDecisions.skillRuntime` block**, in zh and en:
  - `status: technical-candidate-unapproved`;
  - 200 / 510 catalog nodes, with `approvedDesignsAuthored: 0`;
  - nodes with a runtime effect: 9 career, 4 personal;
  - `stage5FinalQuestContent: absent`;
  - 5 of 20 series enterable;
  - provisional items: the recruit stage formula, the free signature-rank catch-up on recruit, personal gates 2–9, English stage labels, and rank 4–5 JP costs;
  - `artAccepted: false`;
  - evidence: the source note and this note.
- **Open question "职业与个人技能树（待按新规则重设计）".** The approved-rule text is kept unchanged. One sentence is appended: a runtime ten-node technical candidate (unapproved) exists, but its nodes are not named or designed; only 9 career and 4 personal nodes have an effect; stage-5 final quests have no content; 15 series cannot be entered; the recruit stage formula and the free signature rank are provisional.
- **`updatedAt`** is now `2026-10-16T07:45:34.000Z`.

These are **not** changed:
- the chapters, characters, job roster, stage names and `finalQuest` texts;
- the superseded draft trees, `canonBasis` (still `approvedAuthored: 0` of 710) and the review blocks;
- every other key of `creatorDecisions`.

Hashes (`sha256-text-lf-v1`):

| File | Hash |
|---|---|
| Game Bible state, before | `303942c975bf51391c6de3bcbaaf4d36807237459de85c591a3143e88b561074` |
| Game Bible state, after | `c841e1226303330006c426c5cca152fe9cbbc21bcfa44fe1d832c19838f78062` |
| progress state, committed as found | `905e6149e6dc46723ff02b6d50aaadbc8893b3cd3b57497e9b2a7ece6f6c981c` |

## Meter

The progress state is committed as found. It holds three zero-change closeouts, with `changed: false` and 35 → 35:

| Closeout | Task | Evidence |
|---|---|---|
| `closeout-20261016-063819-f50c445c` | this progression candidate | the source note |
| `closeout-20261016-063819-e876a836` | female battle idle v05 | Codex visual audit `…battle-static-v05-codex-visual-audit…c64e85a2.md` |
| `closeout-20261016-063820-2db43dbf` | Washington establishing view | session-limit hold note `…wdc-capitol-establishing-session-limit_hold-note…6e7bdc43.md` |

All three evidence notes are committed with it. No closeout was added for this sync. It integrates the task that `f50c445c` already records, and the dispatch asked for the current meter state with exactly these three closeouts.

## UI captures copied (not art; not acceptance)

The two stationed-Merchant overlay captures from the follow-up's windowed run (`--resolution 1280x720 --capture`, `checks=498`) were **copied** from `%TEMP%\wsc-growth\capture2\`. The originals and the two non-stationed overlay captures were left in place. This table serves as their manifest:

| Repo file | Source | sha256 (bytes) |
|---|---|---|
| `outputs/rpg-2-star-ocean-the-second_progression-ten-node_growth-overlay-stationed-merchant-capture-zh-1280x720_unapproved-v01_20261016-034534-fb6b1492.png` | `progression-ten-node_stationed-zh.png` | `da3db7bedd3d1a98ac682f8067a62609885c8c01c4be9b2ac0c0c48bb9b411ed` |
| `outputs/rpg-2-star-ocean-the-second_progression-ten-node_growth-overlay-stationed-merchant-capture-en-1280x720_unapproved-v01_20261016-034534-6bb4b55f.png` | `progression-ten-node_stationed-en.png` | `f8962ca0f660e8a946c13cdf3c762cd841bc1c00ff927be33bd4035fa32c0994` |

I viewed both. Liang Xu is shown as a Contract Manager (契约经理). The Fair Quote node is greyed and reads "Lv1 · 驻守冻结 / Lv1 · stationed". The summary ends with the frozen reason. Job nodes for stages 3–5 show their stage gate, and personal nodes 4–10 show Lv22…Lv100. All text is inside the 1280×720 frame in both languages.

## Committed

- Code and data:
  - the catalog `game/data/growth/…progression-ten-node_science-mvp-skeleton_v01_20261016-005300-e36e5d2c.json`;
  - `game/scripts/growth_rules.gd`, `app_state.gd`, `growth_screen.gd` and `commerce_ledger.gd`.
- Tests:
  - `game/tests/m4_smoke.gd` and `m5_smoke.gd`;
  - the two merchant tests;
  - the new progression test.
- Notes: the source QA note and this note.
- Game Bible state (narrow status edit), and the progress state with its 3 closeouts and their 3 evidence notes.
- The two capture PNGs above.

## Not committed (left dirty or untracked, untouched)

- `game/scripts/battle_arena.gd` (art hunks).
- `docs/progress.md`.
- The Game Bible app and server.
- The character visual checklist (md and json).
- The Game Bible builder (unchanged).
- All unapproved art: female battle idle v04/v05, Capitol west v04, and the establishing-view tool.
- Other workstreams' notes and tools.
- `.playwright-cli/`.

## Still open (do not overstate)

1. **The 710 approved skill designs are not authored.**
   - 191 career and 506 personal nodes are unnamed skeletons with no effect.
   - The 13 nodes that have an effect reuse existing runtime skills. They are not approved 10-node designs.
2. **No stage-5 final-quest content exists.** Stage 5 is reachable only through `clear_series_final_quest` in tests.
3. **15 of the 20 series are catalogued but cannot be entered.**
4. **Stages 3–5 add no new battle action.** Rank 4–5 balance is unreviewed.
5. **Provisional, pending creator review:**
   - the recruit stage formula (`1 + level / 10`, held at 4 without that series' final quest);
   - the free signature-rank catch-up on recruit;
   - personal gates 2–9;
   - English stage labels;
   - rank 4–5 JP costs.
6. **No human review or playtest of the progression UI.**
