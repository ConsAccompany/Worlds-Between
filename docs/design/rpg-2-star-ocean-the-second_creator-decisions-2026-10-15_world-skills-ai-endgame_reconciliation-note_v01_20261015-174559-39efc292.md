# Creator decisions 2026-10-15 — design reconciliation note

- Date: 2026-10-15 (recorded 17:45 local / 21:45 UTC)
- Kind: **design-record reconciliation only.** No runtime code, game data, tool, test or art file was changed. Nothing in this note is implemented in the Godot game.
- Authority: the decisions below were given by the creator in chat and are recorded as **creator-approved design decisions**. They supersede the provisional Shanghai / Songjiang / Liangzhu science-region geography and every earlier wording that conflicts with them.
- Files reconciled in this pass (only these):
  - `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`
  - `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`
  - `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js` (UI labels that hard-coded superseded wording)
  - `docs/progress.md`
- Counters are unchanged: exploration sprites **0/52**, science scene quality **0/11**, human timed playtests **0/2**; 51 identities / 52 visual variants. **M2 stays in progress** until the runtime follows these decisions and humans have reviewed it.

## 1. World and geography

| Topic | Creator decision |
|---|---|
| Map | Global Earth map with real place names (rule of 2026-10-14 kept). |
| Adventure start | **2537-05-25** (start of the formal adventure). The one-year training prologue precedes it; its own start date was not given. |
| Underground community | Near the **Catskills** (New York State). |
| Science civilization | United States + Canada; hub **New York City (NYC)**. |
| First playable area | **Lower Manhattan — City Hall Park**. |
| Outskirts | **Yonkers**. |
| Washington, D.C. | The whole city is abandoned. The **U.S. Capitol grounds** are recognizable, partially collapsed and overgrown. An active science survey outpost and patrol automata operate there. Washington is the **high-precision Pixelorama scene pilot**. |
| Liangzhu | Remains a **future Asia / Wuxia scene, not MVP**. Its accepted terrain direction and its Pixelorama workflow permission stay on record for that future scene. |
| First air route | **NYC – Chicago**. |
| Chicago in MVP | One playable district: **the Loop**. |

### Five Earth civilization spheres

| Sphere | Region | Hub | Notes |
|---|---|---|---|
| Science | United States + Canada | New York City | First chapter. |
| Magic | South America | Manaus (马瑙斯) | Light and dark leaders are co-located there. |
| Wuxia | Asia | Chongqing | New sphere. |
| Nature | Oceania | Brisbane | |
| Culture | Europe + Africa | Dual hubs **Athens** and **Cairo** | The former "Fantasy" sphere. An alien-descendant culture centred on memory, knowledge and inheritance. |

- Mexico, Central America and the Caribbean are **mixed borderlands** with side content. They are **not** a sixth mainline.
- **Antarctica** is DLC.
- The **final other planet** is reached by **portal** after all **five** Earth mainlines. It is separate from the five spheres; the old fifth board "Exterritorial / 星外" is no longer one of the five.

## 2. Jobs and skills

- The **20 job series** roster is accepted.
- **Every existing five-stage name and every `finalQuest` text** in the Game Bible JSON is approved **unchanged**. This pass did not edit them. A SHA-256 over `jobProposal.series` is identical before and after this pass (see §7).
- New skill rules:
  - All branches are eventually learnable (no exclusive branch choices).
  - Each skill has **max rank 5**, raised with JP.
  - Each job series has **10 nodes**: **exactly 2 unlocked immediately at each of 5 tiers**.
  - Each of the **51 character identities** has **10 personal nodes**, all reached by **personal level 100**. Each has **at least one exclusive personal skill immediately on joining**. Personal skills are always usable, whatever the current job.
- **Superseded drafts:** the existing 20 seven-node job trees (rank max 3) and the 16 five-node personal trees (rank max 3) are **superseded drafts**, not approved 10-node designs. They remain in the JSON as reference and are marked **pending redesign**. The approved structure needs 20 × 10 + 51 × 10 = **710 nodes**. This pass wrote **none** of them.

## 3. Battle AI and combos

- AI uses **no consumable items by default**. A per-character strategy may allow them.
- Heal / revive skill AI targets **downed allies first**, then **urgent healing**.
- **Combo AI is off by default.** It can be enabled in auto battle.
- **Every participant pays energy** for a combo.
- Each pair of characters has a **relationship score 0–100 plus named stages**. Scores can fall and recover.
- Combos **unlock automatically** when the relationship and current-skill conditions are met. The menu **describes the conditions**.

## 4. Reputation

- Five dimensions, with the creator-approved Chinese names as canon: **求知 (inquiry), 果敢 (resolve), 共情 (empathy), 公正 (fairness), 守诺 (promise-keeping)**.
- The same five dimensions apply worldwide and per sphere, **with different weights per sphere**.
- The game keeps the **actual behaviour record** separate from **NPC perceived reputation (rumour)**. Evidence or action can correct the perception.

## 5. Commerce

- Price effects of discoveries **start locally** and **propagate over established trade routes**.

## 6. Endgame and missable content

- **2 repeatable, adjustable-difficulty scenes in each of the 5 Earth spheres, plus 2 on the final planet** (12 total).
- **5 fixed difficulty tiers**, all **selectable immediately**. Every tier gives the same reward types; higher tiers give larger quantities and higher drop rates.
- **No missed content.**
- The 10 romance identities and their stages stay **deferred**. Quality acceptance is pending.

## 7. What this pass changed, and what it did not

Changed (design records only):

- Game Bible JSON: new `creatorDecisions` block. Updates to facts, open questions and chapters 1–9, written to match §§1–6. The job / personal skill-tree drafts are marked superseded and pending redesign, with the approved rules attached. `environmentVisualReview` records Liangzhu as future Asia/Wuxia (not MVP) and Washington, D.C. as the designated Pixelorama pilot (not authored).
- MVP progress JSON: M2 summary, remaining items and blocker. The M2 `anchor`, `start-year` and `air-route` gates are now `decided_runtime_pending`. The pending-decision list drops the four resolved items (first city, community anchor, start year, air-route pair) and the superseded Songjiang label, and adds the open follow-ups. A new `designDecisions` pointer refers to this note.
- App UI: labels that hard-coded the superseded wording now match the data. These were the 7-node / 5-node / rank-3 captions, "proposal pending" on approved job names, "first city and start year await the user", and the board filter labels.
- `docs/progress.md`: a new dated entry and summary wording.

Not changed:

- Game runtime (`game/`), tools, tests and art. The game still uses the **superseded provisional** Shanghai / Songjiang Outskirts / Liangzhu place set, the Yangtze Delta regional layer, Rome2Rio estimates for those routes and the **2026-04-01 08:00** calendar placeholder. NYC, Yonkers, City Hall Park, Washington, D.C., Chicago and the NYC–Chicago route are **not in game data**.
- Character records. The 50 companions still carry their old board labels (科技 11, 自然 11, 奇幻 11, 魔法 10, 星外 7). No companion is assigned to Wuxia yet, and Culture is shown as 奇幻 data. Reassignment is a pending character-design task. The UI labels 奇幻 as "文化（原奇幻）" and 星外 as "终局星球（原星外）" without changing the data.
- Acceptance counters, approval-ledger statuses and art.

## 8. Follow-ups opened by these decisions (not decided here)

1. **Runtime geography migration:** replace the Shanghai set with NYC (Lower Manhattan City Hall Park), Yonkers outskirts, the Catskills community, Washington, D.C. and the Chicago Loop. Add the NYC–Chicago air route with sourced figures. Set the new-game date to 2537-05-25 (the prologue start date is still needed). Migrate saves.
2. **Skill redesign:** write the 200 job nodes and 510 personal nodes to the approved rules. Set JP costs for ranks 2–5.
3. **Companion re-mapping:** assign companions to the five spheres (including Wuxia) and the final planet. Review the old Fantasy trait wording (myth-inspired bloodline traits) against the new Culture definition.
4. **Final planet:** set its minimum content scale. The old minimum of "5 cities / 5 communities / 5 field scenes per board" now applies to each of the five Earth spheres.
5. **Mainline order:** the old rule was "after the Science first chapter, the other boards are in free order". Carrying it to the four other spheres is an extension of that rule and still needs creator confirmation.
6. **Numbers still open:** relationship stage names and thresholds, reputation weights per sphere, difficulty multipliers per tier, and AI strategy presets.
7. **Washington, D.C. pilot:** scene brief and Pixelorama production. Not started, art acceptance 0.
8. **Stale test expectation:** `tests/game-bible-m2-global-travel/…_check_m2-v01_20261015-064400-06efaa9b.js` asserts `anchor` / `start-year` = `awaiting_decision` and `air-route` = `research_only`. Those expectations now describe superseded state. The test owner needs to update them; this pass did not edit tests.

## 9. Wording corrections (2026-10-15, after visual review of the Game Bible World page)

Text-only fixes in the Game Bible JSON. No world or skill rule, counter, approval status, runtime file or test changed.

- **Reputation names:** the earlier pass wrote 好奇、勇气、同理 in place of the approved names. All occurrences now read **求知、果敢、共情、公正、守诺** (chapter 2 body, the open-question detail and `creatorDecisions.reputation.dimensions`).
- **Manaus:** the Chinese name is **马瑙斯**, not 玛瑙斯. All four occurrences are corrected (chapter 2 sphere table twice, the open-question detail and `creatorDecisions.spheres`).
- **Pausing in battle:** chapter 3 said "暂停时间可选择技能，也可向队友临时下指令", which could be read as any character pausing. It now states the existing rule: only the character the player is directly controlling can pause time. While paused, the player picks that character's skills and can give temporary orders to the other party members. AI-controlled party members cannot pause.

## 10. Integration update (2026-10-15, after the US runtime migration)

This section updates the §8 follow-ups. The decisions in §§1–6 are unchanged.

- **§8.1 Runtime geography migration: implemented as a technical candidate.** See the [US migration QA note](../qa/rpg-2-star-ocean-the-second_us-science-sphere_runtime-migration_qa-note_m2-v02_20261015-175011-364131c8.md) and the [integration QA note](../qa/rpg-2-star-ocean-the-second_five-sphere-registry-and-us-runtime_integration-qa-note_m2-v02_20261015-184437-b3b84617.md).
  - Now in the runtime: NYC (City Hall Park), Yonkers, the Washington, D.C. Capitol ruins, NYC–Chicago with a placeholder Loop district, and the 2537-05-25 start.
  - The travel region registry now has the five Earth spheres plus the portal-only final planet. `fantasy` survives only as a legacy alias of `culture`.
  - Still open: the art, release-grade route figures, a runtime place for the Catskills community, and human review.
- **§8.3 Companion re-mapping, partly resolved.** Culture is the former Fantasy sphere renamed, so the old 奇幻 board label maps directly to Culture and 星外 maps to the final planet. That leaves no question about whether the old Fantasy description carries over. The remaining design work is giving Wuxia companions.
- **§8.5 Mainline order: not an open question.** The earlier user rule already says that after the Science first chapter the other independent mainlines have no fixed order. That rule covers all four other Earth spheres.
- **§8.8 Stale test: updated.** The M2 gate check now expects the `anchor`, `start-year` and `air-route` gates to be `implemented`, and cross-checks them against the active v02 travel data.
- **Still open:** the prologue start date; whether old 2026-dated saves shift into 2537; the 710 skill nodes; relationship stage names and thresholds; reputation weights per sphere; difficulty multipliers; AI presets; the final planet's content scale.
- **Endgame scope:** 2 repeatable scenes per Earth sphere plus 2 on the final planet is full-game content, not MVP.
