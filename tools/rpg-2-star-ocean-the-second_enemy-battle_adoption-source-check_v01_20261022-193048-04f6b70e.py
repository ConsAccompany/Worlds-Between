"""Only two authorized default constants may change; full-line comments may be updated."""
import argparse
import hashlib
import json
from pathlib import Path

def normalize(path):
    return Path(path).read_text(encoding="utf8").replace("\r\n", "\n")

def code(text):
    return "\n".join(line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#"))

def expected(before):
    result = code(before)
    for enemy in ["SENTRY", "PATROL"]:
        old = f"const {enemy}_MVP_DEFAULT := false"
        assert result.count(old) == 1, old
        result = result.replace(old, f"const {enemy}_MVP_DEFAULT := true")
    return result

def validate(before, after):
    return expected(before) == code(after)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    assert Path(args.before).resolve() != Path(args.after).resolve()
    before, after = normalize(args.before), normalize(args.after)
    assert validate(before, after), "Code changed outside the two default constants"
    for function, override, flag, default in [
        ("patrol_animation_enabled", "patrol_animation_override", "PATROL_ANIMATION_CLI_FLAG", "PATROL_MVP_DEFAULT"),
        ("sentry_v2_enabled", "sentry_v2_override", "SENTRY_V2_CLI_FLAG", "SENTRY_MVP_DEFAULT"),
    ]:
        block = (f"static func {function}() -> bool:\n\tif {override} >= 0:\n"
                 f"\t\treturn {override} == 1\n\treturn OS.get_cmdline_user_args().has({flag}) or {default}")
        assert block in after, function
    for field in ["SENTRY_V2_ART_APPROVED", "SENTRY_V2_SPRITE_ACCEPTED", "PATROL_ANIMATION_ART_APPROVED"]:
        assert f"const {field} := false" in after
    mutations = {
        "enemy_hp": after.replace('"max_hp": 64', '"max_hp": 65', 1),
        "lost_explicit_off": after.replace("if sentry_v2_override >= 0:", "if sentry_v2_override > 0:", 1),
    }
    for name, mutated in mutations.items():
        assert mutated != after and not validate(before, mutated), name
    result = {"passed": True, "onlyCodeChanges": ["SENTRY_MVP_DEFAULT false->true", "PATROL_MVP_DEFAULT false->true"],
              "commentUpdatesAllowed": "full-line comments only", "negativeCopiesRefused": list(mutations),
              "overridePriorityUnchanged": True, "artAcceptanceFlagsFalse": True,
              "hashAlgorithm": "sha256-utf8-text-lf",
              "sourceHashes": {"before": hashlib.sha256(before.encode()).hexdigest(),
                               "after": hashlib.sha256(after.encode()).hexdigest()}}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf8")
    print("ENEMY51_SOURCE_SCOPE_PASS;2negative copies refused")

if __name__ == "__main__":
    main()
