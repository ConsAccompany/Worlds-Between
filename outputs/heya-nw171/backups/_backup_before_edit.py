#!/usr/bin/env python3
"""Back up an existing development file before editing it.

Creates a unique directory under outputs/heya-nw171/backups/, copies with `cp -a --preserve=all`
(mode/owner/timestamps/xattrs where permitted), verifies source==backup SHA-256 and metadata, and
writes a per-backup receipt. Exit 1 if any verification fails.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--intent", required=True)
    a = ap.parse_args()
    src = Path(a.path).resolve()
    if not src.is_file():
        raise SystemExit(f"not a file: {src}")
    before = src.stat()
    hash_before = sha(src)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    label = re.sub(r"[^A-Za-z0-9_.-]+", "-", a.label).strip("-")[:80] or "file"
    uid = uuid.uuid4().hex[:8]
    dest_dir = ROOT / "outputs/heya-nw171/backups" / f"{stamp}_{label}_{uid}"
    dest_dir.mkdir(parents=True, exist_ok=False)
    dest = dest_dir / "original"
    subprocess.run(["cp", "-a", "--preserve=all", str(src), str(dest)], check=True)
    after = dest.stat()
    hash_after = sha(dest)
    source_after_hash = sha(src)
    checks = {
        "sha256_equal": hash_before == hash_after,
        "source_unchanged": hash_before == source_after_hash,
        "size_equal": before.st_size == after.st_size,
        "mode_equal": stat.S_IMODE(before.st_mode) == stat.S_IMODE(after.st_mode),
        "mtime_ns_equal": int(before.st_mtime_ns) == int(after.st_mtime_ns),
        "uid_equal": before.st_uid == after.st_uid,
        "gid_equal": before.st_gid == after.st_gid,
    }
    receipt = {
        "schema": "worlds-between.backup-before-edit.v1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "intent": a.intent,
        "source": str(src.relative_to(ROOT)),
        "backup": str(dest.relative_to(ROOT)),
        "source_sha256_before": hash_before,
        "source_sha256_after": source_after_hash,
        "backup_sha256": hash_after,
        "bytes": before.st_size,
        "source_stat": {"mode": oct(stat.S_IMODE(before.st_mode)), "mtime_ns": int(before.st_mtime_ns),
                        "uid": before.st_uid, "gid": before.st_gid},
        "backup_stat": {"mode": oct(stat.S_IMODE(after.st_mode)), "mtime_ns": int(after.st_mtime_ns),
                        "uid": after.st_uid, "gid": after.st_gid},
        "verification": checks,
        "verified": all(checks.values()),
        "command": f"cp -a --preserve=all {src} {dest}",
    }
    rp = dest_dir / "backup-receipt.json"
    rp.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"verified": receipt["verified"], "source": receipt["source"], "backup": receipt["backup"],
                      "sha256": hash_after, "receipt": str(rp.relative_to(ROOT)), "checks": checks}, indent=2))
    return 0 if receipt["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
