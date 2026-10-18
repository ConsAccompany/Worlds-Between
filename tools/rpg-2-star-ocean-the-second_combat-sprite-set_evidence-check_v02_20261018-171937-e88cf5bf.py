"""Verify final combat sprite capability evidence. No model calls, art approval or game mutation."""
from pathlib import Path
import hashlib, json, re, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "outputs/csp-typed-v02_20261018-171817-b62803cf/rpg-2-star-ocean-the-second_combat-set-pilot_capture-manifest_20261018-171908-a4e51160.json"
BASE = "outputs/combat-set-pilot-v01_21e56480/rpg-2-star-ocean-the-second_combat-set-pilot_base-commit-report_20261018-155051-165ae4a6.json"
SOURCES = {
    "battleScriptSha256": "game/scripts/battle_arena.gd",
    "helperSha256": "game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd",
    "checkScriptSha256": "game/tests/rpg-2-star-ocean-the-second_combat-sprite-set_pilot-check-capture_v01_20261018-153656-9efd4413.gd",
}
def sha(path, text=False):
    data=path.read_bytes()
    return hashlib.sha256(data.replace(b"\r\n", b"\n") if text else data).hexdigest()
def main():
    manifest_path=ROOT / MANIFEST
    manifest=json.loads(manifest_path.read_text())
    assert manifest["sourceHashAlgorithm"] == "sha256-text-lf-v1"
    for field, path in SOURCES.items():
        assert manifest[field] == sha(ROOT / path, True), ("source mismatch", path)
    assert len(manifest["captures"]) == 12
    for capture in manifest["captures"]:
        assert sha(manifest_path.parent / capture["file"]) == capture["sha256"], capture["file"]
    assert {c["language"] for c in manifest["captures"]} == {"en", "zh"}
    assert sum(c["case"] == "female-action-mix" for c in manifest["captures"]) == 2
    baseline=json.loads((ROOT / BASE).read_text())
    base_bytes=subprocess.check_output(["git", "show", "3e040a9ae3bd410d8fab4b0921bcb63e8bb3c9b7:game/scripts/battle_arena.gd"], cwd=ROOT)
    assert hashlib.sha256(base_bytes).hexdigest() == baseline["battleScriptSha256"]
    for value in baseline["renders"].values():
        assert sha((ROOT / BASE).parent / value["file"]) == value["sha256"]
    for value in manifest["report"]["simulationParity"].values():
        assert value["steps"] == 600 and value["firstDifferentStep"] == -1 and value["saveSnapshotEqual"]
        assert value["traceSha256"] == value["baseCommitTraceSha256"]
    assert len(manifest["report"]["fallbacks"]) >= 100
    assert manifest["report"]["flagOffRenders"]["pilotOnMissingIndexEqualsOff"]
    for log in ["rpg-2-star-ocean-the-second_combat-set-pilot_windowed-check-log_v02_20261018-171908-4a5e627d.txt", "rpg-2-star-ocean-the-second_combat-set-pilot_headless-check-log_v02_20261018-171817-1f97cab4.txt"]:
        text=(manifest_path.parent / log).read_text(encoding="utf-8-sig")
        assert not re.search(r"(?m)^(?:SCRIPT ERROR|ERROR|FAIL|WARNING:.*leaked)", text), log
        assert "COMBAT_SET_PILOT PASS checks=" in text, log
    fixture=json.loads((ROOT / manifest["fixtureIndex"].replace("res://", "game/")).read_text())
    assert len(fixture["sets"]) == 5 and {"hero:male", "hero:female"} <= fixture["sets"].keys()
    for key,path in fixture["sets"].items():
        path=ROOT / path.replace("res://", "game/")
        data=json.loads(path.read_text())
        assert not data["art_approved"] and data["display_proportion"] == "0.65"
        assert sha(path.parent / data["sheet"]) == data["sheet_sha256"]
    print("COMBAT EVIDENCE PASS: source hashes, 12 bilingual captures, saved base blob, 3x600-step traces, malformed fallback, 5 synthetic sets and clean success logs")
if __name__ == "__main__":
    main()
