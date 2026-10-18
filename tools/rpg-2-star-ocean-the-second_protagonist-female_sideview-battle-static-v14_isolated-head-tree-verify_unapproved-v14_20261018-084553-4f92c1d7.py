"""UNAPPROVED, read-only verifier for the isolated tree used by the female battle idle STATIC v14 captures (NONRUNTIME).

The isolated tree is `git -c core.autocrlf=false archive <commit> game` extracted into a temp dir, plus exactly the
enumerated v14 files copied in (the candidate PNG, .pxo, .ora and manifest under game/, the author tool and the capture
script under tools/). This tool proves, before and after the Godot runs, that:
  1. every file of <commit>:game/ is present in the tree and byte-identical to its git blob (git blob sha1 compared);
  2. every enumerated file is present and its sha256 equals the same file in this working tree;
  3. every other file in the tree is a Godot import product: under game/.godot/, or a *.import / *.uid sidecar of a file
     that is in the tree (reported by kind; anything else is listed as unexpected and fails);
  4. game/scripts/battle_arena.gd is <commit>'s blob (the dirty band-capable working-tree copy is never used).
Writes nothing; prints one JSON report; exit 0 only if every check passes.

Run from the repo:  python -I -B <this file> <isolated dir> <commit> <enumerated rel path> [...]
"""
import hashlib, json, os, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _fs(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\") else path


def read(path):
    with open(_fs(path), "rb") as f:
        return f.read()


def git_blob_sha1(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def head_blobs(commit):
    out = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "-z", commit, "--", "game"], capture_output=True,
                         check=True).stdout.decode("utf-8")
    blobs = {}
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, kind, sha = meta.split()
        if kind == "blob":
            blobs[path] = sha
    return blobs


def walk(root):
    files = []
    for d, _, names in os.walk(_fs(root)):
        for n in names:
            rel = os.path.relpath(os.path.join(d, n), _fs(root)).replace("\\", "/")
            files.append(rel)
    return sorted(files)


def main():
    iso, commit, enumerated = sys.argv[1], sys.argv[2], sys.argv[3:]
    blobs = head_blobs(commit)
    files = walk(iso)
    present = set(files)
    missing = [p for p in blobs if p not in present]
    mismatched = [p for p, sha in blobs.items() if p in present and git_blob_sha1(read(os.path.join(iso, p))) != sha]
    enum = {}
    for rel in enumerated:
        here = os.path.join(REPO, *rel.split("/"))
        there = os.path.join(iso, *rel.split("/"))
        enum[rel] = {"present": rel in present,
                     "sha256": hashlib.sha256(read(there)).hexdigest() if rel in present else None,
                     "equals_working_tree_file": rel in present and read(there) == read(here)}
    extra = {"godot_dir": 0, "import_sidecars": 0, "uid_sidecars": 0, "unexpected": []}
    for rel in files:
        if rel in blobs or rel in enum:
            continue
        if rel.startswith("game/.godot/"):
            extra["godot_dir"] += 1
        elif rel.endswith(".import") and rel[:-len(".import")] in present:
            extra["import_sidecars"] += 1
        elif rel.endswith(".uid") and rel[:-len(".uid")] in present:
            extra["uid_sidecars"] += 1
        else:
            extra["unexpected"].append(rel)
    arena = "game/scripts/battle_arena.gd"
    arena_ok = arena in blobs and arena in present and git_blob_sha1(read(os.path.join(iso, arena))) == blobs[arena]
    report = {
        "status": "UNAPPROVED, NONRUNTIME read-only isolated-tree verification; writes nothing",
        "isolated_dir": iso.replace("\\", "/"), "commit": commit,
        "commit_game_files": len(blobs), "commit_game_files_missing": missing,
        "commit_game_files_not_byte_identical": mismatched,
        "enumerated_files": enum, "other_files": extra,
        "battle_arena_gd_is_commit_blob": arena_ok,
        "battle_arena_gd_commit_blob_sha1": blobs.get(arena),
        "battle_arena_gd_sha256_lf": hashlib.sha256(read(os.path.join(iso, arena))).hexdigest() if arena_ok else None,
    }
    ok = (not missing and not mismatched and all(v["present"] and v["equals_working_tree_file"] for v in enum.values())
          and not extra["unexpected"] and arena_ok)
    report["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
