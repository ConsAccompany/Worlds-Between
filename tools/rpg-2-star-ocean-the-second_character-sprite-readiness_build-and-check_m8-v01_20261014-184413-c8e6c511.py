"""Build and check the per-variant character sprite production readiness checklist.

Read-only with respect to the visual registry, asset inventory, manifests and art.
It never marks anything approved itself: every acceptance status mirrors a
user-controlled inventory ``checked`` flag; all prose and counters are derived.
The only hand-entered decisions are USER_STATIC_BASELINES (single static frames the
user approved as a visual baseline), which are hash-locked and never pass a gate.

Content hashes name their algorithm. Binary files (PNG) use ``sha256-bytes``: SHA-256 of the
exact file bytes. Text files (JSON/Markdown) use ``sha256-text-lf-v1``: SHA-256 of the file
bytes after every CRLF pair is replaced by LF, so a lock gives the same value in an LF checkout
and in a Windows ``core.autocrlf=true`` CRLF checkout. Nothing else is normalized, and input
holding a NUL byte or invalid UTF-8 is refused rather than hashed as text.

Usage:
  python <this file> --write   # regenerate the JSON + Markdown checklist
  python <this file>           # check mode: invariants + artifacts are up to date
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "rpg-2-star-ocean-the-second"
REGISTRY = ROOT / "game/data/character-visuals" / f"{SLUG}_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json"
INVENTORY = ROOT / "outputs" / f"{SLUG}_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json"
CORE_HAIR = ROOT / "outputs" / f"{SLUG}_core-cast_hairstyle-manifest_v02_20261013-161317-4f5a6c7d.md"
REMAINING = ROOT / "outputs" / f"{SLUG}_remaining-companions_character-sheet-manifest_v01_20261013-194808-b6d7ee1d.md"
SPEC = ROOT / "docs/character-visuals" / f"{SLUG}_character-visual-spec_topdown-v01_20261014-135700-17a0c9d4.md"
INTAKE = ROOT / "docs/character-visuals" / f"{SLUG}_character-visuals_asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md"
OUT_JSON = ROOT / "game/data/character-visuals" / f"{SLUG}_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json"
OUT_MD = ROOT / "docs/character-visuals" / f"{SLUG}_character-sprite-readiness-checklist_m8-v01_20261014-184413-5d914f92.md"
CHARACTERS_DIR = ROOT / "game/assets/characters"

DIRECTIONS = ["south", "west", "north", "east"]
EXPECTED_VARIANTS = 52
EXPECTED_IDENTITIES = 51
CITY_DISPLAY_HEIGHT_LOGICAL_PX = 48  # user-approved display height, per intake checklist
PLACEHOLDER_SIZE = (32, 48)  # legacy placeholder cell rejected as the art baseline
PILOTS = "game/assets/characters/pixelorama-pilots"
V8_RUN = f"{SLUG}_{{scene}}_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png"
# User-recorded static still-frame baselines. Each is a single static frame the user approved as the visual reference;
# it is NOT a G1-G5 gate pass, does not check any inventory item and never changes a gate status or counter.
# Check mode re-verifies every hash; any change to the files voids the record.
BYTES_HASH = "sha256-bytes"
TEXT_HASH = "sha256-text-lf-v1"
# The v8 manifest was first locked as 0fa7937d…5992, the raw SHA-256 of its CRLF Windows working copy. The same
# content under sha256-text-lf-v1 is 3ba35811…10ed, which is also the raw SHA-256 of the LF blob in commit ff8acd8.
USER_STATIC_BASELINES = {
    "protagonist-female": {
        "facing": "south",
        "pose": "idle",
        "frames": 1,
        "display_height_logical_px": CITY_DISPLAY_HEIGHT_LOGICAL_PX,
        "candidate": "selout v8 cloth-leather",
        "decided_by": "user",
        "decided_on": "2026-10-14",
        "user_reply_zh": "够了，可作为静止帧基准",
        "reviewed_captures": ["city-bright", "outskirts-bright"],
        "decision_record": f"docs/character-visuals/{SLUG}_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md",
        "files": {
            "png": (f"{PILOTS}/{SLUG}_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png",
                    BYTES_HASH, "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"),
            "manifest": (f"{PILOTS}/{SLUG}_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json",
                         TEXT_HASH, "3ba35811bf4d55b061b7719c6451908bdbb1eb68425bdda2c2303cc669f310ed"),
            "qa_report": (f"outputs/{SLUG}_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json",
                          TEXT_HASH, "513ab6595fd3bedee02d8477e9a2646c7d98b40f19de8791d147e746e3ea631a"),
            "capture_city_bright": (f"outputs/{V8_RUN.format(scene='city-bright')}",
                                    BYTES_HASH, "0b8e67ac75539fdac46e7843687d660d0dfa98697f7bf229b0079437351d9e65"),
            "capture_outskirts_bright": (f"outputs/{V8_RUN.format(scene='outskirts-bright')}",
                                         BYTES_HASH, "b4cedaddc7832850e2904e798e92c36ca479966e8c59453f1bb05e11d881c12f"),
            "capture_annex_dark": (f"outputs/{V8_RUN.format(scene='survey-annex-room2-dark')}",
                                   BYTES_HASH, "da444d274b21a529859b306af612d46859087ef2785bc0d66f9e19f9682d5b0c"),
            "qa_note": (f"docs/qa/{SLUG}_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md", None, None),
        },
        "not_approved": ["exploration_animation", "other_facings", "runtime_replacement", "runtime_sprite_acceptance",
                         "scene_quality_gates", "human_playtests"],
    },
}
ROBOT_REGION = "星外"

# Candidate confusions at sprite scale, for HUMAN review only. Each group quotes the
# registry anchors verbatim at build time; nothing here changes canon or portraits.
HAIR_REVIEW_GROUPS = [
    ("chin-length-straight", ["nalia", "yelan"],
     "两者锚点都以「齐颌…直发」开头；区分依赖单侧细辫与平刘海，48 px 背面需确认仍可分。"),
    ("single-thin-side-braid", ["nalia", "gu-lin"],
     "两者都含单侧细辫，且发长均在齐颌／齐耳附近；区分依赖发色与细辫颜色。"),
    ("single-long-braid", ["muxiu", "mi-yi"],
     "单条及背长辫 vs 低位鱼骨辫：背面同为单条下垂辫，需确认长度/编法在 48 px 可见。"),
    ("twin-braids", ["adi", "isai", "ruan-tian"],
     "均为两条辫；粗长 / 饰珠细辫 / 两侧短辫簇的差异需在北向（背面）确认。"),
    ("low-coiled-or-bun", ["liang-xu", "heya", "ye-qiao", "xuan-ya"],
     "盘发 / 颈后盘辫 / 贴头盘绕短辫 / 双短髻都是贴头团状轮廓，需核对位置与数量。"),
    ("very-short-crop", ["milo", "daga", "xida", "kern", "pei-zhi"],
     "极短寸／圆寸／平头在 48 px 下轮廓接近；区分依赖鬓角发片、侧纹、发色。"),
    ("shaved-sides", ["jiang-lan", "su-yan", "luowen", "ji-cheng", "han-ze"],
     "多种剃侧／剃短造型；上方发束、卷、斜刘海、齐肩直发、莫霍克需各自保留独特外廓。"),
    ("fluffy-short", ["protagonist-male", "sain", "sangguo", "lin-que"],
     "蓬松／层次／碎层短发相近；主角男为可玩角色，需确认与同屏伙伴不混淆。"),
    ("short-curls", ["yanke", "tao-yu", "aiti", "wu-li"],
     "短卷发类；区分依赖胡须、发色、贴头程度与高蓬体量。"),
    ("low-tied-back", ["lin-yan", "ruima"],
     "低马尾 vs 低束发，文字描述几乎同义；区分只剩发色（蓝黑 / 银灰）。"),
    ("silver-white-hair", ["liang-xu", "sain", "he-huai", "ruima", "ji-cheng", "tao-li"],
     "银白／灰白发色集中；颜色不能作为唯一身份提示（视觉规格要求），需靠外廓区分。"),
    ("shoulder-length-straight", ["chenxian", "ji-cheng", "bu-he"],
     "披肩／齐肩直发；布禾包在布巾里、纪澄耳后剃短，需确认外廓不同。"),
    ("bald-or-receding", ["zhou-he", "tao-li"],
     "光头 vs 光亮额头＋短白发圈；侧/背面需确认可分。"),
]
# Anchors that do not describe the hair shape itself, flagged for human confirmation.
ANCHOR_NOTES = {
    "lairui": "锚点只描述发夹（「黑色双侧短羽形发夹」），未写发型本身。",
    "an-suo": "锚点为「无帽短发」，发型描述泛化；主要识别点在一字胡与票夹。",
    "luo-qi": "锚点未描述发型，只有白眉、胡须与草帽；草帽是否常驻需确认。",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_lf_bytes(data: bytes) -> bytes:
    """sha256-text-lf-v1 input: the bytes with each CRLF pair replaced by LF. Refuses non-text input."""
    if b"\x00" in data:
        raise ValueError("NUL byte: not a text file")
    data.decode("utf-8")  # raises UnicodeDecodeError (a ValueError) on invalid UTF-8
    return data.replace(b"\r\n", b"\n")


def text_sha256(path: Path) -> str:
    return hashlib.sha256(text_lf_bytes(path.read_bytes())).hexdigest()


def content_hash(path: Path, algorithm: str) -> str:
    if algorithm == BYTES_HASH:
        return sha256(path)
    if algorithm == TEXT_HASH:
        return text_sha256(path)
    raise ValueError(f"unknown hash algorithm {algorithm!r}")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def git_tracked() -> set[str] | None:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True, encoding="utf-8")
    except (OSError, subprocess.CalledProcessError):
        return None
    return set(out.stdout.splitlines())


def path_record(path: str | None, tracked: set[str] | None) -> dict | None:
    if not path:
        return None
    exists = (ROOT / path).is_file()
    return {"path": path, "exists": exists, "git_tracked": None if tracked is None else path in tracked}


def png_size(path: str) -> tuple[int, int] | None:
    head = (ROOT / path).read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


def acceptance(item: dict | None) -> str:
    return "art_accepted" if item and item.get("checked") else "pending"


def load_manifest(path: str) -> dict | None:
    full = ROOT / path
    if not full.is_file():
        return None
    return json.loads(full.read_text(encoding="utf-8"))


def static_baseline(visual_id: str) -> dict | None:
    spec = USER_STATIC_BASELINES.get(visual_id)
    if spec is None:
        return None
    files = {}
    for role, (path, algorithm, expected) in spec["files"].items():
        full = ROOT / path
        record = {"path": path, "exists": full.is_file()}
        if expected:
            record["sha256_algorithm"] = algorithm
            record["sha256"] = expected
            try:
                record["sha256_matches"] = record["exists"] and content_hash(full, algorithm) == expected
            except ValueError as error:
                record["sha256_matches"] = False
                record["sha256_error"] = str(error)
        files[role] = record
    return {**{k: v for k, v in spec.items() if k != "files"}, "decision_record_exists": (ROOT / spec["decision_record"]).is_file(), "files": files,
            "scope_note": "single static frame approved as the visual baseline only; not a G1-G5 pass, not runtime-integrated, no counter changes"}


def find_manifests(visual_id: str) -> list[str]:
    hits = sorted(CHARACTERS_DIR.rglob(f"{SLUG}_{visual_id}_*manifest*.json"))
    return [rel(p) for p in hits]


def inventory_items(inventory: dict) -> dict[str, dict]:
    characters = next(c for c in inventory["categories"] if c["id"] == "characters")
    return {item["id"]: item for group in characters["subcategories"] for item in group["items"]}


def build(tracked: set[str] | None) -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inv = inventory_items(inventory)
    entries = registry["entries"]
    by_id = {e["visual_id"]: e for e in entries}

    missing: list[dict] = []
    untracked: list[dict] = []
    untracked_discovered: list[dict] = []
    discrepancies: list[str] = []

    def note_path(owner: str, role: str, record: dict | None) -> None:
        if record is None:
            return
        if not record["exists"]:
            missing.append({"visual_id": owner, "role": role, "path": record["path"]})
        elif record["git_tracked"] is False:
            untracked.append({"visual_id": owner, "role": role, "path": record["path"]})

    variants = []
    for ordinal, e in enumerate(entries, start=1):
        vid = e["visual_id"]
        ex, combat, display = e["exploration"], e["combat"], e["runtime_display"]
        identity_id = "protagonist" if vid.startswith("protagonist-") else vid

        source = path_record(e["source_portrait"]["path"], tracked)
        note_path(vid, "source_portrait", source)
        if source and source["exists"] != e["source_portrait"]["exists"]:
            discrepancies.append(f"{vid}: registry source_portrait.exists={e['source_portrait']['exists']} but file exists={source['exists']}")

        direction_records = {}
        for d in DIRECTIONS:
            rec = path_record((ex.get("directions") or {}).get(d), tracked)
            direction_records[d] = rec
            note_path(vid, f"exploration_placeholder_{d}", rec)

        walk_manifest = path_record(ex.get("walk_manifest"), tracked)
        note_path(vid, "exploration_walk_manifest", walk_manifest)
        combat_manifest = path_record(combat.get("manifest"), tracked)
        note_path(vid, "combat_manifest", combat_manifest)

        registered = {r["path"] for r in (walk_manifest, combat_manifest) if r}
        frame_paths_checked = 0
        for role, rec in (("exploration_frame", walk_manifest), ("combat_frame", combat_manifest)):
            manifest = load_manifest(rec["path"]) if rec and rec["exists"] else None
            for frame in (manifest or {}).get("frames", []):
                frame_paths_checked += 1
                note_path(vid, role, path_record(frame["path"], tracked))
            if manifest is not None and role == "exploration_frame":
                manifest_id = manifest.get("visual_id") or manifest.get("character_id")
                if manifest_id is not None and manifest_id != vid:
                    discrepancies.append(f"{vid}: exploration manifest id is '{manifest_id}', registry visual_id is '{vid}'")

        all_manifests = find_manifests(vid)
        frame_count_manifests = [p for p in all_manifests if "frame_counts" in (load_manifest(p) or {})]
        # A manifest declaring frame_counts is not a production frame set unless it says art_approved=true.
        unapproved_frame_count_manifests = [p for p in frame_count_manifests if (load_manifest(p) or {}).get("art_approved") is not True]
        unregistered = [p for p in all_manifests if p not in registered]
        # Discovered manifests are outside note_path's registry-referenced scope; report untracked ones separately.
        if tracked is not None:
            untracked_discovered += [{"visual_id": vid, "path": p} for p in unregistered if p not in tracked]
        unregistered_exploration = [p for p in unregistered if "native-exploration" in p or "native-animation" in p]
        if unregistered_exploration and ex["production_status"] == "not_started":
            discrepancies.append(f"{vid}: registry exploration is not_started but unregistered manifest exists: {', '.join(unregistered_exploration)}")
        for path in unregistered_exploration:
            for frame in (load_manifest(path) or {}).get("frames", []):
                frame_paths_checked += 1
                note_path(vid, "unregistered_manifest_frame", path_record(frame["path"], tracked))

        inv_sprite = inv.get(f"runtime-sprite.{vid}", {})
        inv_display = inv.get(f"display.{vid}", {})
        inv_combat = inv.get(f"playable-combat.{vid}")
        combat_scope = inv_combat.get("scope", "MVP") if inv_combat else inv.get("combat-sprite.other-companions", {}).get("scope", "unknown")
        user_checked = bool(inv_sprite.get("checked"))

        has_directions = all(direction_records[d] and direction_records[d]["exists"] for d in DIRECTIONS)
        direction_sizes = {d: png_size(direction_records[d]["path"]) for d in DIRECTIONS} if has_directions else {}
        if has_directions and all(size == PLACEHOLDER_SIZE for size in direction_sizes.values()):
            readiness = "placeholder_32x48_rejected_baseline"
        elif has_directions:
            readiness = "registered_directions_pending_review"
        elif unregistered_exploration:
            readiness = "unregistered_placeholder_manifest"
        else:
            readiness = "not_started"

        anchor_source = rel(CORE_HAIR) if e["companion_number"] is None or e["companion_number"] <= 15 else rel(REMAINING)
        variants.append({
            "ordinal": ordinal,
            "visual_id": vid,
            "identity_id": identity_id,
            "display_name_zh": e["display_name_zh"],
            "roster": e["roster"],
            "companion_number": e["companion_number"],
            "region_board": e["region"],
            "identity_and_hair_anchor": e["identity_and_hair_anchor"],
            "anchor_source": anchor_source,
            "anchor_has_hair": e["region"] != ROBOT_REGION,
            "readiness_state": readiness,
            # Stage 0 is only provable while no manifest declares production frame counts;
            # anything further needs human review against the intake checklist.
            "intake_stage": None if frame_count_manifests else 0,
            "frame_count_manifests": frame_count_manifests,
            "frame_count_manifests_unapproved": unapproved_frame_count_manifests,
            "gates": {
                "source_art": {
                    "approval": e["source_portrait"]["approval"],
                    "portrait": source,
                    "note": "approval is the registry/inventory value; this checklist does not change it",
                },
                "four_facing": {
                    "required_directions": DIRECTIONS,
                    "production_directions_done": [],
                    "placeholder_directions": {d: r["path"] for d, r in direction_records.items() if r},
                    "registered_direction_sizes": {d: list(s) if s else None for d, s in direction_sizes.items()},
                    "west_authoring": "undeclared",
                    "status": "pending",
                },
                "exploration_animation": {
                    "registry_production_status": ex["production_status"],
                    "registry_review_status": ex["review_status"],
                    "placeholder_idle_frames": ex.get("idle_frames", 0),
                    "placeholder_walk_frames": ex.get("walk_frames", 0),
                    "placeholder_manifest": walk_manifest,
                    "unregistered_manifests": unregistered,
                    "static_idle_baseline": static_baseline(vid),
                    "production_frame_counts": None,
                    "frame_counts_user_approved": False,
                    "status": "pending",
                },
                "combat_animation": {
                    "inventory_scope": combat_scope,
                    "mvp_required": combat_scope == "MVP",
                    "registry_production_status": combat["production_status"],
                    "registry_review_status": combat["review_status"],
                    "prototype_actions": combat.get("action_count", 0),
                    "prototype_frames": combat.get("frame_count", 0),
                    "prototype_manifest": combat_manifest,
                    "inventory_item": f"playable-combat.{vid}" if inv_combat else None,
                    "inventory_checked": bool(inv_combat and inv_combat.get("checked")),
                    "status": acceptance(inv_combat) if combat_scope == "MVP" else "out_of_mvp_scope",
                },
                "runtime_display": {
                    "registry_production_status": display["production_status"],
                    "registry_review_status": display["review_status"],
                    "inventory_stage": inv_display.get("stage"),
                    "inventory_checked": bool(inv_display.get("checked")),
                    "status": acceptance(inv_display),
                },
                "scale": {
                    "target_display_height_logical_px": CITY_DISPLAY_HEIGHT_LOGICAL_PX,
                    "review_viewport": "1280x720 canvas_items, science city",
                    "master": None,
                    "scale": None,
                    "cell_size": None,
                    "ground_pin": None,
                    "status": "pending_pilot_values",
                },
                "qa": {
                    "automated_metadata_checks": "not_run" if frame_count_manifests else "not_run_no_production_frames",
                    "in_engine_capture_receipt": None,
                    "human_identity_direction_review": "pending",
                    "frame_paths_cross_checked": frame_paths_checked,
                    "status": "pending",
                },
                "art_acceptance": {
                    "status": acceptance(inv_sprite),
                    "decided_by": "user_only",
                    "inventory_item": f"runtime-sprite.{vid}",
                    "inventory_stage": inv_sprite.get("stage"),
                    "inventory_checked": user_checked,
                    "receipt": None,
                },
            },
        })

    groups = []
    for key, ids, concern in HAIR_REVIEW_GROUPS:
        groups.append({
            "group": key,
            "members": [{"visual_id": i, "display_name_zh": by_id[i]["display_name_zh"], "anchor": by_id[i]["identity_and_hair_anchor"]} for i in ids],
            "concern": concern,
            "decision": "pending_human_review",
        })
    anchor_counts: dict[str, list[str]] = {}
    for e in entries:
        anchor_counts.setdefault(e["identity_and_hair_anchor"], []).append(e["visual_id"])
    exact_duplicates = {a: ids for a, ids in anchor_counts.items() if len(ids) > 1}

    frame_count_manifests = [p for v in variants for p in v["frame_count_manifests"]]
    identity_count = len({v["identity_id"] for v in variants})

    return {
        "schema_version": 1,
        "kind": "character_sprite_production_readiness_checklist",
        "scope": {
            "visual_variants": len(variants),
            "character_identities": identity_count,
            "mvp": f"all {identity_count} characters need an in-game visual identity ({len(variants)} variants); playable content is the science region",
            "combat_mvp_variants": [v["visual_id"] for v in variants if v["gates"]["combat_animation"]["mvp_required"]],
        },
        "sources": {
            "registry": {"path": rel(REGISTRY), "sha256_algorithm": TEXT_HASH, "sha256": text_sha256(REGISTRY)},
            "inventory": {"path": rel(INVENTORY), "sha256_algorithm": TEXT_HASH, "sha256": text_sha256(INVENTORY)},
            "visual_spec": rel(SPEC),
            "intake_checklist": rel(INTAKE),
            "core_hairstyle_manifest": rel(CORE_HAIR),
            "remaining_companions_manifest": rel(REMAINING),
        },
        "policy": {
            "art_acceptance": "only the user may accept art; each status mirrors the user-controlled inventory checked flag (runtime-sprite / playable-combat / display); this script does not locate or verify the intake-checklist receipt file",
            "batch_gate": "no batch production until one variant passes intake stage 4 and the user approves production frame counts",
            "frame_counts": "user approval of production frame counts is not machine-detectable here; 20 = existing placeholder layout, 48 = single-character pilot proposal",
            "content_hashes": {
                BYTES_HASH: "SHA-256 of the exact file bytes; used for binary files (PNG)",
                TEXT_HASH: "SHA-256 of the file bytes after each CRLF pair is replaced by LF; used for text files (JSON, Markdown) so locks match in LF and CRLF checkouts; NUL bytes or invalid UTF-8 are refused, nothing else is normalized",
            },
        },
        "summary": {
            "source_portraits": {k: sum(v["gates"]["source_art"]["approval"] == k for v in variants) for k in ("approved", "concept")},
            "readiness_states": {s: sum(v["readiness_state"] == s for v in variants) for s in sorted({v["readiness_state"] for v in variants})},
            "art_accepted": sum(v["gates"]["art_acceptance"]["status"] == "art_accepted" for v in variants),
            "art_pending": sum(v["gates"]["art_acceptance"]["status"] == "pending" for v in variants),
            "combat_mvp_accepted": sum(v["gates"]["combat_animation"]["status"] == "art_accepted" for v in variants),
            "runtime_display_accepted": sum(v["gates"]["runtime_display"]["status"] == "art_accepted" for v in variants),
            "static_idle_baselines_user_approved": [v["visual_id"] for v in variants if v["gates"]["exploration_animation"]["static_idle_baseline"]],
            "any_manifest_declares_frame_counts": bool(frame_count_manifests),
            "frame_count_manifests": frame_count_manifests,
            "frame_count_manifests_unapproved": [p for v in variants for p in v["frame_count_manifests_unapproved"]],
            "intake_stage_0": sum(v["intake_stage"] == 0 for v in variants),
            "missing_paths": len(missing),
            "untracked_referenced_paths": len(untracked),
            "untracked_discovered_manifests": len(untracked_discovered),
            "git_status_checked": tracked is not None,
        },
        "variants": variants,
        "hair_review": {
            "exact_duplicate_anchors": exact_duplicates,
            "candidate_confusion_groups": groups,
            "anchor_notes": [{"visual_id": k, "anchor": by_id[k]["identity_and_hair_anchor"], "note": n} for k, n in ANCHOR_NOTES.items()],
            "no_hair_robot_variants": [v["visual_id"] for v in variants if not v["anchor_has_hair"]],
            "anchors_with_persona_prose": [v["visual_id"] for v in variants if "。" in v["identity_and_hair_anchor"]],
        },
        "path_check": {"missing": missing, "untracked_but_referenced": untracked,
                       "untracked_discovered_manifests": untracked_discovered, "registry_discrepancies": discrepancies},
    }


STATE_LABEL = {
    "placeholder_32x48_rejected_baseline": "有 32×48 占位帧（已被否定为画质基线）",
    "registered_directions_pending_review": "注册表四方向帧非 32×48 占位，待人工复核",
    "unregistered_placeholder_manifest": "有未登记的 32×48 占位清单",
    "not_started": "未开始",
}


def mark(record: dict | None) -> str:
    if record is None:
        return "—"
    flag = "存在" if record["exists"] else "**缺失**"
    if record["exists"] and record["git_tracked"] is False:
        flag += "（未纳入 git）"
    return f"`{record['path']}` · {flag}"


def box(status: str) -> str:
    return "[x]" if status == "art_accepted" else "[ ]"


def render_md(data: dict) -> str:
    s, src = data["summary"], data["sources"]
    total = data["scope"]["visual_variants"]
    variants = data["variants"]
    combat_mvp = [v for v in variants if v["gates"]["combat_animation"]["mvp_required"]]
    combat_other = [v for v in variants if not v["gates"]["combat_animation"]["mvp_required"]]
    other_scopes = "/".join(sorted({v["gates"]["combat_animation"]["inventory_scope"] for v in combat_other})) or "—"
    combat_frames = sorted({v["gates"]["combat_animation"]["prototype_frames"] for v in combat_mvp})
    anchor_split = {name: sum(v["anchor_source"] == src[key] for v in variants)
                    for key, name in (("core_hairstyle_manifest", "core"), ("remaining_companions_manifest", "remaining"))}
    persona_ids = set(data["hair_review"]["anchors_with_persona_prose"])
    persona_numbers = [v["companion_number"] for v in variants if v["visual_id"] in persona_ids and v["companion_number"] is not None]
    persona_range = f"编号 {min(persona_numbers)}–{max(persona_numbers)}" if persona_numbers else "无编号"
    any_accepted = s["art_accepted"] or s["combat_mvp_accepted"] or s["runtime_display_accepted"]
    if s["art_accepted"]:
        acceptance_line = f"「美术验收」已勾选 {s['art_accepted']}/{total}（镜像资产清单 runtime-sprite 的用户勾选；本脚本不核对回执文件），其余为 **pending**"
    else:
        acceptance_line = "所有「美术验收」均为 **pending**"
    if s["frame_count_manifests"]:
        unapproved = set(s["frame_count_manifests_unapproved"])
        frames_line = (f"- 正式生产帧（经用户美术验收）：{s['art_accepted']}/{total}。另检测到 {len(s['frame_count_manifests'])} 份清单声明 `frame_counts`（"
                       + "、".join(f"`{p}`" for p in s["frame_count_manifests"])
                       + f"），其中 {len(unapproved)} 份未标 `art_approved=true`，只是待人工评审的试点帧，不是正式生产帧；"
                       f"相关变体入库阶段未自动推导，需按入库检查清单人工复核。其余 {s['intake_stage_0']}/{total} 个变体处于入库阶段 0。")
    else:
        frames_line = f"- 正式生产帧：0/{total}。所有清单均未声明 `frame_counts`，因此所有变体处于入库阶段 0（未达阶段 1）。"
    L = [
        "# 《世界之间》角色精灵制作就绪检查清单（逐变体）v0.1",
        "",
        "**状态：事实清单，不批准任何素材。** 本文由脚本从视觉注册表与资产清单只读生成，未改动注册表、现有美术、进度计数或 Game Bible。"
        + acceptance_line + "；只有用户可以验收（见[入库检查清单](" + Path(src["intake_checklist"]).name + ") 第 9 节）。",
        "",
        f"- 机器可读版：`{rel(OUT_JSON)}`",
        f"- 生成／校验脚本：`{rel(Path(__file__))}`（`--write` 重新生成；无参数为校验模式）",
        f"- 注册表：`{src['registry']['path']}`（{src['registry']['sha256_algorithm']} `{src['registry']['sha256'][:16]}…`）",
        f"- 资产清单：`{src['inventory']['path']}`（{src['inventory']['sha256_algorithm']} `{src['inventory']['sha256'][:16]}…`）",
        f"- 哈希算法：二进制文件（PNG）用 `{BYTES_HASH}`（原始字节）；文本文件（JSON/Markdown）用 `{TEXT_HASH}`"
        "（仅把 CRLF 换成 LF 后计算 SHA-256，LF 与 CRLF 检出结果相同；含 NUL 或非 UTF-8 的文件拒绝按文本处理）。",
        f"- 规格：[俯视视觉规格](" + Path(src["visual_spec"]).name + f")；发型锚点来源：核心 {anchor_split['core']} 个变体取自 `" + Path(src["core_hairstyle_manifest"]).name
        + f"`（用户批准的发型参考），其余 {anchor_split['remaining']} 名取自 `" + Path(src["remaining_companions_manifest"]).name + "`。",
        "",
        "## 范围与汇总",
        "",
        f"- **{total} 个视觉变体 / {data['scope']['character_identities']} 名角色**（主角男女为同一角色的两种外观）。MVP：{data['scope']['character_identities']} 名角色都需要游戏内视觉身份；可玩内容为科技区。",
        f"- 来源立绘：approved {s['source_portraits']['approved']} / concept {s['source_portraits']['concept']}（注册表现值，本文不改）。",
        f"- 就绪状态：" + "；".join(f"{STATE_LABEL[k]} {n}" for k, n in s["readiness_states"].items()) + "。",
        f"- 美术验收（runtime-sprite）：已验收 {s['art_accepted']} / 待定 {s['art_pending']}；MVP 战斗动作已验收 {s['combat_mvp_accepted']}/{len(combat_mvp)}；显示图已验收 {s['runtime_display_accepted']}/{total}。",
        frames_line,
        f"- 用户批准的静态待机基准帧：{len(s['static_idle_baselines_user_approved'])} 个变体（"
        + ("、".join(f"`{i}`" for i in s["static_idle_baselines_user_approved"]) or "无")
        + "）。只批准单张静态视觉基准，不算任何闸门通过，不计入上面的美术验收或探索精灵数。",
        f"- 战斗动作 MVP 必需（资产清单 scope=MVP）：" + "、".join(f"`{v}`" for v in data["scope"]["combat_mvp_variants"]) + f"；其余 {len(combat_other)} 名战斗组在资产清单中为 {other_scopes} 范围，不属 MVP。",
        f"- 路径核对：缺失 {s['missing_paths']} 个；已引用但未纳入 git {s['untracked_referenced_paths']} 个（详见末节）。",
        "",
        "## 闸门定义（每个变体相同）",
        "",
        "| 闸门 | 通过条件 | 依据 |",
        "|---|---|---|",
        "| G0 来源立绘 | 立绘文件存在；`approval` 只记录注册表现值，approved/concept 由用户决定，本清单不改写 | 注册表 `source_portrait` |",
        "| G1 四方向 | `south`/`west`/`north`/`east` 四向正式帧齐全；西向独立绘制，若为东向镜像须标 `mirrored_east` 并经用户接受 | 规格「四朝向」、入库 §5 |",
        "| G2 探索动画 | 每方向待机＋行走，帧数按清单 `frame_counts` 声明且经用户批准（20=占位现状、48=试点提案，均未批准）；循环接回相位 1 | 入库 §1、§3、§6 |",
        "| G2c 战斗动画 | 仅 MVP 可玩五形象必需：待机、移动、攻击、防御、闪避、受击、倒下、个人技能 | 规格「可玩五形象连贯」、资产清单 |",
        f"| G3 比例 | 城市显示高度 {CITY_DISPLAY_HEIGHT_LOGICAL_PX} 逻辑像素（用户已批准）；每变体唯一 `master`/`scale`/`cell_size`/`ground_pin`（数值待试点） | 入库 §3、§7 |",
        "| G4 QA | 入库 §4 自动元数据检查全过；1280×720 `canvas_items` 城市实机截图回执；人工身份／方向／alpha 复核 | 入库 §4、§8、§9 阶段 1–3 |",
        "| G5 美术验收 | 用户书面回执文件；任何哈希变化即作废 | 入库 §9 阶段 4（仅用户） |",
        "| 显示图 | 游戏内展示图（独立于精灵验收） | 注册表 `runtime_display`、资产清单 `display.*` |",
        "",
        "批量门槛：须先有一个变体四方向待机与行走达到阶段 4、且用户批准正式帧数，才可批量制作其余变体。"
        + ("下列方框仅在资产清单对应项已由用户勾选时打勾；G1–G4 本脚本不自动打勾。" if any_accepted
           else "下列所有闸门方框均未勾选，因为没有任何一项已获验收。"),
        "",
        "## 逐变体清单",
        "",
    ]
    for v in data["variants"]:
        g = v["gates"]
        num = f"伙伴 #{v['companion_number']}" if v["companion_number"] is not None else "主角"
        ex, cb, rd, qa, art = g["exploration_animation"], g["combat_animation"], g["runtime_display"], g["qa"], g["art_acceptance"]
        ff = g["four_facing"]
        placeholder = "、".join(ff["placeholder_directions"]) or "无"
        stage = v["intake_stage"] if v["intake_stage"] is not None else "未自动推导（有声明 `frame_counts` 的清单，需人工复核；不表示已越过阶段 0）"
        west = "未声明" if ff["west_authoring"] == "undeclared" else ff["west_authoring"]
        auto_qa = {"not_run_no_production_frames": "未运行（无正式帧）", "not_run": "未运行"}.get(qa["automated_metadata_checks"], qa["automated_metadata_checks"])
        receipt = f"回执 `{art['receipt']}`" if art["receipt"] else ("资产清单已由用户勾选，本脚本未核对回执文件" if art["status"] == "art_accepted" else "无回执")
        L += [
            f"### {v['ordinal']:02d}. `{v['visual_id']}` · {v['display_name_zh']}（{v['roster']} · {num} · {v['region_board']}）",
            "",
            f"- 身份／发型锚点（注册表原文）：「{v['identity_and_hair_anchor']}」" + ("" if v["anchor_has_hair"] else " — 机器人，无发型，头部外廓即锚点"),
            f"- 来源立绘：**{g['source_art']['approval']}** · {mark(g['source_art']['portrait'])}",
            f"- 就绪状态：{STATE_LABEL[v['readiness_state']]} · 入库阶段 {stage}",
            f"- 美术验收：**{art['status']}**（仅用户；资产清单 `{art['inventory_item']}` stage={art['inventory_stage']} checked={str(art['inventory_checked']).lower()}）",
            f"- [ ] G1 四方向正式帧 {len(ff['production_directions_done'])}/{len(ff['required_directions'])}（占位方向：{placeholder}；西向绘制方式：{west}）",
            f"- [ ] G2 探索动画（注册表 {ex['registry_production_status']} / {ex['registry_review_status']}；占位 待机 {ex['placeholder_idle_frames']} + 行走 {ex['placeholder_walk_frames']}；正式帧数{'已由用户批准' if ex['frame_counts_user_approved'] else '未批准'}）",
        ]
        for p in v["frame_count_manifests"]:
            L.append(f"  - 声明 `frame_counts` 的清单：`{p}`"
                     + ("（未批准试点帧，非正式生产帧）" if p in v["frame_count_manifests_unapproved"] else ""))
        if ex["placeholder_manifest"]:
            L.append(f"  - 占位清单：{mark(ex['placeholder_manifest'])}")
        for p in ex["unregistered_manifests"]:
            L.append(f"  - 注册表未引用的相关清单：`{p}`")
        sb = ex["static_idle_baseline"]
        if sb:
            f = sb["files"]
            L += [
                f"  - 用户批准的静态基准帧（{sb['decided_on']}，用户回复「{sb['user_reply_zh']}」）：{sb['facing']} {sb['pose']} 单帧 {sb['candidate']}，"
                f"{sb['display_height_logical_px']} 逻辑像素；只是静态视觉基准，本闸门仍为 {ex['status']}。决定记录：`{sb['decision_record']}`",
                f"    - 源图：`{f['png']['path']}`（{f['png']['sha256_algorithm']} `{f['png']['sha256'][:16]}…`）；"
                f"清单：`{f['manifest']['path']}`（{f['manifest']['sha256_algorithm']} `{f['manifest']['sha256'][:16]}…`）",
                f"    - 用户看过的 1280×720 实机截图：`{f['capture_city_bright']['path']}`、`{f['capture_outskirts_bright']['path']}`；同次暗场景：`{f['capture_annex_dark']['path']}`",
                f"    - QA 报告：`{f['qa_report']['path']}`；QA 说明：`{f['qa_note']['path']}`",
                "    - 不批准：探索动画、其他朝向、替换运行时精灵、runtime-sprite 验收、场景画质闸门、人工试玩。",
            ]
        if cb["mvp_required"]:
            L.append(f"- {box(cb['status'])} G2c 战斗动画（MVP 必需；注册表 {cb['registry_production_status']} / {cb['registry_review_status']}；原型 {cb['prototype_actions']} 动作 {cb['prototype_frames']} 帧；"
                     f"资产清单 `{cb['inventory_item']}` checked={str(cb['inventory_checked']).lower()}）")
            if cb["prototype_manifest"]:
                L.append(f"  - 原型清单：{mark(cb['prototype_manifest'])}")
        else:
            L.append(f"- G2c 战斗动画：资产清单 scope={cb['inventory_scope']}，不属 MVP（注册表 {cb['registry_production_status']}）")
        L += [
            f"- [ ] G3 比例 {CITY_DISPLAY_HEIGHT_LOGICAL_PX} 逻辑像素；master/scale/cell_size/ground_pin 未定",
            f"- [ ] G4 QA：自动检查{auto_qa}；实机截图回执{qa['in_engine_capture_receipt'] or '无'}；人工身份/方向复核 {qa['human_identity_direction_review']}",
            f"- {box(art['status'])} G5 用户美术验收：{art['status']}，{receipt}",
            f"- {box(rd['status'])} 显示图：注册表 {rd['registry_production_status']} / {rd['registry_review_status']}；资产清单 stage={rd['inventory_stage']} checked={str(rd['inventory_checked']).lower()}",
            "",
        ]

    hr = data["hair_review"]
    L += [
        "## 待人工复核：发型锚点可能重复或含糊",
        "",
        "以下只是 48 px 精灵尺度下的**潜在混淆提示**，不改写角色设定、发型或已批准立绘；是否需要处理由用户决定。",
        "",
        f"- 完全相同的锚点文本：{'无' if not hr['exact_duplicate_anchors'] else json.dumps(hr['exact_duplicate_anchors'], ensure_ascii=False)}。",
        "",
        "| 组 | 成员与注册表原文 | 关注点 | 决定 |",
        "|---|---|---|---|",
    ]
    for grp in hr["candidate_confusion_groups"]:
        members = "<br>".join(f"`{m['visual_id']}` {m['display_name_zh']}：「{m['anchor']}」" for m in grp["members"])
        L.append(f"| {grp['group']} | {members} | {grp['concern']} | 待人工复核 |")
    L += ["", "锚点本身含糊：", ""]
    for n in hr["anchor_notes"]:
        L.append(f"- `{n['visual_id']}`：{n['note']}")
    L += [
        f"- 机器人变体无发型（{len(hr['no_hair_robot_variants'])} 个）：" + "、".join(f"`{i}`" for i in hr["no_hair_robot_variants"]) + "；需确认以头部外廓代替发型锚点。",
        f"- 注册表锚点字段混有性格描述（{len(hr['anchors_with_persona_prose'])} 个，{persona_range}）：本清单原文引用，未自行抽取发型短语；生产前宜由人工确认 48 px 可见的发型／头部锚点。",
        "",
        "## 路径核对与注册表差异",
        "",
    ]
    pc = data["path_check"]
    L.append(f"- 缺失文件：{len(pc['missing'])} 个。" + ("" if pc["missing"] else "注册表与已登记清单引用的所有立绘、占位帧、清单和帧文件均存在。"))
    for m in pc["missing"]:
        L.append(f"  - `{m['visual_id']}` {m['role']}：`{m['path']}`")
    L.append(f"- 已引用但未纳入 git：{len(pc['untracked_but_referenced'])} 个（文件存在，仅工作区未跟踪；本任务不暂存）。")
    by_owner: dict[str, list[str]] = {}
    for u in pc["untracked_but_referenced"]:
        by_owner.setdefault(f"{u['visual_id']} {u['role']}", []).append(u["path"])
    for owner, paths in by_owner.items():
        L.append(f"  - `{owner}`：{len(paths)} 个，如 `{paths[0]}`")
    L.append(f"- 注册表未引用、按文件名发现的清单中未纳入 git：{len(pc['untracked_discovered_manifests'])} 个"
             "（不计入上一项；只检查清单文件本身，不检查其帧文件）。")
    for u in pc["untracked_discovered_manifests"]:
        L.append(f"  - `{u['visual_id']}`：`{u['path']}`")
    L.append(f"- 注册表差异：{len(pc['registry_discrepancies'])} 条（只记录，未修改注册表）。")
    for d in pc["registry_discrepancies"]:
        L.append(f"  - {d}")
    L += [
        "",
        "## 注意事项",
        "",
        "- 「有 32×48 占位帧」不等于完成任何闸门：创作者已否定该帧为正式画质基线。",
        f"- 战斗原型帧（{len(combat_mvp)} 个 MVP 可玩形象，每个 " + "/".join(map(str, combat_frames)) + f" 帧）已接入可玩战场；资产清单用户勾选验收 {s['combat_mvp_accepted']}/{len(combat_mvp)}。",
        f"- 本清单不推进任何计数；生成时资产清单 runtime-sprite 用户勾选 {s['art_accepted']}/{total}（进度文档计数以其自身为准，本脚本不改写）。",
        "",
    ]
    return "\n".join(L)


def check(data: dict) -> list[str]:
    failures = []
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    reg_ids = [e["visual_id"] for e in registry["entries"]]
    ids = [v["visual_id"] for v in data["variants"]]
    if len(ids) != EXPECTED_VARIANTS or len(set(ids)) != EXPECTED_VARIANTS:
        failures.append(f"expected {EXPECTED_VARIANTS} unique variants, got {len(ids)} ({len(set(ids))} unique)")
    if ids != reg_ids:
        failures.append("variant IDs/order differ from registry")
    if data["scope"]["character_identities"] != EXPECTED_IDENTITIES:
        failures.append(f"expected {EXPECTED_IDENTITIES} identities, got {data['scope']['character_identities']}")
    counts = registry["counts"]
    if counts["visual_variants"] != len(ids):
        failures.append(f"registry counts.visual_variants={counts['visual_variants']} but {len(ids)} entries")
    expected_sources = {"approved": counts["approved_source_portraits"], "concept": counts["concept_source_portraits"]}
    if data["summary"]["source_portraits"] != expected_sources:
        failures.append(f"source approval totals {data['summary']['source_portraits']} differ from registry counts {expected_sources}")
    s = data["summary"]
    if s["art_accepted"] + s["art_pending"] != len(ids):
        failures.append("art_accepted + art_pending does not cover every variant")
    inv = inventory_items(json.loads(INVENTORY.read_text(encoding="utf-8")))
    for v, e in zip(data["variants"], registry["entries"]):
        if v["identity_and_hair_anchor"] != e["identity_and_hair_anchor"]:
            failures.append(f"{v['visual_id']}: anchor not verbatim")
        g = v["gates"]
        for gate, item_id in (("art_acceptance", f"runtime-sprite.{v['visual_id']}"),
                              ("runtime_display", f"display.{v['visual_id']}"),
                              ("combat_animation", f"playable-combat.{v['visual_id']}")):
            if gate == "combat_animation" and not g[gate]["mvp_required"]:
                continue
            accepted = g[gate]["status"] == "art_accepted"
            if accepted != bool(inv.get(item_id, {}).get("checked")):
                failures.append(f"{v['visual_id']}: {gate} status {g[gate]['status']} disagrees with inventory {item_id}.checked")
        if v["intake_stage"] == 0 and v["frame_count_manifests"]:
            failures.append(f"{v['visual_id']}: intake stage 0 claimed despite frame_counts manifest")
        if set(v["gates"]["four_facing"]["required_directions"]) != set(registry["direction_order"]):
            failures.append(f"{v['visual_id']}: direction set differs from registry direction_order")
        sb = g["exploration_animation"]["static_idle_baseline"]
        if sb:
            if not sb["decision_record_exists"]:
                failures.append(f"{v['visual_id']}: static baseline decision record missing: {sb['decision_record']}")
            for role, record in sb["files"].items():
                if not record["exists"] or record.get("sha256_matches") is False:
                    failures.append(f"{v['visual_id']}: static baseline {role} missing or hash changed: {record['path']}"
                                    + (f" ({record['sha256_error']})" if record.get("sha256_error") else ""))
                # Binary art stays locked to its exact bytes; only text files may use the CRLF-normalized hash.
                is_png = record["path"].lower().endswith(".png")
                if "sha256" in record and record["sha256_algorithm"] != (BYTES_HASH if is_png else TEXT_HASH):
                    failures.append(f"{v['visual_id']}: static baseline {role} uses {record['sha256_algorithm']} for {'binary' if is_png else 'text'} file")
            # A static baseline must never read as a gate pass or acceptance.
            if g["exploration_animation"]["status"] != "pending" or g["four_facing"]["production_directions_done"]:
                failures.append(f"{v['visual_id']}: static baseline must leave G1/G2 pending")
    md = render_md(data)
    for v in data["variants"]:
        if f"「{v['identity_and_hair_anchor']}」" not in md:
            failures.append(f"{v['visual_id']}: anchor missing from Markdown")
    return failures


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate checklist artifacts")
    args = parser.parse_args()

    registry_hash_before = sha256(REGISTRY)
    data = build(git_tracked())
    json_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    md_text = render_md(data)
    failures = check(data)
    if sha256(REGISTRY) != registry_hash_before:
        failures.append("registry changed during run")

    if args.write and not failures:
        # Always LF, whatever the platform; Git may still check them out as CRLF.
        OUT_JSON.write_text(json_text, encoding="utf-8", newline="\n")
        OUT_MD.write_text(md_text, encoding="utf-8", newline="\n")
    elif not args.write:
        for path, text in ((OUT_JSON, json_text), (OUT_MD, md_text)):
            if not path.is_file() or text_lf_bytes(path.read_bytes()) != text.encode("utf-8"):
                failures.append(f"stale or missing artifact: {rel(path)} (run with --write)")

    s = data["summary"]
    print(f"variants={data['scope']['visual_variants']} identities={data['scope']['character_identities']} "
          f"source approved={s['source_portraits']['approved']} concept={s['source_portraits']['concept']} "
          f"art_accepted={s['art_accepted']} pending={s['art_pending']} missing_paths={s['missing_paths']} "
          f"untracked_referenced={s['untracked_referenced_paths']} untracked_discovered_manifests={s['untracked_discovered_manifests']} discrepancies={len(data['path_check']['registry_discrepancies'])}")
    if failures:
        raise SystemExit("FAIL\n" + "\n".join(failures))
    print("character sprite readiness checklist: PASS")


if __name__ == "__main__":
    main()
