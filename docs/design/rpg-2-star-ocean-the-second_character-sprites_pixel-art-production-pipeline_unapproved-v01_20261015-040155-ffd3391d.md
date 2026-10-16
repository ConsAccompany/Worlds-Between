# Character sprites — high-precision pixel-art production pipeline (design, UNAPPROVED v01)

- Scope: 51 identities / 52 variants (`protagonist` has male + female), per the readiness ledger
  `game/data/character-visuals/…readiness-checklist_m8-v01_20261014-184413-53da3710.json`.
- Starting point: the **only** user-approved art — female south idle static **v8**
  (`game/assets/characters/pixelorama-pilots/…south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`,
  decision doc `docs/character-visuals/…south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md`).
  Approved = static south frame at 48 logical px only. Nothing else (animation, other facings, runtime swap) is approved.
- The 32×48 placeholders are **rejected** as an art baseline. Do not trace, upscale or reuse them for pixels.
- **Permission boundary:** Pixelorama use is permitted **only for the female, one-direction (south) pilot**.
  It does not extend to other facings, other characters or environment work. Every later phase in §7 needs a new, explicit user go-ahead.
- Status: process design only. This note edits no art, runtime, tracker, counters, progress or Git. It claims no visual approval.

## 0. Verified environment (2026-10-15)

| Item | Result |
|---|---|
| Claude auth | `claude auth status`: claude.ai, firstParty, `subscriptionType: max`, no `ANTHROPIC_API_KEY`. No paid or credit route is used. |
| Pixelorama | `work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe` → `--version` prints `v1.2.3-stable` (`work/` is gitignored). |
| Pixelorama CLI | **Verified headless round-trip.** `Pixelorama.exe --headless --quit -- --export -o <dir>\f.png <pxo>` on the Python-written w01 walk `.pxo` gave 8 × 80×112 PNGs that are **pixel-identical** to the builder's PNGs. `--spritesheet` gave 640×112. `--size` / `--framecount` work. Source `.pxo` SHA unchanged. |
| CLI caveats | (a) The `-o` basename is ignored: files come out as `<project-name>_000N.png` in the `-o` directory. Always export to an empty temp dir, then rename by script. (b) Each run rewrites `current_dir` in `%APPDATA%\pixelorama\config.ini`. Back it up and restore it; this probe did. (c) Each run takes about 3.4 s to open. |
| Godot | `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`. Capture scenes run **windowed**, because headless capture can hang. Not re-run for this note. |
| Python | `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` (3.12, Pillow, NumPy). Run with `-I`. |
| Runtime | 640×360 viewport, `canvas_items`, integer stretch, nearest filter. The hero is a `Sprite2D` swapping preloaded 32×48 textures; there are no `SpriteFrames`. The 80×112 cell at scale 0.5 gives 48 logical px, so 1 texel = 1 window px at 1280×720. |

## 1. Source and editable format

1. **Master cell:** 80×112 RGBA, binary alpha, ground pin (40,104), body height 96 ±1 texels, display scale 0.5, nearest filter, no opaque texel on the border. This matches v8: 43×96 visible, alpha bounds (13,8)–(55,103).
2. **Editable source = one `.pxo` per variant × direction × action.** For example, `…_protagonist-female_south-walk-editable_<ver>_<stamp>-<id>.pxo`. Pixelorama frames are the animation frames.
   - Use one `.pxo` per action, not a mega-sheet. This keeps the CLI export and frame→file mapping 1:1, and follows the existing "one image per file" rule.
3. **Fixed layer stack**, top to bottom. These are role layers, so the identity texels stay copyable and auditable:
   - `guides` (hidden, never exported: pin, 96-row line, cell border)
   - `fx` (optional)
   - `hair-front`, `head-face`, `arm-near`, `torso-coat`, `accessory`, `legs`, `boots`, `arm-far`, `hair-back`
4. **v8 has no `.pxo` today.** v8 was made by a Python recolour of v7. Step 0 of the pilot is a deterministic Python writer that splits the v8 PNG into the role layers and writes a v8 `.pxo`. Use pxo_version 7 with fixed zip timestamps, like the run-v3 builder. Gate it on the v8 `sha256-bytes` lock. Then prove it with the verified CLI round-trip: the flattened export must equal v8 byte-for-byte at the texel level.
5. **Hand edits happen in the Pixelorama GUI** (pilot only). The edited `.pxo` is re-exported by CLI. PNGs are **never** hand-edited directly.
   - A diff script logs every changed texel against the pre-edit export. The log goes into the manifest (`hand_edit_log`). This keeps E6 measurable.
6. **Never overwrite.** Every save is a new uniquely named file:
   `rpg-2-star-ocean-the-second_<visual_id>_<direction>-<action>-<part>_<milestone-vNN>_<YYYYMMDD-HHMMSS>-<8hex>.<ext>`.

## 2. Pose and animation template

**Frame counts are not approved.** The ledger says "20 = placeholder layout, 48 = pilot proposal". The batch gate needs explicit user approval of counts after one variant passes intake stage 4. The tiers below are a **proposal** to put to the user.

| Tier | Who | Set per variant |
|---|---|---|
| A (all 52) | everyone | S/W/N/E static idle; S/W/N/E walk 8 (contact, down, passing, up × 2 legs, as in the w01 phase names) |
| B (party) | 2 protagonists + 15 main | Tier A + run 12 (locomotion v2) or 16 (run v3r2; the count is itself pending) + 2–4 frame breathing idle |
| C (combat) | combat-capable roster | side-view 8 actions per the existing combat layout (20 frames placeholder), done later and separately |

- **Locomotion rules** are carried over from w02/v3r2:
  - distance-keyed frame stepping at `MOVE_SPEED 140`
  - root lock with exact fractions
  - stance-foot drift ≤1 screen px per tick (E8)
  - head and torso rows copied from the static idle and moved only by the declared bob
- **East is never a blind mirror of west.** Mirroring is allowed only when the variant's `asymmetric_details` list is empty and the user signs off. Side braids, scarf tails, holsters and the knee guard all break mirroring. The run-v3 `--check` already gates "no mirrors".
- **North facing is authored, not derived.** Hair-back carries most of the identity there (§5).
- **Pose template file:** one `guides` layer per direction, holding the pin, head-top row, shoulder row, hip row, knee row and sole row taken from v8 south. Later identities reuse the template rows, not the v8 texels. That avoids cloning the female's body onto everyone.

## 3. Palette and silhouette gates (machine-checked, block on failure)

| Gate | Rule |
|---|---|
| P1 alpha | 0 partial-alpha texels; nothing opaque on the cell border |
| P2 palette cap | ≤48 colours per variant (v8 uses 32). Every animation frame ⊆ that variant's idle palette |
| P3 declared palette | Each variant ships a palette JSON of named ramps (`skin`, `hair`, `coat`, `trim`, `boots`, `metal`, `selout`) with hex values. Unknown colours fail |
| P4 ramp value spacing | Adjacent ramp steps differ by ≥ the v8 minimum Lab L* step. Measure that from v8; do not invent a number |
| P5 scene contrast | Silhouette-edge texels vs each review background: report CIELAB ΔE, as the v8 QA scenes already do. A threshold is proposed only after v8's own values are recorded as the reference |
| S1 height / pin | Idle body 96 ±1; walk −3/+1 (E4); sole row on pin y=104; torso pin x drift 0 (E3) |
| S2 identity rows | Rows declared "locked" (head and hair) equal the idle master after integer offset (E1) |
| S3 silhouette read | Solid-black mask render at 1 texel = 1 px for every frame. Fails if the head+hair mask differs from the variant's own idle head mask beyond the declared bob (catches hair drift between frames) |
| S4 cross-identity separation | Pairwise IoU of head+hair masks (rows 8–~40, at matched pin) for every pair in the ledger's `hair_review.candidate_confusion_groups`, **for S and N facings**. Report the value; the user decides. No threshold is set until a pair is user-judged "distinct" or "confusable" |
| S5 determinism | Re-running the build and CLI export gives byte-identical PNGs (E7) |

## 4. Visual review at true game scale (human gate, never automated)

1. Use the existing windowed Godot capture scenes (`--motion-dir=…`), not zoomed editor views. Review in three backgrounds:
   - **bright:** `scifi.city`
   - **bright:** `scifi.outskirts`
   - **dark:** survey annex room 2, floor darkened 0.10
   - Optional: ruins.
2. Capture at **1280×720**, the reference where 1 texel = 1 px. Also capture at **1920×1080 / fullscreen**. With integer stretch, a 0.5-scale sprite at a 3× stretch is 1.5 px per texel and may sample unevenly. **This is unverified and must be checked before any runtime decision.**
3. Each review packet holds:
   - the true-scale captures
   - a 4× nearest preview (written outside `game/`)
   - side-by-side with the approved v8 capture and the rejected 32×48 placeholder for scale reference
   - for motion, a looping capture at real speed
4. Only the user may answer. Record the reply verbatim in a decision doc, and hash-lock it like the v8 decision. Manifests keep `art_approved: false`; the decision doc is the approval record.

## 5. Identity and hair differentiation

- **Anchor source:** `identity_and_hair_anchor` per variant in the ledger. 7 variants have no hair anchor (huan-7, suiya, zhongdu, menling, lingbing, lengjing, yuyin). They need a non-hair identity anchor (headgear, mask, shell or silhouette mass) agreed with the user **before** any pixels.
- **Per-variant identity card** (text, before pixels):
  - hair mass shape from S and N
  - part line
  - braid count, side and length
  - 2 signature colours (hair + one costume accent)
  - one asymmetric detail
  - which rows are "locked identity rows"
- **Confusion groups to resolve first:**
  - chin-length straight: nalia / yelan
  - single side braid: nalia / gu-lin
  - single long braid: muxiu / mi-yi
  - twin braids: adi / isai / ruan-tian
  - low coil or bun: liang-xu / heya
  - …and the rest of the groups in `hair_review`
  - For each group, do silhouette thumbnails (S3/S4) plus a colour-swatch row **before** full production. Differences must survive in the **north (back) view at 48 px**. Colour-only separation is not enough for pairs flagged in the ledger.
- **Male vs female protagonist** share the `protagonist` identity. They must differ in silhouette mass (shoulders, hair) and not by recolour alone.

## 6. Per-variant outputs

Folder: `game/assets/characters/<visual_id>/<set>-<milestone-vNN>/`. It holds a `.gdignore` until the user approves runtime integration, as the run-v3 builder does under `game/`.

| Output | Content |
|---|---|
| `…-editable_….pxo` | one per direction × action, with the role layers from §1 |
| `…-fNN-<phase>-<leg>_….png` | per-frame 80×112 exports, from the CLI only |
| `…-palette_….json` | the named ramps from P3 |
| `…-manifest_….json` | `visual_id`, `identity_id`, cell/pin/scale/filter, `derived_from` (v8 path + sha256-bytes), source `.pxo` sha256-bytes, frames[] (file, phase, sha256-bytes), `hand_edit_log`, gate results, `pending_visual_decisions`, `art_approved: false` |
| `…-qa-report_….json` | P1–P5 and S1–S5 values, plus E8 drift numbers |
| review captures | 1280×720 and 1920×1080, three scenes, in `docs/qa/` or `outputs/`, PNG `sha256-bytes` |
| test | per-set `--check` mode (deterministic, exits 1 on failure), plus a unittest under `tests/<visual_id>-<set>/`, plus the premium exploration validator on the manifest |

- Hash locks: `sha256-bytes` for PNG and `.pxo`; `sha256-text-lf-v1` for JSON and MD.
- The readiness ledger is regenerated only through its own `…readiness_build-and-check…py --write`, after a user decision. It is never hand-edited.
- **Existing debt:** `tests/protagonist-female-south-run-v3/…7e6c5e0d.py` still expects the pre-r2 names (`run-pilots-v3`, stamp 034327), while the builder is now r2. It is likely stale; reconcile it before the run set is reviewed. Not run here.

## 7. Realistic solo sequencing

Each phase ends with a user review. **Phases 1+ need new explicit permission**, both to use Pixelorama and to touch more facings or characters.

| Phase | Work | Rough effort (unverified estimate) |
|---|---|---|
| 0 — female south pilot (permitted now) | v8 → role-layer `.pxo` writer + CLI round-trip proof; finish south walk/run from w02/v3r2 with a logged Pixelorama hand-fix pass; P/S/E gates; true-scale bright and dark review | 2–4 sessions |
| 1 — female W/N/E (needs permission) | static idles first (west authored, east authored or mirror-approved); then walks | 3–6 sessions |
| 2 — counts and template freeze | user approves frame counts and tiers (§2); intake stage 4 passes; pose-template rows frozen. **Batch gate opens here only** | 1 session |
| 3 — second and third variants | protagonist-male (same identity, different body), then one main with a confusion-group partner (e.g. liang-xu vs heya) to prove S4 | 4–8 sessions |
| 4 — waves | main 15 → side 15 → situational 20, in waves of 3, Tier A first; Tier B only for the party | a Tier A variant is about 36 frames. At the v8 pace (8 iterations for one frame) and on the order of 1 h per derived frame, plan **~30–50 h per Tier A variant**. 50 more variants is a **multi-month** solo effort |

- **Scope lever:** if that total is too large, the user's options are Tier A only for situational characters, or fewer walk frames for non-party characters. Both are user decisions, not defaults.
- **Stop rules** (from the pipeline memo):
  - any gate still failing after 2 iterations → stop and report
  - E6 hand-edit budget blown → limbs need a hand-drawn path; ask
  - E8 fails → offer stride or speed change; do not proceed silently

## 8. Not verified / open flags

- **Pixelorama GUI editing:** not exercised in this session. Unknown whether a GUI-saved `.pxo` (as opposed to a Python-written one) round-trips pixel-identically through `--export`. Test this once in phase 0.
- **Palette import:** whether Pixelorama 1.2.3 imports `.gpl` or `.json` palettes and keeps the project palette inside the `.pxo` was not tested. Also untested: `--json`, `--split-layers`, and what the `--direction` values mean.
- **Display at non-1280×720 window sizes:** not captured.
- **Godot capture scenes:** not re-run for this note.
- **Effort figures:** guesses, not measurements.
- **Pixelorama.exe signature:** reported as unsigned by an earlier review; not rechecked here.
- **No visual judgement was made** by the author of this note. Nothing here is approved.
