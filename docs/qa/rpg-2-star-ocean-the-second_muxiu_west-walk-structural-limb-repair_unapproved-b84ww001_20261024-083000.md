# Muxiu west walk — batch84 structural far-limb repair (b84ww001), UNAPPROVED

Task: `content.char.muxiu.walk-west`, second serial batch84 job. One bounded structural fix of the coordinator-observed
defect: the far leg/boot rendered as a thin dark detached string/sliver with no continuous clothed leg. **Verdict:
source candidate produced and independently checked; canonical task remains TODO/UNAPPROVED.** No score, approval,
default-adoption, commit, push, ledger/Bible/registry or Git-index write was made. Producer does not approve art.

## 1. Root cause (confirmed by reading the preserved baseline)

The preserved `...b78ww001-v01r1...py` adapter split ONE neutral boot/wrap/trouser set by forward-coordinate masks.
Its far-boot mask `(f>=8) | ((f>=5) & y<=96)` retained only the front 2-5 texels of the single neutral boot
(`th` sole `(31,32)`), while its far wrap/trouser masks retained the *back* fragments. The resulting PXO
`far-limbs` cel was 29 texels (2-5 wide, y86-103), a detached boot sliver with no trouser/wrap above it. That is a
real structural limb defect, not micro-polish.

## 2. Change of method (one pass)

The far limb is now the **complete occluded limb silhouette**: the full near-role `boots + legwraps + below-hip
trousers` composite recoloured through the pinned Muxiu `DARK` far-shading table
(`r1->r2->r3`, `t1->t2->t3->t4`, `w1->w2->w3`, `q1->q2`, cuff `c`/`q` kept in family) and articulated by the
unchanged far `leg_transform`. It is continuous boot→wrap→trouser by construction, with deliberate occlusion under
the cloak and behind the near leg; no arbitrary dark pixels, no off-palette colours, no mirrored art.

Protected properties kept: neutral static and idle f00 byte-exact; 80x112; density 2; pivot 40,104; 48 logical;
screen-left/west; frozen 12x40 ms gait; stop timing; all thresholds. Far transform timing/offset unchanged, so
contacts are invariant.

## 3. Files created (all new; no existing baseline file edited)

- author: `tools/rpg-2-star-ocean-the-second_muxiu_walk-west-source-author_unapproved-b84ww001-v01_20261024-083000.py`
  raw SHA-256 `3566edc827f2f9ee5414393719ecd433312c8a927b62e20d040d679251447dee`
- checker: `tools/rpg-2-star-ocean-the-second_muxiu_walk-west-independent-check_v01_20261024-083000-b84ww001.py`
  raw SHA-256 `04bedd43f8aef7da6c35c3060b32616a2ff19577d40b24f5098cb5d09e878c88`
- output tree `outputs/muxiu-ww84/` (7 top-level build files + evidence/staging/scratch subdirs)
- opt-in package `game/assets/characters/muxiu-native-v01/west-walk-b84/` (44 files)
- this one report.

Preserved byte-for-byte baselines (hashes unchanged from read):
`...b78ww001-v01r1...py` `4a1b36071e79d2becf5bf6bd70ea8b0c56cf536a1063f2416aad39f827bc3142`;
`...b78ww002...py` `94c52e4be5492e911ea6822e35aa5460fe49dff9c62f115fe60f0cc4ae95e0d5`.

Key build hashes (sha256 raw):
- manifest `8f172c7acdab21427f743232fe24fa53702304108bac724a14102167e42cafb6`
- file-list `450ecf5366ed308daf8da36abcb0eb01af23bb645af709ed1b3fa5ca5dfc5df4`
- check-result `f78e18af7291565d246a6e2eb661bbd42dffff8d9f2b922d9e857905751de917`
- PXO `bc3620878ad8bc0e669486bf1606e88be41249e47949096d7dcf5a0658af92bc`
- ORA `c64fbd5c38f22088e95a293cf382d5679e849bb31e98c2195f2e8559cde89f2d`
- runtime sprite set `1d8179c1341f028d49e580b5e4e1b632156516b7e2fea4ebc443271abf1984dc`
- stop supplemental `3396dccc86592200ff1b1e83b764be32ea249b1771dbe07ef12d3d4d7546b9b9`
- package registry `8ea250ef7a941e41ff3872a7f291dfc5d8079a5e0e26a324095e26ef3708f922`
- contact sheet `55c58ad25f50fd02e86d237e591802bcfb59a5e0ca380af6042c9b63d72db174`
- source-bound west GIF `2e9a3bfd488c15fddc1e718165ab8c610982c7b92014d743754374bf065509c0`
- independent result `e74a636425768e46dc12bfd968b5f5e1b11300da3cd15ab69277bd8561211208`

## 4. Commands and actual results

```
export PYTHONDONTWRITEBYTECODE=1 TMPDIR=$PWD/outputs/muxiu-ww84/tmp
V=/home/kel/projects/worlds-between/tooling/venv/bin/python
$V -X utf8 -I tools/<author-b84>.py build
  WROTE 89 files; REBUILD 89/89 DETERMINISTIC True; SOURCE 20/20
  {"walk_max_world_slip_src_at_40ms_boundaries": 0.8, "walk_planted_foot_world_excursion_src_60fps_samples": 10.667,
   "flight_phases": [4,5,10,11], "stop_bridge_grounded_slip_src_max": 0.0}; RESULT PASS
WB_STAGE_REL=outputs/muxiu-ww84/stage-b84 $V -X utf8 -I tools/<author-b84>.py build
  WROTE 89 files under fresh staging; REBUILD 89/89 DETERMINISTIC True; SOURCE 20/20; RESULT PASS
python3 tools/wb_safe_replace.py <stage>/<file> <installed>/<file>   (3 metadata files)
  RC=0 each; receipts in outputs/muxiu-ww84/replacement-receipts.jsonl
$V -X utf8 -I tools/<author-b84>.py check
  REBUILD 89/89 DETERMINISTIC True; SOURCE 20/20; RESULT PASS
PIXELORAMA=.../tooling/bin/pixelorama $V -X utf8 -I tools/<checker-b84>.py --out outputs/muxiu-ww84/independent-r3
  INDEPENDENT PASS 41 / 41; 16/16 negative controls rejected; native 41/41 RGBA-exact
```

Metadata replacement disclosure: after a validator text fix the installed build manifest/file-list/check-result
carried the pre-fix author hash. The final tree was rebuilt deterministically into fresh staging and only those three
metadata files were installed with the authorized backup-before-replace helper (verified backups under
`outputs/development-backups/<uuid>/original`; three receipts). Frame PNG, PXO, ORA and package bytes were byte-equal
before/after and were not replaced.

## 5. Independent check result and preserved numbers

- 41/41 checks PASS; 16/16 negative controls REJECTED, including **"ORIGINAL fragmented far-limb geometry (2-5 texel
  front-boot split) -> rejected by b84 continuity"** and "far limb severed above the boot -> rejected".
- New checks: every walk/stop `far-limbs` cel is ONE 8-connected clothed mass (span>=18, no 1-texel row, trouser +
  legwrap/cuff + boot roles); in all 36 walk/stop composed frames the far leg remains visibly exposed (min 92 visible
  texels, vertical span>=6).
- Rebuild 89/89; source 20/20 (was 19/19; one added structural check); independent 41/41 (was 39/39; two added).
- Contacts unchanged exactly: 40 ms boundary `0.8` source px; 60 fps held-frame excursion `10.667` source px
  (`5.333` logical); flight `[4,5,10,11]`; each foot grounded 4/12; stop-bridge grounded slip `0` across all 12
  phases; all 12 endpoints exact neutral feet + neutral PNG; timing 39→p0 / 40→p1 / 479→p11 / 480→p0.
- Native Pixelorama: exit 0, no timeout, 41/41 frames RGBA-exact, source unchanged. Application clean: **false**,
  with the same **four** `ERROR: Condition "!actions.custom_samplers.has(function->arguments[ j ].tex_builtin)"...`
  shader diagnostics retained (not an export-equality gate; GUI SaveAs/reopen not verified).
- Palette/border/alpha/identity/bracelet/mirror/anchor checks all PASS; neutral static + idle f00 byte-exact.

Visual candidate: `outputs/muxiu-ww84/independent-r3/...contact-sheet...png` (walk + s1 + s2) and
`...normal-speed-preview-source-bound...gif` (horizontal west, 40 ms, 11.2 src px/40 ms, zero vertical displacement).
Both are source-bound PIL composites, **not** a Godot capture.

## 6. Genuine limits / preserved failures

- No footlock/fluidity claim: `0.8` boundary residual and `10.667` held-frame excursion remain; not slip-free.
- Four native shader diagnostics remain; `application_clean=false`.
- No normal-host / Godot runtime / GUI save-reopen evidence was obtained with the existing parameterized tools in this
  timebox; runtime behavior is **unverified**, not claimed.
- Only the source contact sheet/GIF were judged; no human art or motion acceptance. Producer cannot approve.
- Historical r1 `stop-bridge slip 4` / `SOURCE 18/19` failures remain in their own reports; b84's own checks report 0.
- Legs remain sheared static texels (no foreshortening repaint); the far limb is deliberately darker/occluded.

## 7. Runtime non-adoption and scope

The package is opt-in at `game/assets/characters/muxiu-native-v01/west-walk-b84/` only; no loader, default selector,
registry, scene, test default, ledger, Bible or Git index was changed. Scratch retained (not deleted):
`outputs/muxiu-ww84/{proto,tmp,stage-b84,independent,independent-r2}`; `independent/` and `independent-r2/` are
aborted-run directories from checker argument/shadowing failures (no evidence). No symlink/hardlink staging.

## 8. Next step

Coordinator should independently rerun the b84 checker (with its own Pixelorama path/output dir), visually review the
contact sheet/GIF at normal speed, then present the candidate for creator art decision. If accepted later, integration
must remain a separate coordinator action with the same frozen thresholds.
