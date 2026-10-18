# Yonkers room 1 v04: Godot test-only runtime capture/check and two closeouts (UNAPPROVED)

Date: 2026-10-18. Tag `20261018-053200-7c41e9d2`. Status: **v04 UNAPPROVED, nonruntime, off by default**. Codex viewed the v04 native PNG and judged the contact depth modest and the scene still schematic; **no art acceptance**. No art was changed in this task.

## Engine actually used

- Official Godot **4.7.2.stable.official.ed1daf0bf** (the project-approved version). One temporary download of `Godot_v4.7.2-stable_linux.x86_64.zip` from the godotengine GitHub release went to the session scratchpad; it is not committed.
- Run windowed under Xvfb with the `opengl3` renderer (GL Compatibility), after `--headless --import`. The only engine errors were ALSA audio (no sound device), which fell back to the dummy audio driver.
- The import's generated untracked `.import` and `.uid` files were deleted after the run. No tracked file changed.

## Harness

`tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v04-texture-override-capture-and-check_test-only-v04_20261018-053200-7c41e9d2.gd` is the committed v03 harness with one addition.

- **Override:** before the real `res://scenes/survey_annex.tscn` loads, the five v03 room-1 texture paths are taken over **in memory** (`ImageTexture.take_over_path`) by the v04 nonruntime exports. The harness refuses to run if the v03 plate is already cached.
- **v04 in use:** after the room opens, it checks that the scene's preloaded plate, foreground and three antennas are those v04 textures, and that the plate is pixel-equal to the export (`YK1_V04_TEXTURES_IN_USE`).
- **v03 checks, all unchanged:** structure, door and spawn points, HUD clearance, captions and markers, all six clues by real `interact` at the existing coordinates (163/320/477), collision 14 cases with slide, lane walk, escape, y-sort depth, reachability, and three transitions.
- **Captures:** 30 actual Godot 640×360 frames, zh and en, in `outputs/yonkers-room1-v04_523bba3b/godot-test-only/…_v04-material-depth-test-only-godot-{zh,en}-…_20261018-053200-7c41e9d2.png`.

These are real frames of the real scene drawn with the v04 textures through a test-only override. They are not production runtime: no project script loads v04.

## Results

| Check | Result |
|---|---|
| v04 harness | exit 0, `YK1_V04_ALL_OK`, 0 `YK1_V04_FAIL`, 0 SCRIPT ERROR. Log: `outputs/yonkers-room1-v04_523bba3b/…_godot-v04-test-only-check-log_20261018-053200-7c41e9d2.txt` |
| v03 off-default | The committed v03 harness, with no override, was re-run in the same session (captures in scratch only, not committed). `YK1_V03_PLATE` resolves to the v03 plate; `YK1_V03_ALL_OK`. |
| Behaviour parity | Clue, depth, reachability, HUD and transition lines are identical between the v03 and v04 runs. Collision stop points differ by at most 0.007 px (frame timing), inside the v03 checker's 0.05 px tolerance. |
| Capture pixels | `tools/…_godot-v04-capture-pixel-check_test-only-v04_20261018-053200-7c41e9d2.py` → **PASS**. Of the 15,261 plate pixels v04 changed that no antenna or foreground texel covers, the zh entry shows 14,239 and the en entry 13,969 exactly as v04, and 0 as v03. The rest are under UI or the heroine. 30 captures, all 640×360. |
| Source check (v04) | Re-run: GATES 7/7 PASS (report unchanged). |
| Pixelorama editor or CLI round trip | **NOT RUN**: no Pixelorama binary; still pending locally. |

`survey_annex.gd`, the v03 PNGs, the accepted rooms and every production script are unchanged.

## Closeouts (zero change)

- `closeout-20261018-053308-8d9e0df4`: Game Bible current-candidates-first review queue (418044a).
- `closeout-20261018-053308-d5810a29`: Yonkers v04 SOURCE pass plus the test-only Godot check; Pixelorama pending.

Both are 40.8% → 40.8%. The meter check reads: core 5/5, M2 10/12, science content 3/4, sprites 0/52, scenes 3/12, plays 0/2.

## Local re-run commands (from the repo root)

```
godot --headless --path game --import
godot --path game -s res://../tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v04-texture-override-capture-and-check_test-only-v04_20261018-053200-7c41e9d2.gd -- "$PWD/outputs/yonkers-room1-v04_523bba3b/godot-test-only" 20261018-053200-7c41e9d2 "$PWD/outputs/yonkers-room1-v04_523bba3b/nonruntime-exports"
python -I tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v04-capture-pixel-check_test-only-v04_20261018-053200-7c41e9d2.py
python -I tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py --pixelorama <Pixelorama 1.2.3 exe>
```
