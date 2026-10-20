"""Reuse the bounded normal-input recorder with separate first-stop/bridge/idle captures. No model changes."""
from pathlib import Path
import importlib.util
C=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',C/'tools/rpg-2-star-ocean-the-second_heroine-sea_distance-gameplay_root-runner-v01_20261020-215100-a108f5ec.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
runner.HARNESS=C/'tools/rpg-2-star-ocean-the-second_heroine-sea_stop-handoff-normal-input_root-check-v01_20261020-221738-bc114d39.gd'
if __name__=='__main__': runner.main()
