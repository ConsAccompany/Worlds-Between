# Source-reconciled combined run after the locale-only runtime fix.
import importlib.util
from pathlib import Path
base=Path(__file__).resolve().parent
root=base.parent.parent
spec=importlib.util.spec_from_file_location("checked_battle_wiring",base/'rpg-2-star-ocean-the-second_battle-arena-wiring_root-runner-correction_test-only-v04r2_20261020-191700-5431a8e2.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.WORKTREE=root.parent/"dual05/cx-combined"
m.GAME=m.WORKTREE/"game"
m.CHECKED_RUNNER=m.WORKTREE/"tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
m.OUTPUTS=base
m.FIXTURE=base/'rpg-2-star-ocean-the-second_battle-arena-wiring_combined-locale-check_test-only-v05_20261020-192227-34314296.gd'
m.BASE_COMMIT='39f252e57c6e67f40e35757aaa5471448ef46522'
m.EXPECTED_RAW["res://scripts/battle_arena.gd"]='41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197'
m.EXPECTED_LF["res://scripts/battle_arena.gd"]='41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197'
m.main()
