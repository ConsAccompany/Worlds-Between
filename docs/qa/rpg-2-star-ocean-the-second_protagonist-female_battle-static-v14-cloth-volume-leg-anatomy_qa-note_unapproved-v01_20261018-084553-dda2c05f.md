# Female battle static v14: cloth volume, leg and boot anatomy (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame.** No animation. The runtime, `battle_arena.gd`, the Game Bible, the ledger and every counter are unchanged (40.8%, M2 10/12, scenes 3/12, sprites 0/52, plays 0/2). Nothing is staged, committed or pushed; Codex reviews first.

Auth: Claude Code, Opus 5.5. `claude auth status` reports claude.ai / firstParty / max. No quota or auth block was hit.

Worktree: `work/max0840-battle`, branch `codex/battle-static-v14-20261018-0840`, base `160b823`.

## Brief

The root review of v13: the pack and roll form is modestly better, but:
- the silhouette is overly busy and hard-edged;
- the boot masses are thick;
- the lower body still merges into the dark floor;
- part of v12's full coat was lost.

The creator's standing request on this frame is "继续精修静止帧" (keep refining the static frame). That is not an approval.

Constraints kept from v13:
- 68×72 cell, pin (32, 68), crown row 7, sole row 67: the approved 0.65 battle display proportion;
- bbox [15, 1, 60, 67], blade reach (tip x60);
- face, hair, teal scarf and slate coat identity; no heavier head and no shorter legs;
- real four-person draw order and the radius-18 contact shadow.

## What changed

The v14 author tool is a bounded fork of the v13 tool. v13's tracked files are hash-locked, read-only and untouched.

Unchanged from v13, gated byte-identical (13 layers): ponytail, loose lock, coat torso, shirt, near arm, insignia, blade, guard, fist, hair band, collar, scarf, collar front. The head outline is identical. The palette is v13's 31 keys exactly, with none added or removed.

Changed (7 layers + 1 new layer):

**Coat skirt (back tail):** v12's fullness is back, without v12's black wedge.
- It reaches x17 and row 54 (v13 x18 / row 53, v12 x16 / row 56), at 162 texels (v13 134, v12 156).
- It is shaped as hanging cloth:
  - a shadowed back edge (C);
  - a mid-slate body (c);
  - **one** broad fold from the belt toward the back corner, with a dark flank (C) and a lit ridge (o);
  - a lit split edge;
  - a dark-leather hem (l) rising in one diagonal toward the split.
- Visible tail deep slate (C) is 36 (v12 98, v13 24); mid plus lit (c + o) is 82.

**Legs:**
- The near knee juts 2 texels forward of the shin (v13: 0, one straight column). The knee pad sits on the knee front, and the shin drops back to the ankle.
- The far leg is braced back with a small knee bend. It sits in the body's shadow: deep slate body (C), spruce (T) and a lit spruce front edge (t).
- 7 transparent columns separate the shins, and 5 separate the boots.

**Boots:**
- The shaft is as wide as the shin: 5 colour texels (v13: 7–8).
- Max boot width is 10 (v13 13); boot texels on rows 57–66 went from 93 to 77 (far boot) and 93 to 73 (near boot).
- Anatomy: a dark cuff band where the trouser tucks in, a heel that steps back one texel, and a vamp that slopes to a rounded toe.
- Values:
  - dark leather (d) on the paving;
  - a lit vamp and toe cap (D, plus one warm-grey u texel);
  - inside the real shadow ellipse, only the lowest foot row and the welt are lit leather (D): 2 rows.
- v13 had a 3–4 row lit band plus a full-width warm-grey welt.

**Restrained warm planes:** the existing warm grey `u` appears on 10 texels in total, all on light-facing planes (near thigh top, near shin front, toe caps).
- Gate: every new silhouette-edge texel is black outline. The only non-black edge texels are v13's own (in unchanged art) and the declared deep-teal top edge of the roll.
- So there is no rim light, glow or bright outline.

**Pack, canister and drape:**
- Pack: v13's slumped-sack outline, with the face calmed to one lit flap, one curved flap edge with a pale buckle, one strap and a shadowed back edge.
- New `canister` layer: a small steel canister (6 steel texels) on the pack's visible side, inside the pack's outline, so the silhouette does not change. It is a character-sheet / v8 identity item; v05–v13 had none.
- Hip drape: tucked under the pack bottom so the back contour runs pack → drape → tail. v13's drape stuck out of the silhouette at the hip as a tab. Visible teal: 13 → 10.

**Roll:** v13's cylinder (end-cap ring around a dark core, bowing binding) is unchanged except that its top edge is outlined in deep teal (Q) instead of black.

**Face (mature read):** only 3 brow-row texels are recoloured:
- the brow is hair brown and ends one texel before the eye's front;
- the eye becomes a smaller lash line over the pupil and eye-white;
- dark eye/brow texels (E): 6 → 3.

Head alpha is identical to v13.

Totals:
- 1621 → 1590 texels (−1.9%);
- silhouette IoU 0.912 (58 added, 89 removed);
- 429 composite texels changed;
- width without the sword arm: coat-skirt band 28 → 30, lower body 35 → 32, boots 35 → 29;
- sole-row stance x21–29 / x38–46 (v13 x19–30 / x38–50).

## Files (all new, untracked)

| file | sha256 |
|---|---|
| `game/assets/characters/combat-sideview-pilots/…static-native0p65_unapproved-v14_20261018-084553-336f663b.png` (68×72 RGBA, binary alpha, Pixelorama 1.2.3 flat export of the .pxo) | `86286082c59d923e27fdf572a616467e9acfb2912d55c7b639167c8789ae43dc` |
| `…editable-layers_unapproved-v14_20261018-084553-8a0ff314.pxo` (pxo_version 7, 21 layers + hidden locked guides) | `8a424e58178cb770e76604262f2f0cce9634f1aa4a2cc933689460e456e4e6e3` |
| `…editable-layers_unapproved-v14_20261018-084553-90f4f22b.ora` | `d0688be291b79d24ad14a8f81bf7c59e65e9199f01f53765baa37708cb307fe5` |
| `…manifest_unapproved-v14_20261018-084553-5bf8c74a.json` (`art_approved` false, `runtime_integrated` false, pose gates, v14 targets) | `38d044ac79e41320eea55fc78f2be6be1891f0bc85488208488459c6d214a219` |
| `tools/…native-0p65-author_unapproved-v14_20261018-084553-8e0b84ca.py` (fork of v13's) | `603fb65f79fd9943ad71c3c038623c5bdc1bde7258a7d7a07a8e71a1d14d9c81` |
| `tools/…native-0p65-party-capture-probe_unapproved-v14_20261018-084553-2c7e5a90.gd` (v13 probe + optional 11th arg `zh`/`en`) | `720c8377794ac65458ab203fa664b483ffc76ec1022ef31419c676359f2457a3` |
| `tools/…battle-static-v13-vs-v14-capture-measure_unapproved-v14_20261018-084553-6d41b8e3.py` (read-only) | `9ffcc6e14c6278003fcfe13a909b70de267c330f62cf485022b81a3b530887c4` |
| `tools/…battle-static-v14_isolated-head-tree-verify_unapproved-v14_20261018-084553-4f92c1d7.py` (read-only) | `0ef2e719b3b1126992fc119d097ebc8601e65944a6149f2e37ab7e79cfaafb5f` |
| `outputs/…battle-static-v14_isolated-160b823-check-and-measure-report_unapproved-v14_20261018-084553-36497cfe.json` | `6b770ab0ec6ecbcb75105378d11cbe0f832727a79e076bee769c7d9633826808` |

Captures: 640×360, 1×, real Godot 4.7.2. Each PNG has a manifest next to it with the same stem plus `-manifest`.

| capture `outputs/…party-capture-<floor>-640-probe-<lang>_unapproved-v14_20261018-084553-<id>.png` | sha256 |
|---|---|
| archive (bright) zh `5a0ec9d0` | `775803bfb013097db6450605548018f7e56c8bcc601f17849ff993518f92b414` |
| archive (bright) en `7c83e367` | `1ddd41235a53f345b6ff9ea41cfe9bd89fd482900cdedaf6077b9046c75970c1` |
| outskirts (dark) zh `f1b7abb6` | `cd750d835665b98477efd89a73a3d2d1faf2416d7b80e65d7fe0a78599631d6b` |
| outskirts (dark) en `cb540bbe` | `b2595418166a3bb72423005eeb9900fe4d2a78441bb9ea7ba537a95f8df0fafc` |
| head-geometric (HEAD's own floor) zh `a1d47b82` | `6a782be4da2fa9e965416707b1b0fc3d06f239c2001748a856f780a83a907b9e` |
| head-geometric en `0de3077a` | `a17fa97e625b0ce5c229f165d631c83a01b8e49946bd06efa063a1061ba316b0` |

Manifest IDs: archive zh `d10727aa`, archive en `e98ece9f`, outskirts zh `9efc4ba0`, outskirts en `bc4c2664`, head-geometric zh `2d3ba36f`, head-geometric en `0939a5f0`.

## Evidence

**Isolated HEAD tree** (`%TEMP%\fv14iso`, throwaway):
- built with `git -c core.autocrlf=false archive 160b823 game` plus exactly the 6 enumerated files: the 4 sprite files and the author and capture tools.
- The verify tool passes **before** the Godot runs:
  - all 1760 HEAD `game/` files are present and byte-identical to their git blobs;
  - the enumerated files are identical to the worktree copies;
  - there are no other files.
- It also passes **after** the runs. The only additions are Godot import products: 875 under `.godot/`, 54 `.import` and 37 `.uid`, with 0 unexpected files.
- `battle_arena.gd` is HEAD's blob (sha256-LF `e9737c40…`, as in v13). **No dirty or band-capable `battle_arena.gd` was used.** This worktree is clean apart from the new files.
- The two band PNGs are **tracked at HEAD** (since 7553581) and were read inside the tree:
  - archive `c840e071…`
  - outskirts `feea6297…`
- No external input was used apart from the Godot and Pixelorama executables.
- A fresh tree needs one `--headless --import` before the `-s` script can see the global `SaveStore` class. The first attempt failed with exactly that parse error; after the import, it ran.

**Draw order and shadow:** the v14 capture script's `probe` mode was used. Its in-memory subclass source is byte-identical to v13's (`subclassSourceSha256 7424a306…`).
- Floor, then radius-18 contact shadows, then every fighter through the real `_draw_fighter` in fighter order, then the real `_draw_enemy`.
- **Self-check passed in all 6 runs:** with no floor texture and radius 0, the probe frame is byte-identical to HEAD's own `_draw()`.
- Companions draw over her, and 0 candidate texels are hidden.

**All 6 runs report CAPTURE PASS:**
- 1590/1590 sprite px, 0 off-palette, nearest 1.0, static re-grab;
- crown y211, sole y271 (61 logical px), bbox x283–328, all identical to v13;
- Liang gap 5 px, 0 opaque overlap with every companion;
- the HUD is Chinese in the zh runs and English in the en runs.

**Fidelity (measure tool):**
- In all 6 captures, the v14 PNG composited at (268, 204) over the run's no-sprite frame equals the Godot capture exactly.
- Only the 1590 sprite texels differ.
- The zh and en captures give identical sprite-region numbers.

**`check`:**
- In the worktree, with APPDATA redirected to an empty temp dir: **PASS 63/63**.
  - Static gates.
  - Manifest hashes and UNAPPROVED flags.
  - Byte-identical rebuild.
  - .pxo/.ora stack recomposition and merged image.
  - Pixelorama 1.2.3 headless flat export equals the PNG; split export 21/21 for both formats, with no guides exported.
  - Real Pixelorama APPDATA untouched (the user's GUI was not touched).
  - v13 lock before and after.
  - 35 pose gates.
- In the isolated tree, `check --no-pixelorama` gives **61/61**: the same set minus the 2 Pixelorama gates.

## Measurements: v13 vs v14 on identical real backgrounds

Each cell is mean |ΔL| / share of texels with |ΔL| < 20, outline excluded; for the share, lower is better. Both sprites are composited over the same v14 run's no-sprite frame; this is valid because both have the same pin and 0 companion overlap.

| floor | region | v13 | v14 |
|---|---|---|---|
| archive (bright) | lower body 38–67 | 40.4 / 19.7% | 37.1 / **28.9% (worse)** |
| | coat skirt + legs 40–56 | 36.3 / 29.5% | 36.1 / 30.2% |
| | boots on paving | 53.3 / 0.0% | 48.9 / 14.0% (worse) |
| | boots in shadow | 33.6 / 5.5% | 22.2 / **37.5% (worse)** |
| outskirts (dark) | lower body 38–67 | 31.1 / 31.3% | 28.3 / **34.0% (worse)** |
| | coat skirt + legs 40–56 | 25.4 / 39.9% | 26.0 / 36.9% (better) |
| | boots on paving | 25.4 / 39.8% | 25.2 / 33.7% (better) |
| | boots in shadow | 53.4 / 1.4% | 33.4 / **37.5% (worse)** |
| head-geometric | lower body 38–67 | 28.0 / 51.4% | 26.6 / 48.1% (better) |
| | boots | 22.1 / 72.6% | 16.5 / 71.3% |

Head and torso are within ±2 points everywhere.

A bounded variant with a 1-row lit welt (the first build, superseded and deleted) was worse on the dark floor: boots 48% and lower body 38% under 20. I adopted the 2-row base after comparing both at 1×.

## Visible review at 1× (actual captures) and candid trade-offs

The main review images are the six 640×360 captures at 1×. Compare them with the v13 probe captures `0cc9f010` (archive), `66527b60` (outskirts) and `3129b639` (head-geometric), which use the same draw order and shadow.

What reads better:
- At game size the legs read as legs: a forward knee, a shin dropping back, a far leg braced behind with a gap between them.
- The boots read as boots (dark leather, lit toe cap, thin lit base) instead of v13's large light-brown blocks.
- The coat tail is full again and reads as cloth with a fold, not as a black bundle and not as v13's short stub.
- The brow change makes the face read a little older at 1×. It is a 3-texel change, so the effect is subtle.

What is worse or still open:
- **The dark-floor lower-body merge is not solved by the numbers.**
  - Slimmer, dark-based boots trade v13's large lit foot band for a smaller lit base. Boot texels inside the contact shadow merge more on both floors (5% / 1% → 37.5%), and the lower-body share under 20 rises on both floors.
  - On the dark floor the coat skirt and legs improve slightly (39.9% → 36.9%), but the mid-slate tail is still close to the outskirts wall and paving (L ≈ 80–88).
  - This is the direct price of "thin boots, no pasted glow". Visually, the foot still reads through the lit base, toe cap and outline.
- **The back is calmer at the contour, but not simple.** The roll, pack, canister and drape tip are four small accents in a 13×18 area.
  - At 1× the canister reads as a pale grey mark at the back edge of the pack, not clearly as a bottle.
  - The pack face's dark marks only drop 20 → 18. The visible pack is smaller (111 → 93) because the canister and drape cover part of it.
- **She is slightly lighter in mass** (1621 → 1590 texels; boots 35 → 29 wide). The coat is fuller, but slimmer boots make the lower body narrower. I did not widen her or enlarge the head to match the unapproved companions.
- **HEAD's geometric backdrop is still poor for the boots:** the shafts stand on the dark purple wall (about 72% under 20, as in v13). That backdrop is a placeholder, not a reviewed floor.
- The warm `u` planes are deliberately faint (10 texels). They help the near shin's front edge on the dark floor; they do not change the overall read.

## Not done

- No animation.
- No runtime swap.
- No `battle_arena.gd` edit.
- No Game Bible, ledger or progress edit.
- No commit or push.
- No new creator decision is required to evaluate this frame. It keeps the approved v8 slate coat and the 0.65 proportion.
