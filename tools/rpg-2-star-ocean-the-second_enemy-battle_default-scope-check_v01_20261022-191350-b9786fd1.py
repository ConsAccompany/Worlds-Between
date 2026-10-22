#!/usr/bin/env python3
"""Bounded source-scope validator for the enemy-battle MVP-default preparation.

It is text-only: it never imports, parses as an AST, evals or executes GDScript.
The core predicate is an exact, independently derived transformation:
candidate == original + two comment/const insertions + two enabled-return tails.
Any other byte difference, including ENEMIES stats, telegraph/hit timing,
_finish_battle and result logic, is refused. Inputs are read only.

Exit codes: 0 pass, 1 scope/self-check failure, 2 path or file error.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SENTRY_ANCHOR = 'const SENTRY_V2_CLI_FLAG := "--sentry-v2-pilot"'
PATROL_ANCHOR = 'const PATROL_ANIMATION_CLI_FLAG := "--patrol-battle-animation-pilot"'
COMMENT = "# Prepared MVP switch; separate creator authorization is required before true."
SENTRY_CONST = "const SENTRY_MVP_DEFAULT := false"
PATROL_CONST = "const PATROL_MVP_DEFAULT := false"

PATROL_OLD = (
    "static func patrol_animation_enabled() -> bool:\n"
    "\tif patrol_animation_override >= 0:\n"
    "\t\treturn patrol_animation_override == 1\n"
    "\treturn OS.get_cmdline_user_args().has(PATROL_ANIMATION_CLI_FLAG)"
)
PATROL_NEW = PATROL_OLD.replace(
    "\treturn OS.get_cmdline_user_args().has(PATROL_ANIMATION_CLI_FLAG)",
    "\treturn OS.get_cmdline_user_args().has(PATROL_ANIMATION_CLI_FLAG) or PATROL_MVP_DEFAULT",
)
SENTRY_OLD = (
    "static func sentry_v2_enabled() -> bool:\n"
    "\tif sentry_v2_override >= 0:\n"
    "\t\treturn sentry_v2_override == 1\n"
    "\treturn OS.get_cmdline_user_args().has(SENTRY_V2_CLI_FLAG)"
)
SENTRY_NEW = SENTRY_OLD.replace(
    "\treturn OS.get_cmdline_user_args().has(SENTRY_V2_CLI_FLAG)",
    "\treturn OS.get_cmdline_user_args().has(SENTRY_V2_CLI_FLAG) or SENTRY_MVP_DEFAULT",
)

INSERTIONS = (
    (SENTRY_ANCHOR, SENTRY_CONST),
    (PATROL_ANCHOR, PATROL_CONST),
)
BLOCK_PAIRS = (
    (PATROL_OLD, PATROL_NEW),
    (SENTRY_OLD, SENTRY_NEW),
)


def normalize_lf(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def function_block(source, name):
    marker = "static func %s() -> bool:\n" % name
    start = source.find(marker)
    if start < 0:
        return None
    end = source.find("\n\n\n", start)
    if end < 0:
        end = len(source)
    return source[start:end]


def enemies_block(source):
    marker = "const ENEMIES := {"
    start = source.find(marker)
    if start < 0:
        return None
    end = source.find("\n}", start)
    if end < 0:
        return None
    return source[start:end + 2]


def derive_expected(original):
    """Build the only candidate this task authorizes, or return (None, reasons)."""
    expected = original
    reasons = []
    for anchor, const_line in INSERTIONS:
        if expected.count(anchor) != 1:
            reasons.append("anchor not unique: %s" % anchor)
            continue
        insertion = anchor + "\n" + COMMENT + "\n" + const_line
        expected = expected.replace(anchor, insertion, 1)
    for old_block, new_block in BLOCK_PAIRS:
        if expected.count(old_block) != 1:
            reasons.append("enabled-method shape not unique: %s" % old_block.splitlines()[0])
            continue
        expected = expected.replace(old_block, new_block, 1)
    if reasons:
        return None, reasons
    return expected, []


def validate_pair(original, candidate):
    """Return a report fragment. Both strings are already LF-normalized."""
    checks = []

    def check(check_id, ok, detail):
        checks.append({"id": check_id, "status": "PASS" if ok else "FAIL", "detail": detail})
        return ok

    c_ok = check(
        "inputs_are_lf_text",
        bool(original.strip()) and bool(candidate.strip())
        and "\x00" not in original and "\x00" not in candidate,
        "both snapshots are non-empty UTF-8 text; CRLF/lone CR normalized to LF",
    )

    check(
        "original_has_no_default_consts",
        "SENTRY_MVP_DEFAULT" not in original and "PATROL_MVP_DEFAULT" not in original,
        "original source contains neither SENTRY_MVP_DEFAULT nor PATROL_MVP_DEFAULT",
    )

    expected, derive_reasons = derive_expected(original)
    check(
        "original_has_exact_anchors_and_enabled_methods",
        expected is not None,
        "one sentry anchor, one patrol anchor, and the two override-first enabled methods; "
        + ("; ".join(derive_reasons) if derive_reasons else "shape as expected"),
    )

    exact = expected is not None and candidate == expected
    check(
        "candidate_equals_exact_authorized_transformation",
        exact,
        "candidate equals original plus exactly: comment+const after each CLI_FLAG, and "
        "'existing flag or MVP_DEFAULT' in the two enabled returns; no other byte differs",
    )

    declarations = re.findall(r"^const (SENTRY|PATROL)_MVP_DEFAULT := (\w+)$", candidate, re.M)
    defaults_false = (
        sorted(declarations) == [("PATROL", "false"), ("SENTRY", "false")]
    )
    check(
        "new_defaults_are_false_and_unique",
        defaults_false,
        "each new MVP default is declared once and stays false (activation is not authorized)",
    )

    scoped = True
    for const_name in ("SENTRY_MVP_DEFAULT", "PATROL_MVP_DEFAULT"):
        if candidate.count(const_name) != 2:
            scoped = False
    for anchor, const_line in INSERTIONS:
        pair = anchor + "\n" + COMMENT + "\n" + const_line
        if candidate.count(pair) != 1:
            scoped = False
    check(
        "new_defaults_have_only_declaration_and_one_return_use",
        scoped,
        "each default appears exactly twice: its false declaration and one enabled-return tail",
    )

    methods_ok = True
    for name, old_block, new_block in (
        ("patrol_animation_enabled", PATROL_OLD, PATROL_NEW),
        ("sentry_v2_enabled", SENTRY_OLD, SENTRY_NEW),
    ):
        got = function_block(candidate, name)
        if got != new_block:
            methods_ok = False
    check(
        "enabled_methods_override_priority_and_fallback",
        methods_ok,
        "both methods keep 'override >= 0 -> override == 1' first, then existing CLI flag or new false default",
    )

    remaining = candidate
    for anchor, const_line in INSERTIONS:
        remaining = remaining.replace(anchor + "\n" + COMMENT + "\n" + const_line, anchor, 1)
    for old_block, new_block in BLOCK_PAIRS:
        remaining = remaining.replace(new_block, old_block, 1)
    check(
        "unchanged_remainder_equals_original_exactly",
        remaining == original,
        "removing only the two authorized insertions and restoring the two old returns "
        "reproduces the original exactly: ENEMIES stats, hitboxes/telegraph timing, "
        "_finish_battle and result/presentation logic are unchanged",
    )

    old_enemies = enemies_block(original)
    new_enemies = enemies_block(candidate)
    enemies_same = old_enemies is not None and old_enemies == new_enemies
    check(
        "enemies_block_exact",
        enemies_same,
        "the whole const ENEMIES block (names, max_hp, damage, speed, windup, cooldown, color) is byte-identical",
    )

    stats_ok = False
    expected_stats = (("patrol", "64"), ("sentry", "96"))
    if new_enemies is not None:
        stats_ok = all(
            re.search(r'"%s": \{[^}]*"max_hp": %s,' % (enemy, hp), new_enemies)
            for enemy, hp in expected_stats
        )
    check(
        "enemies_expected_max_hp",
        stats_ok,
        "patrol max_hp 64 and sentry max_hp 96 remain present",
    )

    ok = c_ok and all(item["status"] == "PASS" for item in checks)
    return {
        "ok": ok,
        "status": "PASS" if ok else "FAIL",
        "checks": checks,
        "hashes": {
            "original_sha256_lf": sha256_text(original),
            "candidate_sha256_lf": sha256_text(candidate),
            "original_bytes_lf": len(original.encode("utf-8")),
            "candidate_bytes_lf": len(candidate.encode("utf-8")),
        },
    }


def mutated_negative_tests(original, candidate):
    """Build three in-memory invalid copies; each must be refused."""
    tests = []

    def one(name, description, old, new):
        if candidate.count(old) != 1:
            tests.append({
                "name": name,
                "description": description,
                "refused": False,
                "failed_checks": ["MUTATION_NOT_APPLIED"],
            })
            return
        result = validate_pair(original, candidate.replace(old, new, 1))
        failed = [item["id"] for item in result["checks"] if item["status"] == "FAIL"]
        tests.append({
            "name": name,
            "description": description,
            "refused": not result["ok"],
            "failed_checks": failed,
        })

    one(
        "max_hp_changed",
        "ENEMIES patrol max_hp 64 -> 65",
        '"max_hp": 64',
        '"max_hp": 65',
    )
    one(
        "sentry_default_flipped_true",
        "SENTRY_MVP_DEFAULT false -> true",
        SENTRY_CONST,
        "const SENTRY_MVP_DEFAULT := true",
    )
    one(
        "patrol_flag_condition_dropped",
        "patrol enabled return loses the existing CLI-flag condition",
        "\treturn OS.get_cmdline_user_args().has(PATROL_ANIMATION_CLI_FLAG) or PATROL_MVP_DEFAULT",
        "\treturn PATROL_MVP_DEFAULT",
    )
    return tests


def read_source(path):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError("cannot read %s: %s" % (path, exc))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("%s is not valid UTF-8: %s" % (path, exc))
    if not text.strip():
        raise ValueError("%s is empty" % path)
    return normalize_lf(text)


def check_paths(original, candidate, out):
    problems = []
    for label, path in (("original", original), ("candidate", candidate)):
        if not path.exists():
            problems.append("%s path does not exist: %s" % (label, path))
        elif not path.is_file():
            problems.append("%s path is not a regular file: %s" % (label, path))
    if original == candidate:
        problems.append("original and candidate resolve to the same path")
    if out == original or out == candidate:
        problems.append("out path must not be either input path")
    if out.exists():
        try:
            if out.samefile(original) or out.samefile(candidate):
                problems.append("out path aliases an input file")
        except OSError:
            problems.append("cannot stat out path: %s" % out)
    if out.exists() and out.is_dir():
        problems.append("out path is a directory: %s" % out)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Text-only enemy-battle default preparation scope validator; never executes GDScript."
    )
    parser.add_argument("--original", required=True, help="original enemy_battle.gd snapshot")
    parser.add_argument("--candidate", required=True, help="prepared enemy_battle.gd snapshot")
    parser.add_argument("--out", required=True, help="JSON report path")
    args = parser.parse_args(argv)

    try:
        original_path = Path(args.original).expanduser().resolve()
        candidate_path = Path(args.candidate).expanduser().resolve()
        out_path = Path(args.out).expanduser().resolve()
    except OSError as exc:
        print("PATH_ERROR %s" % exc, file=sys.stderr)
        return 2

    problems = check_paths(original_path, candidate_path, out_path)
    if problems:
        for problem in problems:
            print("PATH_ERROR %s" % problem, file=sys.stderr)
        return 2

    try:
        original_text = read_source(original_path)
        candidate_text = read_source(candidate_path)
    except ValueError as exc:
        print("INPUT_ERROR %s" % exc, file=sys.stderr)
        return 2

    result = validate_pair(original_text, candidate_text)
    negatives = mutated_negative_tests(original_text, candidate_text)
    negatives_ok = all(item["refused"] for item in negatives)
    result["checks"].append({
        "id": "three_negative_copies_refused",
        "status": "PASS" if negatives_ok else "FAIL",
        "detail": "in-memory copies with changed max_hp, flipped SENTRY_MVP_DEFAULT, "
                  "or dropped patrol flag condition are all refused",
    })
    if not negatives_ok:
        result["ok"] = False
        result["status"] = "FAIL"

    original_after = read_source(original_path)
    candidate_after = read_source(candidate_path)
    unchanged = (
        sha256_text(original_after) == result["hashes"]["original_sha256_lf"]
        and sha256_text(candidate_after) == result["hashes"]["candidate_sha256_lf"]
    )
    result["checks"].append({
        "id": "inputs_not_mutated",
        "status": "PASS" if unchanged else "FAIL",
        "detail": "re-read after validation is byte-identical to the hashed normalized sources",
    })
    if not unchanged:
        result["ok"] = False
        result["status"] = "FAIL"

    report = {
        "schema": "rpg-2-star-ocean-the-second_enemy-battle_default-scope-check_v01",
        "status": result["status"],
        "ok": result["ok"],
        "normalization": "UTF-8 strict; CRLF and lone CR normalized to LF; hashes are over LF text",
        "source_paths": {
            "original": str(original_path),
            "candidate": str(candidate_path),
        },
        "hashes": result["hashes"],
        "checks": result["checks"],
        "negative_tests": negatives,
        "authorization": {
            "creator_activation_authorized": "not inferred",
            "final_art_approved": "not inferred",
        },
        "limitations": [
            "text-only scope check; GDScript is not evaluated or executed",
            "passing proves this snapshot's byte-level preparation scope, not gameplay or art approval",
        ],
        "python": sys.version.split()[0],
    }

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    except OSError as exc:
        print("OUTPUT_ERROR %s" % exc, file=sys.stderr)
        return 2

    for item in result["checks"]:
        print("%s %s" % (item["status"], item["id"]))
    for item in negatives:
        print("%s negative/%s" % ("REFUSED" if item["refused"] else "ACCEPTED", item["name"]))
    print("REPORT %s" % out_path)
    print("STATUS %s" % result["status"])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
