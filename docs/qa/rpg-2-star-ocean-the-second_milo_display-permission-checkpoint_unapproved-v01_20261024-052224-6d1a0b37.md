# Milo display: blocked on interpreter execution permission (UNAPPROVED, NOT DONE)

Task: content.char.milo.display (creator batch54; producer Claude). Base revision 6c86613caf02bddfcafb80d8f39112e654d1c95e. Recorded 2026-10-24T05:22:24Z. Hashes are SHA-256 of raw bytes, no normalization.

## Verdict

BLOCKED before any build. No crop, manifest, scene, script, probe, capture or existing game file was created or changed. Meters unchanged (production61.6%, inspection21.6%, approval7.8%); no completion claim.

## Exact denied commands (genuine tool permission gate, not overwrite consent)

Each returned "This command requires approval" and did not run:

    ../tooling/venv/bin/python -I outputs/mdisplay01/scratch/rpg-2-star-ocean-the-second_milo_display-source-measure_v01_20261024-052100-6d1a0b37.py outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png
    ../tooling/venv/bin/python --version

An earlier inline `../tooling/venv/bin/python -I -c "...PIL size probe..."` was refused in the same way. Project-local .claude/settings.local.json (9a15beb4a0436a3fc5ea56932ac645c3cf1d64370166076d84be77728913a75d, unchanged) allows only `Bash(python3 tools/wb_safe_replace.py *)`. Every required step (Pillow crop build, contract/malformed checks, and the checked Godot runner, itself a Python script) needs the venv interpreter. No system-Python substitute, wrapper, settings edit or bypass was tried.

## Verified read-only facts

- Source sheet outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png exists, 2080892 bytes, SHA-256 79a02c532681042ec389cfb6eae0577e3f967652641be7b853461e6adc4c244f, tracked since 51a82d36. Its pixel dimensions and front-figure bounds have NOT been measured, so no crop rectangle is chosen.
- South static (8fb2c8e4) PNG 3822b31805729f3091a61b3e073ade723f613049db4622364dc162a5101fa473 matches its manifest rawsha256. It is 80x112, pivot 40,104, scale 0.5, and it sits under game/assets/characters/milo-native-v01/.gdignore. The display scene would therefore need the existing raw `Image.load_from_file` path from the Lin Que `_load_texture`, not an imported resource. Exported builds would not include it.
- Bible character-04: 米洛 / Milo, 31, 医疗工作者; 白灰短医袍、方形药箱、鲜绿色腕带.

## Planned implementation once the interpreter is permitted

Adapt the four lin-que_display tools and the ldisplay64 scene/script into mdisplay01-only files. Measure the sheet, then pin an exact front-figure rectangle (no back view) at the 0.72 box aspect. The scene uses the south static only, labeled "Static source (south)" / "静态来源（南向）": no direction or walk controls, no west, no pilot registry. It shows the portrait, EN/ZH identity, Art pending / 美术待定, and a localized non-crashing missing-portrait fallback, plus a missing-static fallback. Then the checked runner import, the Xvfb EN/ZH probes with captures, crop equality, and the malformed cases.

Retained file: outputs/mdisplay01/scratch/rpg-2-star-ocean-the-second_milo_display-source-measure_v01_20261024-052100-6d1a0b37.py (9e932e50f348073dc686e1e47b957a53861c3e5ad1b96f834a61ed83473f4277), read-only measurement helper, never executed.

## Next action

The creator or coordinator grants the project-local venv interpreter for this task's scoped scripts (e.g. `Bash(../tooling/venv/bin/python -I tools/rpg-2-star-ocean-the-second_milo_display-*)`, `Bash(../tooling/venv/bin/python -I outputs/mdisplay01/*)`, and the checked-runner invocation under `xvfb-run -a`), or runs the steps directly. Then resume this task from the measurement step.
