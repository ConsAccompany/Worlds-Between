"""Fetch/verify the asset handoff; optional historical-root restore never edits game defaults."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, shutil, subprocess, tempfile, urllib.request, zipfile

ROOT = Path(__file__).resolve().parents[1]
def lp(p):
    p = Path(p).absolute()
    return Path("\\\\?\\" + str(p)) if os.name == "nt" and not str(p).startswith("\\\\?\\") else p
def digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1048576), b""): h.update(block)
    return h.hexdigest()
def sha(path):
    with lp(path).open("rb") as f: return digest(f)
def safe(base, relative):
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or any(x in {".", ".."} or ":" in x or "\\" in x for x in parts):
        raise ValueError("unsafe relative path")
    current = Path(base).absolute()
    for part in parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ValueError("symlink/reparse destination refused")
    current.resolve().relative_to(Path(base).resolve())
    return current
def read_index(arg):
    path = Path(arg) if arg else next((ROOT/"assets/handoff").glob("*complete-index*.json"))
    data = json.loads(lp(path).read_text(encoding="utf-8"))
    if data.get("schema") != "worlds-between.asset-handoff-index/1": raise ValueError("wrong schema")
    seen = set()
    for a in data["assets"]:
        if not re.fullmatch("[0-9a-f]{64}", a["sha256"]) or a["sha256"] in seen: raise ValueError("bad/duplicate content identity")
        seen.add(a["sha256"])
        if not isinstance(a["bytes"], int) or a["bytes"] < 0: raise ValueError("bad size")
    return data
def download(data, cache):
    cache.mkdir(parents=True, exist_ok=True)
    for b in data["bundles"]:
        target = safe(cache, b["name"])
        if lp(target).exists():
            if sha(target) != b["sha256"]: raise ValueError("existing cache differs: " + b["name"])
            print("CACHE OK", b["name"], flush=True); continue
        prefix = "https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/main/"
        expected = prefix + b["repositoryPath"]
        if b["url"] != expected: raise ValueError("unexpected download destination")
        fd, temp = tempfile.mkstemp(prefix="wb-assets-", suffix=".part", dir=cache)
        try:
            with os.fdopen(fd, "wb") as out, urllib.request.urlopen(b["url"], timeout=90) as response:
                shutil.copyfileobj(response, out, length=1048576)
            if Path(temp).stat().st_size != b["bytes"] or sha(temp) != b["sha256"]: raise ValueError("archive integrity mismatch")
            os.replace(temp, lp(target))
            print("DOWNLOADED", b["name"], flush=True)
        finally:
            if Path(temp).exists(): Path(temp).unlink()
def repository_bytes(asset):
    path = safe(ROOT, asset["storage"]["path"])
    raw = lp(path).read_bytes()
    if len(raw) == asset["bytes"] and hashlib.sha256(raw).hexdigest() == asset["sha256"]:
        return raw, False
    # Windows text checkouts may convert CRLF. Verify the exact stored Git blob;
    # only a line-ending-only working-copy difference is permitted for text source.
    if path.suffix.lower() not in {".py",".gd",".js",".mjs",".json",".svg",".md",".txt"}:
        raise ValueError("binary repository asset differs: " + asset["storage"]["path"])
    gitraw = subprocess.check_output(["git","cat-file","blob",asset["gitBlob"]],cwd=ROOT)
    if len(gitraw) != asset["bytes"] or hashlib.sha256(gitraw).hexdigest() != asset["sha256"]:
        raise ValueError("stored Git blob differs")
    if raw.replace(b"\r\n",b"\n") != gitraw.replace(b"\r\n",b"\n"):
        raise ValueError("working text differs beyond line endings: " + asset["storage"]["path"])
    return gitraw, True
def verify(data, cache, main_only=False):
    count = 0; archives = {}; text_checkouts = 0
    try:
        for a in data["assets"]:
            s = a["storage"]
            if s["type"] == "git":
                raw, converted = repository_bytes(a)
                text_checkouts += int(converted)
            elif not main_only:
                name = s["bundle"]
                if name not in archives:
                    bundle = next(b for b in data["bundles"] if b["name"] == name)
                    f = safe(cache, name)
                    if not lp(f).exists() or sha(f) != bundle["sha256"]: raise ValueError("missing/different archive: " + name)
                    archives[name] = zipfile.ZipFile(lp(f))
                with archives[name].open(s["member"]) as stream:
                    if digest(stream) != a["sha256"]: raise ValueError("archive member differs: " + s["member"])
            else: continue
            count += 1
    finally:
        for z in archives.values(): z.close()
    print("ASSET_VERIFY_PASS", count, "mode", "repository-only" if main_only else "repository-plus-archives", "exact-Git-text-fallbacks", text_checkouts)
    return count
def restore(data, cache, root_id, destination):
    if root_id not in {r["id"] for r in data["roots"]}: raise ValueError("unknown origin root")
    destination = Path(destination).absolute()
    if destination == ROOT or ROOT/"game" == destination or (ROOT/"game") in destination.parents:
        raise ValueError("restore into a separate archive workspace, never the live game")
    archives = {}; count = 0
    try:
        for a in data["assets"]:
            paths = [r["path"] for r in a["origins"] if root_id in r["roots"]]
            if not paths: continue
            for relative in paths:
                target = safe(destination, relative); s = a["storage"]
                if lp(target).exists():
                    if sha(target) != a["sha256"]: raise ValueError("refusing nonmatching existing file: " + relative)
                    continue
                lp(target.parent).mkdir(parents=True, exist_ok=True)
                if s["type"] == "git":
                    raw, _ = repository_bytes(a)
                    lp(target).write_bytes(raw)
                else:
                    if s["bundle"] not in archives:
                        bundle = next(b for b in data["bundles"] if b["name"] == s["bundle"])
                        zpath = safe(cache, bundle["name"])
                        if sha(zpath) != bundle["sha256"]: raise ValueError("archive SHA mismatch before restore")
                        archives[s["bundle"]] = zipfile.ZipFile(lp(zpath))
                    with archives[s["bundle"]].open(s["member"]) as source, lp(target).open("xb") as out:
                        shutil.copyfileobj(source,out,1048576)
                if sha(target) != a["sha256"]: raise ValueError("restored file differs")
                count += 1
    finally:
        for z in archives.values(): z.close()
    print("ASSET_RESTORE_PASS", root_id, count, str(destination))
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest"); p.add_argument("--cache-dir", default=str(ROOT/"assets/handoff/packages"))
    p.add_argument("--download",action="store_true"); p.add_argument("--verify",action="store_true")
    p.add_argument("--verify-main",action="store_true"); p.add_argument("--restore-root"); p.add_argument("--destination")
    a = p.parse_args()
    if not any([a.download,a.verify,a.verify_main,a.restore_root]): p.error("choose --download, --verify, --verify-main or --restore-root")
    if a.restore_root and not a.destination: p.error("--restore-root needs --destination")
    data = read_index(a.manifest); cache = Path(a.cache_dir).absolute()
    if a.download: download(data,cache)
    if a.verify or a.verify_main: verify(data,cache,a.verify_main and not a.verify)
    if a.restore_root: restore(data,cache,a.restore_root,a.destination)
if __name__ == "__main__": main()
