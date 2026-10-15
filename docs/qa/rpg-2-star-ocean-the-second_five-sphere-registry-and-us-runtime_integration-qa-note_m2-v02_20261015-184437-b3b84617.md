# Five-sphere region registry and US runtime integration: QA note (M2 v02)

- Date: 2026-10-15 (local)
- Worker: Claude (Worlds Between integration worker). Signed-in Claude Max, `firstParty` (`claude auth status`: `authMethod: claude.ai`, `subscriptionType: max`). `ANTHROPIC_API_KEY` was not set. No API key, credits or paid fallback was used.
- Scope: region registry, M2 tracking reconciliation, two UI fixes and the related tests. The art files are owned by another worker (Washington candidates) and were not touched; nor were the unrelated dirty hunks in `game/scripts/battle_arena.gd`. Nothing was staged, committed or pushed.
- **M2 status: not accepted, still in progress.** Counters are unchanged: runtime sprites **0/52**, science scene visuals **0/11**, human timed playtests **0/2**, 51 identities / 52 variants.

## 1. Region registry: five Earth spheres plus the final planet

The active v02 travel data `game/data/world-travel/…locations-routes_m2-us-science-v02_20261015-175011-c454007b.json`, field `regions`:

| id | planet | names (zh / en) | scope | status |
|---|---|---|---|---|
| `science` | earth | 科技板块 / Science sphere | US + Canada; hub NYC. `countryCodes: ["US","CA"]` | active-mvp |
| `magic` | earth | 魔法板块 / Magic sphere | South America; hub Manaus (马瑙斯) | locations-pending |
| `wuxia` | earth | 武侠板块 / Wuxia sphere | Asia; hub Chongqing | locations-pending |
| `nature` | earth | 自然板块 / Nature sphere | Oceania; hub Brisbane | locations-pending |
| `culture` | earth | 文化板块 / Culture sphere | Europe + Africa; dual hubs Athens and Cairo. `legacyIds: ["fantasy"]` | locations-pending |
| `offworld` | exterritorial | 终局星球 / Final planet | Reached by portal after all five Earth mainlines | locations-pending, portal only |

- **Hubs are text only.** They appear in each region's `scope`/`note`. No location, coordinate or route was added for any sphere except science, and no city was invented.
- **`fantasy` is an alias, not a region.** It is only an explicit `legacyIds` entry on `culture`, and `WorldRouteRegistry.resolve_region_id("fantasy")` returns `culture`. A location whose `regionId` is an alias fails validation as an unknown region. No save stores a region ID: saves store location IDs. The location aliases for old saves (`retiredLocations` for the three Shanghai IDs) are unchanged.
- **Map boards.** The display registry `game/data/world-map/…place-registry_m2-us-science-v02_…-eeaa6baa.json` `boards` mirrors the same six entries (`legacy_ids: ["fantasy"]` on culture) and adds a note. Only this block and the note changed; the rest of the file's hand formatting is unchanged.
- **Validator** (`game/scripts/world_route_registry.gd`):
  - `EARTH_REGION_COUNT := 5` replaces the hard-coded 4.
  - New `alias_to_region` and `resolve_region_id()`.
  - A legacy region ID that equals an active region or another alias is rejected.
  - The existing `countryCodes` rule still rejects any science place outside the US or Canada.
- **Core smoke** (`…calendar-route-core-smoke_…-a19d5ae7.gd`) now checks:
  - five Earth regions plus a non-Earth portal region;
  - the exact region ID set;
  - `fantasy` → `culture` and is not active;
  - no place outside science;
  - its fixture now has five Earth regions.

  It also gained three validator rejection cases: a legacy region ID reused by an active region, a location in an aliased region ID, and a place outside its region's countries.
- **Provisional files preserved.** SHA-256 before and after this pass, all unchanged and clean against HEAD:

  | File | SHA-256 |
  |---|---|
  | v01 travel data | `d633344b72b8c0af6c1998f0d06569b5fc876a97078c0ade6045759b04ba9e94` |
  | v01 place registry | `d16d7fcb4871c5f9d7fd0cdd8a436089830d3ea6318fd5250760525df131e661` |
  | v01 geodata | `500c5a12775c88ca0003ff11379e8eb6aced95b5da83f765b8e0192cf5b9be49` |

## 2. Tracking reconciliation

- **`outputs/…mvp-progress_state_v01_…-28a1c7e4.json`**
  - M2 `summary`, `remaining`, `blocker` and `details` describe the migrated runtime. New evidence lines point to the US migration note, the Great Lakes capture note and this note.
  - `m2Expansion.anchor` is now `implemented_technical_candidate` (NYC, City Hall Park, art not accepted). The Catskills community is recorded as decided but with no runtime place.
  - `creatorDecision.runtimeImplemented` is `true`, with `runtimeStatus` set to "technical candidate".
  - Gates: `anchor`, `start-year` and `air-route` moved from `decided_runtime_pending` to **`implemented`** and cite the US migration QA note. `map-ui`, `place-registry`, `route-preview`, `save-migration` and `acceptance-test` details and evidence now describe the US set and the re-run counts. **9/12 implemented**, 3 open (`route-data` estimate_only, `map-art` not_started, `visual-review` human_pending), none `done`. M2 `status` stays `in_progress`.
  - Decisions:
    - New blocked decision `old-save-dates`: shift 2026-dated saves into 2537?
    - `companion-sphere-mapping` now says 奇幻 = Culture (renamed) and 星外 = final planet; only Wuxia companions remain to design.
    - `prologue-start-date`, `skill-tree-redesign` (200 + 510 = 710 nodes) and `romance-10` stay open.
  - `designDecisions.runtimeImplemented` is `"partial"`, with its scope stated. The endgame is noted as full-game content, not MVP.
- **`outputs/…game-bible_state_v01_…-b8c16d42.json`**
  - `creatorDecisions` changes:
    - `runtimeImplemented` is now `"partial"`.
    - `status` says the geography is a runtime technical candidate, and that skills, AI, combos, reputation, price propagation and the endgame are not implemented.
    - New `runtimeEvidence`.
    - New `endgame.scope`: "完整游戏内容，不属于 MVP".
  - World chapter changes:
    - The Culture row says it is the renamed Fantasy sphere and that the old Fantasy setting carries over. The "待复核" question is removed.
    - The mainline-order sentence now reads "其余四个地球文明圈（魔法、武侠、自然、文化）的独立主线没有固定顺序，由玩家自由选择". The "推断，待创作者确认" wording is removed.
    - The anchor paragraph ends with the runtime state instead of "尚未迁移".
  - The rules chapter's endgame line is marked full-game, not MVP.
  - Open questions:
    - "运行时地理迁移" and "新游戏日期" are retitled as implemented, with their remaining items listed.
    - "伙伴的文明圈归属" is reworded to match the progress decision.
  - `environmentVisualReview` status and the `currentMapSatisfiesGeographyRuleNote` describe the US layers. The US QA note is added to `runtimeGeographyMap.qa`.
  - **Unchanged:** the reputation names are still exactly 求知、果敢、共情、公正、守诺, and Manaus is still 马瑙斯. `jobProposal`, `skillTreeProposal`, `personalSkillTrees` and `characters` have identical canonical hashes before and after this pass.
- **`outputs/…game-bible_app_v01_…-90e7bc24.js`.** One sentence in the "真实地名与汽车／飞机旅行" rule card changed. It now names the US Northeast/Great Lakes map and the runtime candidate instead of "运行时仍是已被取代的上海暂定组合…尚未迁移…没有航空路线". `node --check` passes.
- **`docs/progress.md`**
  - M2 summary bullet and M2 checklist updated: migration, calendar date, air route and weekly-settlement hookup ticked with their limits; route figures, map art and human review still open.
  - The previous entry's reputation line now uses the canonical names. It had said "curiosity, courage, empathy…".
  - New dated entry.
- **`docs/design/…creator-decisions…reconciliation-note_…-39efc292.md`.** Appended §10, an integration update. The earlier sections are unchanged.
- **Game Bible M2 test.** `tests/game-bible-m2-global-travel/…-06efaa9b.js` no longer hard-codes the Shanghai runtime. It cross-checks the gates against the active v02 travel data: US places, US/CA, the five spheres plus portal, `fantasy` only as an alias, the 2537-05-25 start, and the car and air figures. It checks that the v01 record still lists the Shanghai set and expects 9/12 implemented with no runtime-pending badge. It also checks the canon: reputation names, 马瑙斯, the endgame scope, no "待创作者确认"/"待复核" in the world chapter, and that the 710-node and relationship-tuning items stay open.

## 3. UI fixes

| Defect seen by Codex | Fix | Proof |
|---|---|---|
| English air route card: "Air · Air 1177.1 km" | `world_map_text.gd` en `air_km` is now "Flight %s km". zh "飞机 · 航程 … km" is unchanged. | Windowed capture prints `ROUTE en route.air.nyc__chicago [selected]: Air · Flight 1177.1 km · 6 h 5 min / Arrive May 25, 2537 14:05 / estimated distance and time`. The migration smoke asserts that the English text begins "Air · Flight " and contains "Air" once. |
| Loop: English "Technical placeholder · Art not accepted" badge and the subtitle ran under the Save button | `chicago_loop_district.gd` `_place_badge()` puts the badge 14 px after the title's measured width, and falls back to the hint row if it would pass `save_button.x − 8`. `app_state.gd` `area_loop_hint` no longer repeats the placeholder text. It now reads "Blocks inside the elevated L · No survey, recruit or battle" / "高架环线（L）内的街区 · 无勘察、招募或战斗". The badge text is unchanged. | The migration smoke checks, in both languages, that the title, hint and badge end left of Save and that the badge overlaps neither label. Inspected in the zh and en 1280×720 Loop arrival captures (below). |

The Loop stays explicitly unapproved. The badge "技术占位 · 美术未验收 / Technical placeholder · Art not accepted" and the footer note ("buildings and block scale are placeholders") are still on screen in both languages.

## 4. Test results (Godot 4.7.2, this machine, 2026-10-15)

Headless (`--headless --path game --script …`), all exit 0:

| Test | Output |
|---|---|
| core travel/calendar smoke (…a19d5ae7) | `GLOBAL_TRAVEL_CORE_OK` |
| global map smoke (…7b4550d6) | `GLOBAL_EARTH_MAP_SMOKE_OK checks=212` |
| map–travel integration (…786a054d) | `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=105` |
| commerce weekly settlement (…a9d18fda) | `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149` |
| US migration smoke (…5ffdb1e9) | `US_SCIENCE_MIGRATION_SMOKE_OK checks=32` (was 29; +1 English one-Air check, +2 Loop header checks) |
| merchant path (…4f6e24f2) | `MERCHANT_CITY_COMMERCE_PATH_OK checks=109` |
| merchant Fair Quote (…b37eb6d9) | `MERCHANT_FAIR_QUOTE_OK checks=91` |
| export data inclusion (…6e5c07b5) | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `m2_smoke.gd` | `M2_SMOKE_OK` |
| `m6_smoke.gd` | `M6_SMOKE_OK` |

The route-card and status-backing readability checks were first started headless by mistake. Both need a display renderer, so they hung until the 400 s timeout (exit 124). They were then run windowed, as their headers require.

Windowed (`--path game`, 1280×720), all exit 0:

| Test | Output |
|---|---|
| route-card readability (…e51bfe23); captures sent to `%LOCALAPPDATA%\Temp` via `M2_CARD_CAPTURE_DIR` | `ROUTE_CARD_READABILITY_OK 109 checks` |
| status-backing readability (…2d7e93b1); captures to temp via `M2_STATUS_CAPTURE_DIR` | `STATUS_BACKING_READABILITY_OK 199 checks` |
| bilingual map visual capture (…9b2fac94) | `GLOBAL_MAP_CAPTURE_OK 22`; `BEFORE earth.us.ny.new-york-city May 25, 2537 08:00`; `AFTER earth.us.il.chicago May 25, 2537 14:05` |

The 22 captures are in `outputs/` as `rpg-2-star-ocean-the-second_global-earth-map_*-runtime-capture_m2-v02_20261015-184808-49d78162.png` (11 zh, 11 en). The following were opened and inspected:
- `us-great-lakes-chicago-air-route-card-en`: "Air · Flight 1177.1 km · 6 h 5 min".
- `us-great-lakes-chicago-air-route-card-zh`: "飞机 · 航程 1177.1 km · 6小时5分钟".
- `chicago-loop-arrival-en`: the badge sits right after "Chicago · The Loop" and ends well left of Save.
- `chicago-loop-arrival-zh`: the badge follows "芝加哥 · 卢普区".

These captures are unapproved runtime evidence, not visual acceptance.

Node:
- `node tests/game-bible-m2-global-travel/…-06efaa9b.js`: see §6 for the final run output.

Not run: the geodata reproducibility builder (`…-0a728533 --check`). It re-downloads about 15 MB of Natural Earth sources, and this pass did not change geodata. M1, M3–M5, M7 and M8 smokes were not run either, and the M8 canvas-pointer regression was not run.

## 5. Observations left open (not fixed here)

- The map header still says "Global map · Science region" / "全球地图 · 科技板块". The registry names now say "sphere". This is consistent with the existing UI wording and was not in scope.
- The zh Loop footer reads "场景内步行不消耗日历时间。 · WASD 移动 …": a full stop followed by a separator. This predates this pass.
- Route figures stay preliminary (OSRM demo server, BTS July 2026 medians, an American Airlines check-in allowance). Yonkers–Chicago and Washington–Chicago have no route. City Hall Park, the Capitol and Loop art, a runtime place for the Catskills community, and human review are open.
- Open creator decisions: the prologue start date, and whether to shift old 2026-dated saves into 2537.

## 6. Game Bible test result

`node tests/game-bible-m2-global-travel/rpg-2-star-ocean-the-second_game-bible_m2-global-travel-gates_check_m2-v01_20261015-064400-06efaa9b.js`:

```
PASS counters: sprites 0/52 and scenes 0/11 match the inventory; 51 identities / 52 variants match the checklist; human playtests 0/2
PASS approval ledger: only the 48 px scale and v8 static frame approved; sentry and Liangzhu are direction-only; four-direction animation not accepted
PASS M2 in progress with 12 gates (9 implemented with QA evidence incl. 3 migrated from decided/runtime-pending, 3 open, 0 done), 41 evidence paths exist, US runtime (NYC, Yonkers, Washington, Chicago, 2537-05-25) matches the v02 travel data, five Earth spheres + portal final planet with fantasy only an alias, route figures match (preliminary, door-to-door 0, 2 pending), v01 record kept, 7 labelled decisions, 4 resolved ones removed
PASS Production view: gates, ledger and decisions cards in order after the rule card, bilingual labels, 9/12 gates implemented in their own group and M2 not complete, no runtime-pending badge left, counters 0/52 0/11 0/2 and 51/52, two scoped approvals, no controls; raw paths only in collapsed sources; 28 evidence files served byte-identical, 8 evidence probes 404; two design docs served byte-identical, 4 probes 404
PASS hostile gate/ledger/decision fields and unsafe evidence paths render escaped or as a safe fallback; a state without the new fields omits the three cards and still renders
RESULT PASS (5 checks)
```

The other Game Bible Node checks also exit 0 against the edited state and app:
- character readiness: `RESULT PASS (7 checks)`;
- enemy pilots;
- environment candidates;
- paving A/B;
- selout v2/v8: `RESULT PASS (14 checks)`.

## 7. Sync preparation (2026-10-15, before the push to origin/main)

- **Rename.** The Loop placeholder scene and script now follow the project naming pattern:
  - `game/scenes/chicago_loop_district.tscn` → `game/scenes/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.tscn`
  - `game/scripts/chicago_loop_district.gd` → `game/scripts/rpg-2-star-ocean-the-second_chicago-loop_district-placeholder-scene_m2-v02_20261015-185645-a7d62ba0.gd`

  Updated references: the scene's script `ext_resource`, `AppState.AREA_SCENES`, the core smoke (…a19d5ae7), the visual capture (…9b2fac94) and the US migration smoke (…5ffdb1e9). The script has no `class_name`, so nothing else refers to it.
- **Line-ending fix.** The route-card readability check failed 3 of 109 checks on a `core.autocrlf=true` checkout of the staged tree: the English Yonkers and Washington cards were 248 px tall instead of at most 238 px. The cause was three string literals in `game/scripts/scifi_world_map.gd` (card subtitle, route option arrival line, route option notes) that contained a raw line break. A CRLF checkout turned each break into `\r\n`, which added a line. They now use the `\n` escape. LF behaviour is unchanged. The pattern was already in HEAD, so it was latent before this batch.
- **Evidence paths.** The sync stages no screenshots, so on a clean checkout the 9 Great Lakes / US Northeast map captures (`outputs/…_m2-v02_20261015-182538-30506f07.png`) would be missing. The Game Bible M2 gate check requires every evidence path to exist. Those 9 PNG paths were removed from the `map-ui`, `route-preview` and `air-route` evidence lists in the mvp-progress state. Each gate still cites its QA notes, and the [Great Lakes capture QA note](rpg-2-star-ocean-the-second_global-earth-map_great-lakes-chicago-capture_qa-note-unapproved-v01_20261015-182538-30506f07.md) still lists the captures. The PNGs stay local and untracked. The check was not relaxed.
- **Re-run.** After both changes, the Godot and Node checks were re-run on an export of the exact staged index (CRLF checkout). See the commit message for the result lines.
