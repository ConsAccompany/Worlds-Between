# Common combat VFX: produced and wired, artistic acceptance separate

Task `content.vfx.common`, accountable producer DeepSeek; Codex independently checked and integrated. Base main `54794b55d90082f5f67bd8c50882fa716884d16f`. Five64×64 native effect sets: attack(.22s), dodge(.27s), guard(.30s), hit(.20s), heal(.55s); eight RGBA cels each, three editable roles, pivot32,32. Five genuine PXO timelines and five ORA middle-frame snapshots. ORA is explicitly one representative cel, not an eight-frame animation format.

## Independent evidence

- Root native checker:245/245, reconstructs all40PXO cels and five ORA composites, checks alpha≤166, dimensions, native timing, raw source/helper/artifact hashes, then rebuilds all51package files byte-for-byte. `tools/rpg-2-star-ocean-the-second_common-vfx_root-native-check_v01_20261019-164412-1f3bff80.py`.
- Root actual bilingual gameplay hooks:1312/1312, all five kinds loaded eight native frames; real attack/dodge/guard/hit and presentation-only heal emit correctly. Pause/expiry/finite-input/queue bounds pass. Baseline, candidate-off and candidate-on600-step combat histories match; default screen is pixel-identical. Separate actual EN/ZH captures in `outputs/common-vfx-v01/hooks/`.
- Unchanged existing battle VFX regression:33/33, including rejected actions, guard energy, evasion, pause, three600-step combat/save parity pairs. Its standalone unit helper remains the original procedural class; the arena hooks exercise the integrated native class.
- Root loader boundary checker:122/122, missing/invalid JSON, wrong numeric field types/fractions, invalid pivot/cell/event table, partial frame lists, invalid frame type/path, missing PNG, wrong image dimensions and bad duration metadata all safely fall back by whole kind. Does not claim recovery from arbitrary corrupt PNG decoder errors.

## Defect found and fixed

Original producer loader cast malformed `fps` and `frameCount` fields with `int`. A dictionary produced a real SCRIPT ERROR, although its inner report printed eight passes and process exit0. The checked runner correctly rejected that run. Original loader and failed diagnostic log are retained. Codex's separately named root-v02 adds strict finite numeric equality before these fields are used;122boundary checks then pass without diagnostics. Thresholds were not weakened.

## Integration and limits

`battle_arena.gd` changes only the opt-in common helper class, asset directory and constructor. Existing `--battle-vfx-pilot`/override gates remain off by default. No HP, energy, AI, save, reward, action-range or RNG logic changed. Heal remains an existing presentation API; no new healing mechanic is invented.

Root viewed actual gameplay guard, hit and dodge captures: small local contact/foot accents remain within the actor region and do not cover interface text; this is a technical and composition inspection, not creator artistic approval. Full sprites0/52, accepted environments3/12 and human playtests0/2 remain unchanged.

Pixelorama application export/clean application run and GUI Save As/reopen were not verified in this package. Native format reconstruction and deterministic export equality are documented separately from those limitations. No full motion or artistic acceptance is claimed.

Producer encountered Windows sandbox ACL failures while trying optional temporary-directory verification and began an unnecessary ACL troubleshooting path. Codex stopped that worker after the useful package existed, reran the independent native rebuild and actual Godot checks outside that sandbox, and retained the account-local dispatch trace. This was a coordinator stop, not quota or insufficient credit. No permissions were widened and no credit was purchased.
