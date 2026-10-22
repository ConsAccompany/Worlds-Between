# Jiang Lan exploration source - independent validator

- Status: **fail**
- Root: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync`
- Source manifest: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\jexplore39\rpg-2-star-ocean-the-second_jiang-lan_explore-source-manifest_unapproved-jexplore39-v01_20261022-154032-8984b31f.json`
- Main report: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\jexplore39\root\deepseek-actual\rpg-2-star-ocean-the-second_jiang-lan_independent-explore-source-check_v01_20261022-154032-5bca7193-720539f5.json`
- Checker selftest: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync\outputs\jexplore39\root\deepseek-actual\rpg-2-star-ocean-the-second_jiang-lan_independent-explore-source-check_selftest_v01_20261022-154032-5bca7193-720539f5.json` (pass)
- Checks: 126/135 passed

## Failed checks

- `source.south.stop_endpoints`: [(0, 'start', {'ref': 'walk', 'index': 0}), (0, 'end', {'ref': 'idle', 'index': 0}), (1, 'start', {'ref': 'walk', 'index': 1}), (1, 'end', {'ref': 'idle', 'index': 0})]
- `source.west.stop_endpoints`: [(0, 'start', {'ref': 'walk', 'index': 0}), (0, 'end', {'ref': 'idle', 'index': 0}), (1, 'start', {'ref': 'walk', 'index': 1}), (1, 'end', {'ref': 'idle', 'index': 0})]
- `source.north.stop_endpoints`: [(0, 'start', {'ref': 'walk', 'index': 0}), (0, 'end', {'ref': 'idle', 'index': 0}), (1, 'start', {'ref': 'walk', 'index': 1}), (1, 'end', {'ref': 'idle', 'index': 0})]
- `source.east.stop_endpoints`: [(0, 'start', {'ref': 'walk', 'index': 0}), (0, 'end', {'ref': 'idle', 'index': 0}), (1, 'start', {'ref': 'walk', 'index': 1}), (1, 'end', {'ref': 'idle', 'index': 0})]
- `pxo.south.nine_role_layers_plus_hidden_guides`: {'layers': ['far-limbs', 'boots', 'trousers', 'shirt', 'vest', 'arms', 'devices', 'face', 'hair', 'goggles', 'guides'], 'size': [80, 112]}
- `pxo.west.nine_role_layers_plus_hidden_guides`: {'layers': ['far-limbs', 'boots', 'trousers', 'shirt', 'vest', 'arms', 'devices', 'face', 'hair', 'goggles', 'guides'], 'size': [80, 112]}
- `pxo.north.nine_role_layers_plus_hidden_guides`: {'layers': ['far-limbs', 'boots', 'trousers', 'shirt', 'vest', 'arms', 'devices', 'face', 'hair', 'goggles', 'guides'], 'size': [80, 112]}
- `pxo.east.nine_role_layers_plus_hidden_guides`: {'layers': ['far-limbs', 'boots', 'trousers', 'shirt', 'vest', 'arms', 'devices', 'face', 'hair', 'goggles', 'guides'], 'size': [80, 112]}
- `runtime.stop_bridges`: [('south', 0, 1, 'k'), ('south', 0, 2, 'k'), ('south', 1, 1, 'k'), ('south', 1, 2, 'k'), ('south', 2, 1, 'k'), ('south', 2, 2, 'k'), ('south', 3, 1, 'k'), ('south', 3, 2, 'k')]


## Contact / slip disclosure

- south: {"direction": "south", "status": "not_verified", "reason": "TypeError", "pivot": [40, 104], "pivot_is_not_footlock": true}
- west: {"direction": "west", "status": "not_verified", "reason": "TypeError", "pivot": [40, 104], "pivot_is_not_footlock": true}
- north: {"direction": "north", "status": "not_verified", "reason": "TypeError", "pivot": [40, 104], "pivot_is_not_footlock": true}
- east: {"direction": "east", "status": "not_verified", "reason": "TypeError", "pivot": [40, 104], "pivot_is_not_footlock": true}

## Limitations

- Technical source contract only; no art/motion/creator approval.
- Pixel-derived foot landmarks can be `not_verified`; fixed pivots are never treated as footlock.
