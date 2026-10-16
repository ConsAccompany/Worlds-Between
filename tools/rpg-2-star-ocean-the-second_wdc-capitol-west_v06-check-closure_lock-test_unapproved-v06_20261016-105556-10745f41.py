"""UNAPPROVED, NONRUNTIME, TEST-ONLY: negative tests for the v06 Capitol West builder's clean-clone closure (Task K).

Proves the v04 LOCK relaxation is narrow and the other locks still bite. It imports the v06 builder
(tools/...walkable-scale-depth_pixelorama-build_unapproved-v06_20261016-071733-18b9cea3.py), points its REPO at a
throwaway mirror under %LOCALAPPDATA%\\Temp holding copies of only the files that lock_check() and
own_artifacts_check() read, and mutates the mirror. Nothing in the repo is written. No Pixelorama, no Godot.

Cases:
  1 baseline mirror (with v04 if the source tree has it): LOCK all_ok, own artifacts 16/16
  2 v04 dir absent: LOCK all_ok, v04 reported absent
  3 v04 present but one file changed: LOCK fails (the optional entry still guards when present)
  4 v05 candidate dir absent: LOCK fails (mandatory tracked predecessor)
  5 vista v02 dir: one file changed -> LOCK fails
  6 a v06 output capture changed by one byte: own artifacts fail
  7 a v06 candidate JSON converted to CRLF: own artifacts still 16/16 (text digest is line-ending independent)
  8 a v06 candidate file absent: own artifacts fail
Run: python -I -B <this file>     (exit 0 only if every case behaves as stated)
"""
import importlib.util, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
BUILDER = os.path.join(HERE, "rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_pixelorama-build_"
                             "unapproved-v06_20261016-071733-18b9cea3.py")
V04 = "game/assets/environments/candidates/wdc-capitol-west-v04_20261016-004457-a17af0a6"
LONG = "\\\\?\\"
VISTA = "game/assets/environments/candidates/wdc-dome-west-v02_20261016-044903-cdb4ebdb"


def FS(p):
    """Extended-length path on Windows: mirror paths exceed MAX_PATH (260) under %TEMP%."""
    p = os.path.abspath(p)
    return LONG + p if os.name == "nt" and not p.startswith(LONG) else p


def load():
    spec = importlib.util.spec_from_file_location("cw6", BUILDER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def copy_rel(src_root, dst_root, rel):
    s, d = os.path.join(src_root, *rel.split("/")), os.path.join(dst_root, *rel.split("/"))
    if os.path.isdir(FS(s)):
        shutil.copytree(FS(s), FS(d))
    elif os.path.isfile(FS(s)):
        os.makedirs(FS(os.path.dirname(d)), exist_ok=True)
        shutil.copyfile(FS(s), FS(d))


def first_file(root, rel, ext=None):
    d = os.path.join(root, *rel.split("/"))
    fs = sorted(f for f in os.listdir(FS(d)) if ext is None or f.endswith(ext))
    return os.path.join(d, fs[0])


def flip_last_byte(p):
    with open(FS(p), "rb") as f:
        b = bytearray(f.read())
    b[-1] ^= 1
    with open(FS(p), "wb") as f:
        f.write(bytes(b))


def main():
    m = load()
    have_v04 = os.path.isdir(os.path.join(REPO, *V04.split("/")))
    base = tempfile.mkdtemp(prefix="wb-cw6k-", dir=os.environ.get("LOCALAPPDATA") and
                            os.path.join(os.environ["LOCALAPPDATA"], "Temp"))
    results = []

    def mirror(name):
        root = os.path.join(base, name)
        for rel in list(m.LOCK) + [m.CAND_REL, m.OUT_REL]:
            copy_rel(REPO, root, rel)
        m.REPO = root
        return root

    def case(label, ok):
        results.append((label, ok))
        print(("PASS " if ok else "FAIL ") + label)

    try:
        r = mirror("c1"); lk, oa = m.lock_check(), m.own_artifacts_check()
        case(f"1 baseline (v04 in source tree: {have_v04}): lock all_ok, own 16/16",
             lk["all_ok"] and oa["all_ok"] and oa["count"] == 16 and
             lk["optional_absent"] == ([] if have_v04 else [V04]))

        r = mirror("c2"); v04_dir = FS(os.path.join(r, *V04.split("/")))
        if os.path.isdir(v04_dir):
            shutil.rmtree(v04_dir)
        lk = m.lock_check()
        case("2 v04 absent: lock all_ok and v04 reported absent", lk["all_ok"] and lk["optional_absent"] == [V04]
             and lk["entries"][V04]["present"] is False)

        if have_v04:
            r = mirror("c3"); flip_last_byte(first_file(r, V04)); lk = m.lock_check()
            case("3 v04 present but changed: lock fails", not lk["all_ok"] and lk["entries"][V04]["status"] == "MISMATCH")
        else:
            print("SKIP 3 v04 present but changed (no v04 dir in this tree, e.g. a clean clone)")

        r = mirror("c4"); v05c = f"game/assets/environments/candidates/{m.V05_RUN}"
        shutil.rmtree(FS(os.path.join(r, *v05c.split("/")))); lk = m.lock_check()
        case("4 v05 candidate dir absent: lock fails", not lk["all_ok"] and lk["entries"][v05c]["status"] == "MISSING")

        r = mirror("c5"); flip_last_byte(first_file(r, VISTA, ".png")); lk = m.lock_check()
        case("5 vista v02 file changed: lock fails", not lk["all_ok"] and lk["entries"][VISTA]["status"] == "MISMATCH")

        r = mirror("c6"); flip_last_byte(first_file(r, m.OUT_REL, ".png")); oa = m.own_artifacts_check()
        case("6 v06 capture changed: own artifacts fail", not oa["all_ok"] and oa["matched"] == 15)

        r = mirror("c7"); p = first_file(r, m.CAND_REL, ".json")
        with open(FS(p), "rb") as f:
            b = f.read()
        with open(FS(p), "wb") as f:
            f.write(b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))   # already CRLF in an autocrlf=true clone
        oa = m.own_artifacts_check()
        case("7 v06 candidate JSON as CRLF: own artifacts still 16/16", oa["all_ok"] and oa["matched"] == 16)

        r = mirror("c8"); os.remove(FS(first_file(r, m.CAND_REL, ".gpl"))); oa = m.own_artifacts_check()
        case("8 v06 candidate file absent: own artifacts fail", not oa["all_ok"] and oa["matched"] == 15)
    finally:
        m.REPO = REPO
        shutil.rmtree(FS(base), ignore_errors=True)
    n_ok = sum(ok for _, ok in results)
    print(f"{n_ok}/{len(results)} cases PASS")
    return 0 if n_ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
