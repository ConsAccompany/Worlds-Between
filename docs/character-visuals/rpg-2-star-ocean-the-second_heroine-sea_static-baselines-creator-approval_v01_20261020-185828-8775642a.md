# Heroine Sea of Stars-direction static appearance approval

Recorded at 2026-10-20T18:58:28.265961Z; recording time, not an exact user-message timestamp.

Creator response: **approved**. This followed the two inspected gameplay stills presented together. Both heroine static appearance baselines are approved.

## Exact approved assets

### Right-facing combat static appearance

- Native asset: `outputs/hero-sea-v01/rpg-2-star-ocean-the-second_heroine-battle_still-native136_sea-unapproved-v01_20261020-181955-1294c865.png`
- Native SHA256: `4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6`
- Presented gameplay capture: `outputs/hero-sea-v01/root-20261020-182710-dd45d8bd/rpg-2-star-ocean-the-second_heroine-battle-sea-v01-ci1280-outskirts-en-injected_test-only_20261020-182710-dd45d8bd.png`
- Capture SHA256: `9cb3874350792c3d04114b40453d72ac54d5d8661aaa2ae4740698ec7f83f1fe`
- Artifact commit: `d5cfb11e9c7f576ad39c39c238f3f94a4408879d`

### South-facing exploration static appearance at 48 logical pixels

- Native asset: `outputs/hero-sea-exp-v01/rpg-2-star-ocean-the-second_heroine-sea_exploration-native80x112_unapproved-v01_20261020-181941-4449ed55.png`
- Native SHA256: `6bf1d688487bd3fcc71eeb2e7c9b7c74f1fe6b6cd6362860b7fa0d42e009e429`
- Presented gameplay capture: `outputs/hero-sea-exp-v01/capture-20261020-182023-3f2b9c9b/rpg-2-star-ocean-the-second_heroine-sea_exploration-city-bright-en-sea1280_test-only-v01_20261020-142025-f86a9397.png`
- Capture SHA256: `7fed9db978070c4d547c26d1af083b6f185b66ef1fbceda390c6815f26929c9b`
- Artifact commit: `d5cfb11e9c7f576ad39c39c238f3f94a4408879d`

## Scope and next action

Approval covers these two still appearances. Motion, other directions, other characters, environments, portrait, display packages and complete runtime sprites remain unapproved. Existing scales, test-only capture status and runtime defaults are unchanged. Historical filenames and frozen manifests retain their original creation status; this decision records the subsequent scoped approval.

Use these designs for heroine motion next. Paint occluded anatomy and coherent poses; flat mask slices alone are insufficient moving anatomy. Inspect normal-speed movement and combat anticipation/contact/recovery in actual gameplay.

Native pixel export equality remains verified, but Pixelorama shader diagnostics/crash and GUI Save As/reopen reliability remain unresolved. Artistic approval does not close those technical gates.

## Progress accounting

Production stays 53.2%. South static approval was already complete for the earlier baseline: replace its current evidence without new points. Combat static has no separate creator task; do not mark full combat-set acceptance. Complete runtime sprites 0/52; accepted science environments 3/12; human post-art playtests 0/2.
