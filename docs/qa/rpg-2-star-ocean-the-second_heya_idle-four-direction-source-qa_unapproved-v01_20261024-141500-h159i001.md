# Heya four-direction idle source bank — independent QA (UNAPPROVED, batch159)

Task: `content.char.heya.idle-anim`. Producer: DeepSeek via the authorized adapter. Coordinator: Hermes.
Status: technical source bank built and independently checked; **not** default-integrated, **not** committed by
this producer, **not** art/motion approved, **not** human-reviewed. Coordinator audit and commit remain pending.

## Tested boundary

All four existing Heya static packages are the exact neutral inputs. The source bank adds only a four-frame idle
loop per direction (south/west/north/east); no walk, stop, combat or new character was authored. Canvas 80x112,
pivot (40,104), body rows 8..103, display scale 0.5 = 48 logical px, binary alpha, existing 36-colour palette.
Frame model is the established jexplore39 idle settle applied to Heya role layers:

| frame | torso | head | arms | duration |
|---|---|---|---|---|
| f00 | 0 | 0 | 0 | 700 ms |
| f01 | +1 | +1 | 0 | 200 ms |
| f02 | +1 | +1 | +1 | 400 ms |
| f03 | 0 | +1 | +1 | 200 ms |

Offsets are source texels (0.5 logical px), downward settle only. `head = face,hair,braid,scarf`;
`torso = dress,coat,apron,belt,strap,bag,herb`; `arms = arms`; `boots` and composite sole rows 90..103 are frozen
in every frame. f00 is byte-exact the existing static PNG. Cycle 1500 ms, loop target f00. No global sprite bob.

Installed package: `game/assets/characters/heya-native-v01/idle/` (4 directions, each 4 PNG frames, animated PXO,
static-layer ORA, palette copy, manifest; plus runtime sprite-set JSON). Staging: `outputs/heya-i159/staging/idle/`.

## Executed checks (actual commands and results)

1. Author build/check — `python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i159-v01_20261024-140235-a159i001.py check`
   - deterministic rebuild of 34 generated files; source pins exact before/after; 39/39 internal checks; 33/33 installed files byte-equal.
   - checks include f00==static bytes, 1500 ms timing, PXO metadata/tags, binary alpha + palette + transparent
     border, frozen sole rows, non-zero subtle motion/loop closure, exact group offsets/no horizontal shift, no walk/stop frames.
2. Independent checker — `python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-independent-check_v01_20261024-140235-a159i001.py`
   - PASS, 4/4 directions, 5/5 real negative controls rejected (PNG pixel flip, PXO duration, ORA static pixel,
     manifest duration, palette colour). Report hash is listed in the provider receipt.
3. Native Pixelorama animated export — `python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-native-pixelorama-check_v01_20261024-140235-a159i001.py`
   - PASS 40/40 export gates across 4 directions: 224 per-frame/per-layer cells exact, 16 split-merged frames
     exact, 16 flat frames exact, no hidden guides exported, PXO inputs unchanged.
   - Application diagnostics are **not clean**: 8 `custom_samplers` shader-compiler error lines per direction
     (plus their `at:` lines) retained verbatim in the report/logs. Equality is claimed; diagnostic cleanliness is not.
   - GUI SaveAs/reopen of the animated PXO was not tested.
4. Godot normal-speed source-fit — `python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit_v01_20261024-140235-a159i001.py`
   - PASS through the checked runner, finite 75 s deadline, Xvfb `640x360x24`, OpenGL3, **Dummy audio**.
   - 12 fresh 640x360 captures: city/ruins x EN/ZH x three phases. All four directions play simultaneously at the
     explicit 1.5 s loop; recorded frame indices are f00 at ~0.10 s, f02 at ~1.00 s, f03 at ~1.35 s for every
     direction and language. Runtime manifest and scripts unchanged. Test-only overlay: not ordinary actor
     integration, not a default change, not human motion review.
   - Visual inspection: four sprites readable in a test-only panel; all four directions present; EN and ZH labels
     render. Small face/braid detail remains ambiguous at 48 logical px, as in the static sources.

## Preserved failures and limits

- First built PXO bank had `guides` as the first native cell because the frame layer list was not ordered to
  `ROLES+guides`; the independent checker caught it (`PXO cells are not exact model shifts`, 4/4 directions).
  The staging bank was backed up under `outputs/heya-i159/backups/staging-draft2-*`, the tool was corrected,
  rebuilt and reinstalled; the failed independent reports `...T140508/140527/140542.json` are retained.
- Earlier checker implementation details (transparent-RGB zero-shift comparison) also failed and were retained;
  correcting the checker did not change source bytes.
- A first Godot fit attempt used `AnimatedSprite2D` and failed parse/type inference under the project's
  warnings-as-errors setting; the failed log/capture is retained under `outputs/heya-i159/fit/failed-parse-r1`.
  A second playback approach produced wrong frame indices and is retained under `.../failed-anim-r2`; the final
  wall-clock `Sprite2D` playback passes with explicit frame indices.
- Pixelorama headless application diagnostics fail (known `custom_samplers` errors); GUI animated SaveAs/reopen,
  ordinary actor integration, interaction, performance, save/reload, combat and human playtests were **not** run.
- No default, registry, ledger, Bible, Git index, commit, provider/account setting or protected vault/history file
  was changed by this task. The pre-existing dirty registry/ledger/Bible modifications were preserved untouched.
- No art, motion, style or gameplay acceptance follows from these metrics. Source production is not approval.

## Coordinator rerun (minimal)

```bash
cd /home/kel/projects/worlds-between/repo
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i159-v01_20261024-140235-a159i001.py check
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-independent-check_v01_20261024-140235-a159i001.py
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-native-pixelorama-check_v01_20261024-140235-a159i001.py
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit_v01_20261024-140235-a159i001.py
```

Expected: author `RESULT PASS`; independent `"passed": true` with 5/5 controls rejected; native
`"equality_passed": true` 40/40 with `diagnostic_clean:false`; fit `HEYA_I159_IDLE_NORMAL_SPEED_FIT PASS`.
