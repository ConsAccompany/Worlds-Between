"""Hash receipt for the fcx-v03 exact render optimization (UNAPPROVED, unscored, opt-in pilot only).

sha256-text-lf-v1 (CRLF -> LF only) for text files, sha256-bytes for everything else. Also asserts that the files
outside this task's scope (driver, package JSON, south runtime JSON, hosts) still have their v02 hashes and that the
WEST model is byte-identical to its frozen copy.
    python -I <this> <checkout root>
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(sys.argv[1])
TEXT = {".gd", ".json", ".log", ".md", ".txt", ".py"}
P = "rpg-2-star-ocean-the-second_female-complete-explore"
ID = "20261019-190421-fcx3a1b7"
OUT = os.path.join(ROOT, "outputs", "fcx-v03")


def digest(path):
    data = open(path, "rb").read()
    if os.path.splitext(path)[1].lower() in TEXT:
        return "sha256-text-lf-v1", hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
    return "sha256-bytes", hashlib.sha256(data).hexdigest()


def entry(rel):
    algo, value = digest(os.path.join(ROOT, rel))
    return {"path": rel.replace(os.sep, "/"), "algorithm": algo, "sha256": value}


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, encoding="utf-8").stdout.strip()


fexp = "game/scripts/fexp"
models = sorted(f for f in os.listdir(os.path.join(ROOT, fexp)) if "-model_" in f and f.endswith(".gd"))
frozen = "outputs/fcx-v03/frozen-v02"
v02 = {"east": "f526e06e4dd577e9cbde3a619ca29f1f8993680138270c9cc51e417ba6de0d8e",
       "north": "1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562",
       "south": "80bfd5e1b2118914b9ffaa9f911d9cf5353d80f9b9eb784608cc147c4c18e911",
       "west": "2ca7cee64887bc99c16f768b349f3e88baa0568bfba50fc953fa7d9eed499ace"}
checks = {}
for f in models:
    d = f.split("_female-complete-explore_")[1].split("-model")[0]
    checks["frozen_%s_equals_v02" % d] = digest(os.path.join(ROOT, frozen, f))[1] == v02[d]
checks["west_current_equals_frozen"] = digest(os.path.join(ROOT, fexp, [m for m in models if "west" in m][0]))[1] == v02["west"]
out_of_scope = {
    "game/scripts/fexp/" + P + "_driver_pilot-v01_20261019-184900-f2c0a7e1.gd": "e468c1f9560be06c9ef63a1394c2fc3b9e7b3f556c4984aa598e2be80ca67a5b",
}
for rel, want in out_of_scope.items():
    checks["unchanged " + rel.split("/")[-1]] = digest(os.path.join(ROOT, rel))[1] == want
# Package / south runtime JSON and hosts must match the v02 hash receipt.
v02_receipt = json.load(open(os.path.join(ROOT, "outputs", "fcx-v02", P + "_hash-receipt_v02_20261019-185900-f2c0a7e1.json"), encoding="utf-8"))
recorded = {}


def walk(node):
    if isinstance(node, dict):
        path = node.get("path") or node.get("file")
        value = node.get("sha256") or node.get("sha256_text_lf_v1") or node.get("sha256_bytes")
        if isinstance(path, str) and isinstance(value, str):
            recorded[path.replace("\\", "/")] = value
        for v in node.values():
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)


walk(v02_receipt)
for section in ("text", "bytes", "binary"):
    for rel, value in (v02_receipt.get(section) or {}).items():
        if isinstance(value, str):
            recorded[rel.replace("\\", "/")] = value
for rel, want in sorted(recorded.items()):
    if any(k in rel for k in ("data/fexp/", "scifi_exploration_area.gd", "survey_annex.gd", "exploration_sprite_set_pilot.gd", "chicago")):
        full = os.path.join(ROOT, rel)
        if os.path.exists(full):
            checks["unchanged " + rel.split("/")[-1]] = digest(full)[1] == want
evidence = []
for dirpath, _, files in os.walk(OUT):
    for f in sorted(files):
        if f.startswith(P + "_hash-receipt_v03"):
            continue
        evidence.append(entry(os.path.relpath(os.path.join(dirpath, f), ROOT)))
tools = sorted(f for f in os.listdir(os.path.join(ROOT, "tools")) if ID in f)
receipt = {
    "schema": "worlds-between.fcx-v03-hash-receipt.v1",
    "status": "UNAPPROVED, unscored, not default; opt-in pilot only; exact render optimization (no art/state/cadence change)",
    "hash_normalization": {"text": "sha256-text-lf-v1 (CRLF->LF only) for " + ", ".join(sorted(TEXT)), "binary": "sha256-bytes"},
    "source_revision": {"head": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                        "note": "working tree, nothing committed or staged by this task"},
    "frozen_v02_models": [entry(os.path.join(frozen, f)) for f in models],
    "optimized_models": [entry(os.path.join(fexp, f)) for f in models],
    "tools": [entry(os.path.join("tools", f)) for f in tools],
    "evidence": evidence,
    "scope_checks": checks,
}
# Not vacuous: driver + package + south runtime + loader + both hosts must have been compared.
checks["out_of_scope_files_compared_ge_6"] = sum(1 for k in checks if k.startswith("unchanged ")) >= 6
ok = all(checks.values())
receipt["scope_checks_pass"] = ok
path = os.path.join(OUT, P + "_hash-receipt_v03_" + ID + ".json")
with open(path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, indent=1)
for k, v in checks.items():
    print(("OK  " if v else "BAD ") + k)
print("RECEIPT", digest(path)[1], "entries", len(evidence) + len(tools) + 2 * len(models))
print("FCX_V03_RECEIPT_PASS" if ok else "FCX_V03_RECEIPT_FAIL")
sys.exit(0 if ok else 1)
