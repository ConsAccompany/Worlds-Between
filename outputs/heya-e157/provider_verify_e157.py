"""Batch157 provider verification for content.char.heya.static-east.

Read-only over existing source/native/fit evidence plus the two fresh e157 checks.
Writes only outputs/heya-e157/provider-verification.json. Never edits game/assets,
tools, docs, ledger, Bible, registry or the Git index.
"""
import hashlib
import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / "outputs/heya-e157"
PKG = R / "game/assets/characters/heya-native-v01/east"
STAGE = R / "outputs/heya-e155/staging/east"

EXPECTED_PKG = {
    "rpg-2-star-ocean-the-second_heya_east-static_unapproved-v01_20261024-141500-6041ee95.png":
        "273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4",
    "rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-5493fe7b.pxo":
        "45ab6257e31b20fb756e1d18c687d1716c73d2fa22489737ed86fd5348e2bf56",
    "rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-d23c7857.ora":
        "0cf8b0b465560bf6328de320f2e40f356cb5d304c3c546227de3a2ba12e8bc91",
    "rpg-2-star-ocean-the-second_heya_east-palette_unapproved-v01_20261024-141500-f7eba38b.json":
        "6af85c7ac9e1dfc76a44a53864d9a7ef58c7d02d1c3e3e8ab1d71b50e6d55311",
    "rpg-2-star-ocean-the-second_heya_east-manifest_unapproved-v01_20261024-141500-489081a6.json":
        "dc5e13978247c8781955785f2d5ef46a0ac0fe26ced3e03ed98ea1a871a6302d",
    ".gdignore": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ".gitattributes": "7db6a4594ca028c9756c1c6f838e247424a086289bc4516147589efdaf27380c",
}
EXPECTED_TOOLS = {
    "tools/rpg-2-star-ocean-the-second_heya_east-static-author_unapproved-v01_20261024-141500-h155e001.py":
        "42c06afb67653975e3e2a385f2e7cd30c5ba936080f3fc14e9bb7b1e8b5c23e0",
    "tools/rpg-2-star-ocean-the-second_heya_east-static-source-check_v01_20261024-141500-h155e001.py":
        "66f691cd68685d3201b07933c7335cdd33148cc13c7983294669ba3d744e2c01",
    "tools/rpg-2-star-ocean-the-second_heya_east-static-native-pixelorama-check_v01_20261024-141500-h155e001.py":
        "544a6eacaf8d35db3d22a4ac31ae45d8fcd7dca2f18ef8df21b01bf37b988973",
    "tools/rpg-2-star-ocean-the-second_heya_east-static-source-fit_v01_20261024-141500-h155e001.py":
        "7609ef8616f306142b0a099b6f25f73af69d1c97fe84807fde6befeeb7eb8d86",
    "tools/wb_safe_replace.py":
        "b2ae290f49515a89893c729fc354fb5a55e33ca85135511f668be65f6e3b7595",
}
PROTECTED = [
    "outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json",
    "outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json",
    "docs/coordination/rpg-2-star-ocean-the-second_workflow-operating_registry-v01_20261018-211617-6d390c24.json",
    "outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json",
    "outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json",
    "game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json",
    ".git/index",
]
DEPENDENCIES = {
    "south": "game/assets/characters/heya-native-v01/south/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json",
    "west": "game/assets/characters/heya-native-v01/west/rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json",
    "north": "game/assets/characters/heya-native-v01/north/rpg-2-star-ocean-the-second_heya_north-manifest_unapproved-v01_20261024-134500-ee613b85.json",
}
DEP_SHA = {
    "south": "d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c",
    "west": "75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752",
    "north": "7445095eec59c152a0f580acf0d63f17ec900be4824c1eb35cd2fc7a8064c0f7",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(rows, name, ok, detail=None):
    rows.append({"id": name, "passed": bool(ok), "detail": detail})


def main():
    rows = []
    # 1. installed package + staging identity
    pkg = {p.name: sha(p) for p in PKG.iterdir() if p.is_file()}
    check(rows, "installed_exact_expected_set", pkg == EXPECTED_PKG, pkg)
    stage = {p.name: sha(p) for p in STAGE.iterdir() if p.is_file()}
    check(rows, "staging_equals_installed_bytes",
          all(pkg.get(k) == v for k, v in stage.items()) and set(stage) == set(EXPECTED_PKG) - {".gitattributes"},
          {"stage": stage, "install": pkg})
    manifest = json.loads(next(PKG.glob("*manifest*.json")).read_text(encoding="utf8"))
    declared = {v["file"]: v["rawsha256"] for v in manifest.get("files", {}).values()}
    check(rows, "manifest_declares_installed_hashes",
          all(declared.get(k) == v for k, v in EXPECTED_PKG.items() if k in declared),
          {"declared": declared})
    check(rows, "manifest_native_80x112_scale_0.5",
          manifest.get("canvas") == [80, 112] and manifest.get("display_scale") == 0.5
          and manifest.get("logical_height_px") == 48,
          {"canvas": manifest.get("canvas"), "display_scale": manifest.get("display_scale"),
           "logical_height_px": manifest.get("logical_height_px")})

    # 2. fresh e157 author-check log
    author_log = (OUT / "provider-author-check.log").read_text(encoding="utf8", errors="replace")
    check(rows, "e157_author_check_exit_marker",
          "HEYA_EAST_V01_ALL_OK" in author_log and '"hard_failures": []' in author_log,
          {"sha256": sha(OUT / "provider-author-check.log")})
    disk_lines = [l for l in author_log.splitlines() if "disk_matches_rebuild" in l or "true" in l]
    check(rows, "e157_author_check_stage_install_disk_all_true",
          author_log.count(": true") >= 10 and "false" not in author_log.split("disk_matches_rebuild")[1].split("hard_failures")[0],
          None)

    # 3. fresh e157 independent source check
    ind_path = next((OUT / "provider-independent-1").glob("*independent-source-proof*.json"))
    ind = json.loads(ind_path.read_text(encoding="utf8"))
    check(rows, "e157_independent_passed", ind.get("passed") is True, {"n": len(ind.get("checks", []))})
    check(rows, "e157_independent_57_of_57",
          len(ind.get("checks", [])) == 57 and all(c.get("passed") for c in ind["checks"]),
          {"failed": [c["id"] for c in ind.get("checks", []) if not c.get("passed")]})
    check(rows, "e157_independent_checker_hash_matches_tool",
          ind.get("checkerSha256") == EXPECTED_TOOLS[
              "tools/rpg-2-star-ocean-the-second_heya_east-static-source-check_v01_20261024-141500-h155e001.py"])
    check(rows, "e157_independent_source_hashes_match_installed",
          ind.get("sourceHashes") == pkg, {"sourceHashes": ind.get("sourceHashes")})
    check(rows, "e157_independent_scope_is_source_only",
          "no GUI reliability, motion, ordinary adoption or art approval" in ind.get("scope", ""),
          ind.get("scope"))

    # 4. prior e155 independent evidence validity / reproducibility
    for tag in ("independent-1", "independent-2"):
        p = next((R / "outputs/heya-e155" / tag).glob("*independent-source-proof*.json"))
        d = json.loads(p.read_text(encoding="utf8"))
        check(rows, f"e155_{tag}_report_passed",
              d.get("passed") is True and len(d.get("checks", [])) == 57
              and all(c.get("passed") for c in d["checks"]) and d.get("sourceHashes") == pkg,
              {"sha256": sha(p)})
    check(rows, "e155_independent_runs_byte_identical",
          sha(next((R / "outputs/heya-e155/independent-1").glob("*independent-source-proof*.json")))
          == sha(next((R / "outputs/heya-e155/independent-2").glob("*independent-source-proof*.json"))))

    # 5. native evidence validity
    nat_path = next((R / "outputs/heya-e155/native-1").glob("*/*native-pixelorama-export-report*.json"))
    nat = json.loads(nat_path.read_text(encoding="utf8"))
    check(rows, "native_report_equality_passed", nat.get("equality_passed") is True, {"sha256": sha(nat_path)})
    check(rows, "native_all_11_gates_true",
          len(nat.get("gates", {})) == 11 and all(nat["gates"].values()), nat.get("gates"))
    check(rows, "native_diagnostics_not_clean_retained",
          nat.get("diagnostic_clean") is False
          and nat.get("shader_sampler_diagnostic_counts") == {"pxo-flat": 4, "pxo-split": 4, "ora-flat": 4},
          {"diagnostic_note": nat.get("diagnostic_note")})
    check(rows, "native_no_runtime_default_or_art_claim",
          nat.get("runtime_or_default_changed") is False and nat.get("art_approved") is False
          and nat.get("gui_saveas_tested") is False)
    check(rows, "native_package_hashes_match_installed",
          nat["package"]["static_sha256"] == EXPECTED_PKG[Path(nat["package"]["static_png"]).name]
          and nat["package"]["pxo_sha256"] == EXPECTED_PKG[Path(nat["package"]["pxo"]).name]
          and nat["package"]["ora_sha256"] == EXPECTED_PKG[Path(nat["package"]["ora"]).name]
          and nat["tool_sha256"] == EXPECTED_TOOLS[
              "tools/rpg-2-star-ocean-the-second_heya_east-static-native-pixelorama-check_v01_20261024-141500-h155e001.py"])
    run_dir = nat_path.parent
    check(rows, "native_run_logs_present",
          all((run_dir / n / f).exists() for n in ("pxo-flat", "pxo-split", "ora-flat")
              for f in ("stdout.log", "stderr.log")))

    # 6. fit evidence validity (first run and r2)
    fit_rows = []
    for proof_name in ("-fit.json", "-fit-r2.json"):
        p = next((R / "outputs/heya-e155").glob(f"*source-fit-proof*{proof_name}"))
        d = json.loads(p.read_text(encoding="utf8"))
        caps = [R / c for c in d.get("captures", [])]
        man = json.loads((R / d["manifest"]).read_text(encoding="utf8"))
        man_sha = {c["file"]: c["sha256"] for c in man["captures"]}
        ok = (d["result"].get("passed") is True and d["result"].get("exitCode") == 0
              and len(caps) == 4 and man.get("runtimeAdopted") is False and man.get("artApproved") is False
              and d.get("runtimeAdopted") is False and d.get("artApproved") is False
              and d.get("sourceSha256") == EXPECTED_PKG[Path(d["source"]).name]
              and all(v == [640, 360] for v in d.get("captureDimensions", {}).values())
              and all(c.exists() and sha(c) == man_sha.get(c.name) for c in caps))
        fit_rows.append({"proof": str(p.relative_to(R)), "sha256": sha(p), "passed": ok,
                         "captures": [str(c.relative_to(R)) for c in caps],
                         "capture_hashes": {c.name: sha(c) for c in caps if c.exists()},
                         "manifest": d["manifest"], "manifest_sha256": sha(R / d["manifest"]),
                         "log": d["log"], "log_sha256": sha(R / d["log"]) if (R / d["log"]).exists() else None})
    check(rows, "fit_proofs_valid_4x640x360_bilingual_dark_bright",
          len(fit_rows) == 2 and all(r["passed"] for r in fit_rows), fit_rows)
    check(rows, "fit_no_runtime_or_art_claim",
          all(json.loads((R / r["proof"]).read_text(encoding="utf8")).get("runtimeAdopted") is False
              for r in fit_rows))

    # 7. tools / docs pins
    check(rows, "tools_match_declared_pins",
          all(sha(R / rel) == h for rel, h in EXPECTED_TOOLS.items()))
    docs = {
        "docs/qa/rpg-2-star-ocean-the-second_heya_east-static-qa_unapproved-v01_20261024-141500-h155e001.md":
            "509697f82078c0d7a2d22a8ae190e49cd7a3d13299e74f3f14351cf918194d34",
        "docs/qa/rpg-2-star-ocean-the-second_heya_east-style-source-contract_unapproved-v01_20261024-141500-h155e001.md":
            "3d34813cf179f72ef3fb30546cb8a62adcbb22974ab7797f2a3bfd1ebeff489a",
    }
    check(rows, "e155_docs_hashes_match_producer_qa",
          {k: sha(R / k) for k in docs} == docs, {k: sha(R / k) for k in docs})

    # 8. retained failures / preservation audit (not retroactively clean)
    audit = json.loads((R / "outputs/heya-e155/coordinator/preservation-audit.json").read_text(encoding="utf8"))
    check(rows, "preservation_failure_retained_not_cleared",
          audit.get("preservation_failed") is True and len(audit.get("findings", [])) >= 2,
          {"protected_count": audit.get("protected_count"), "changed": audit.get("changed")})
    preview = R / "outputs/heya-e155/author-preview.log"
    failed_png = R / "outputs/heya-e155/author/rpg-2-star-ocean-the-second_heya_east-preview-x12_unapproved-v01_20261024-141500-645dd370.png"
    failed_py = R / "outputs/heya-e155/tmp/failing-author-draft-645dd370.py"
    check(rows, "failed_draft_artifacts_retained",
          failed_png.exists() and failed_py.exists(),
          {"failed_png_sha256": sha(failed_png), "failed_py_sha256": sha(failed_py),
           "preview_log_sha256": sha(preview)})
    backups = []
    for rec in sorted((R / "outputs/heya-e155/source-backups").glob("*/receipt.json")):
        rc = json.loads(rec.read_text(encoding="utf8"))
        orig = rec.parent / "original"
        backups.append({"receipt": str(rec.relative_to(R)), "original_sha256": sha(orig),
                        "receipt_sha256": rc.get("sha256") or rc.get("original", {}).get("sha256"),
                        "matches": (rc.get("sha256") or rc.get("original", {}).get("sha256")) == sha(orig)})
    check(rows, "source_backups_hash_verified", len(backups) == 6 and all(b["matches"] for b in backups), backups)
    check(rows, "preview_log_preservation_failure_retained",
          sha(preview) == "bec339449083dba7b558549f30603d6d9a09fbbb79003eba335e0ff694def09f",
          "author-preview.log was redirected twice over differing content; no unique verified backup; "
          "hash is of the surviving later log, not the lost original")

    # 9. protected before/after hashes
    protected = {rel: sha(R / rel) for rel in PROTECTED}
    deps = {k: {"path": v, "sha256": sha(R / v), "expected": DEP_SHA[k], "matches": sha(R / v) == DEP_SHA[k]}
            for k, v in DEPENDENCIES.items()}
    check(rows, "protected_all_present_and_dependency_pins_match",
          all(protected.values()) and all(d["matches"] for d in deps.values()), protected)
    check(rows, "dependencies_south_west_north_unchanged", all(d["matches"] for d in deps.values()), deps)

    # 10. git index / status scope
    index_before = protected[".git/index"]
    status = subprocess.run(["git", "status", "--porcelain=v1"], cwd=R, capture_output=True, text=True).stdout
    scoped = [l for l in status.splitlines() if "heya-e157" in l or "heya_east" in l or "heya-east" in l]
    check(rows, "git_index_untouched_by_provider", index_before == sha(R / ".git/index"), {"index_sha256": index_before})
    check(rows, "git_status_scope_only_e157_and_east_untracked",
          all(("outputs/heya-e157" in l) or ("heya_east" in l) for l in scoped) and "game/assets/characters/heya-native-v01/east" in status,
          {"scoped_status": scoped, "preexisting_status_count": len(status.splitlines()) - len(scoped)})

    summary = {
        "task": "content.char.heya.static-east",
        "batch": "157",
        "utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "provider": "deepseek",
        "checks": rows,
        "checks_total": len(rows),
        "checks_failed": [r["id"] for r in rows if not r["passed"]],
        "protected_hashes": protected,
        "dependency_pins": deps,
        "installed_package": pkg,
        "staging_package": stage,
        "fresh_independent_report": {"path": str(ind_path.relative_to(R)), "sha256": sha(ind_path)},
        "fresh_author_check_log": {"path": "outputs/heya-e157/provider-author-check.log",
                                   "sha256": sha(OUT / "provider-author-check.log")},
        "fit_evidence": fit_rows,
        "native_evidence": {"path": str(nat_path.relative_to(R)), "sha256": sha(nat_path)},
        "hash_normalization": "none; raw bytes",
    }
    (OUT / "provider-verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"checks_total": summary["checks_total"], "checks_failed": summary["checks_failed"],
                      "installed_package": pkg, "protected_hashes": protected}, indent=2))
    print("HEYA_E157_VERIFY " + ("PASS" if not summary["checks_failed"] else "FAIL"))
    return 0 if not summary["checks_failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
