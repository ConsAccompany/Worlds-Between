"""Source-locked segmented south walk bake (female protagonist, M8 E1-E9 feasibility experiment).

Technical feasibility experiment only. Nothing here is art, approved, or used by the game runtime.
Input master is the LANCZOS quantized 80x112 south idle, treated as a PROVISIONAL technical input
(the user has not chosen BOX vs LANCZOS vs neither); if they choose otherwise this may be discarded.

Method (decision memo section 3, method C / section 4 experiment):
  * Layers are cut from the master by the declared mask rules in the pose table (first match wins).
  * Every frame texel is a copy of a master texel placed by a declared integer transform:
      rigid offset (body bob, arm swing), per-row x offset (scarf tip sway, swing-foot tuck),
      and duplicated or dropped shin rows (foot raise / reach). No rotation, resampling or AI pixels.
  * The only non-copied-position texels are the declared occlusion fill behind the swinging arm.
    They are counted per frame. Hand edits: none are made by this script (log is empty).

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script> --pose-table <json> --out-dir <experiment folder> --determinism-dir <tmp>
"""

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "rpg-2-star-ocean-the-second"
CHARACTER = "protagonist-female"
STAMP = "20261014-215052"
ITERATION = 1
VARIANT = f"m8-it{ITERATION}"
# Keeps every absolute output path <= 259 chars (Windows MAX_PATH; Git for Windows without core.longpaths).
MAX_ABS_PATH = 259

PARTS = ["hair_ponytail", "face_head", "torso_coat", "bag", "scarf_tail", "leg_vl", "leg_vr", "arm_vl", "arm_vr"]
PART_FILE_TAG = {
    "hair_ponytail": "hair-ponytail",
    "face_head": "face-head",
    "torso_coat": "torso-coat",
    "bag": "bag-bedroll",
    "scarf_tail": "scarf-tail",
    "leg_vl": "leg-vl-kneeguard",
    "leg_vr": "leg-vr",
    "arm_vl": "arm-vl",
    "arm_vr": "arm-vr",
    "occlusion_fill": "occlusion-fill",
}
KEY_NAMES = ["knee_guard", "scarf_tail", "ponytail"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def short_id(purpose: str) -> str:
    return hashlib.sha1(f"{STAMP}|{VARIANT}|{purpose}".encode()).hexdigest()[:8]


def out_name(purpose: str, ext: str = "png") -> str:
    return f"{PROJECT}_{CHARACTER}_{purpose}_{VARIANT}_{STAMP}-{short_id(purpose)}.{ext}"


def png_bytes(arr: np.ndarray) -> bytes:
    import io

    buffer = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def in_rect(x: int, y: int, rect) -> bool:
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def is_teal(c) -> bool:
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    return g >= r + 10 and b >= r + 10


def is_skin(c) -> bool:
    r, b = int(c[0]), int(c[2])
    return r >= 150 and r - b >= 60


# ---------------------------------------------------------------- masks

def classify(master: np.ndarray, table: dict) -> np.ndarray:
    """Owner part index per texel (-1 = transparent), by the pose table's ordered rules."""
    h, w = master.shape[:2]
    owner = np.full((h, w), -1, dtype=np.int16)
    opaque = master[:, :, 3] == 255
    for rule in table["layer_masks"]["rules"]:
        part = PARTS.index(rule["part"])
        rect = rule["rect"]
        cls = rule["colour_class"]
        if cls == "skin_row_enclosed":
            for y in range(rect[1], rect[3] + 1):
                xs = [x for x in range(rect[0], rect[2] + 1)
                      if opaque[y, x] and owner[y, x] < 0 and is_skin(master[y, x])]
                if not xs:
                    continue
                for x in range(min(xs), max(xs) + 1):
                    if opaque[y, x] and owner[y, x] < 0:
                        owner[y, x] = part
            continue
        for y in range(rect[1], rect[3] + 1):
            for x in range(rect[0], rect[2] + 1):
                if not opaque[y, x] or owner[y, x] >= 0:
                    continue
                c = master[y, x]
                if cls is None or (cls == "teal" and is_teal(c)) or (cls == "not_teal" and not is_teal(c)):
                    owner[y, x] = part
    if np.any(opaque & (owner < 0)):
        raise SystemExit("mask rules left an opaque texel without an owner")
    return owner


def ownership_keys(owner: np.ndarray, table: dict) -> dict:
    keys = {}
    for name in KEY_NAMES:
        spec = table["ownership_keys"][name]
        part = PARTS.index(spec["owner_part"])
        mask = np.zeros(owner.shape, dtype=bool)
        r = spec["rect"]
        mask[r[1]:r[3] + 1, r[0]:r[2] + 1] = True
        keys[name] = mask & (owner == part)
    return keys


def fill_sources(owner: np.ndarray) -> dict:
    """arm_vr footprint texel -> nearest torso_coat texel to its left in the same row."""
    arm = PARTS.index("arm_vr")
    torso = PARTS.index("torso_coat")
    sources = {}
    for y, x in zip(*np.nonzero(owner == arm)):
        for xl in range(x - 1, -1, -1):
            if owner[y, xl] == torso:
                sources[(int(y), int(x))] = (int(y), int(xl))
                break
    return sources


# ---------------------------------------------------------------- transforms

def evenly(n: int, m: int) -> list:
    picks = sorted({int((i + 0.5) * m / n) for i in range(n)})
    if len(picks) != n:
        raise SystemExit(f"cannot pick {n} distinct rows from a band of {m}")
    return picks


def leg_row_map(table: dict, leg: str, foot_row: int, bob: int):
    spec = table["legs"][leg]
    top, idle_foot = spec["top_row"], spec["idle_foot_row"]
    b0, b1 = spec["shin_band"]
    delta = foot_row - idle_foot - bob
    band = list(range(b0, b1 + 1))
    if delta < 0:
        drop = set(evenly(-delta, len(band)))
        band_out = [r for i, r in enumerate(band) if i not in drop]
    elif delta > 0:
        dup = set(evenly(delta, len(band)))
        band_out = []
        for i, r in enumerate(band):
            band_out.append(r)
            if i in dup:
                band_out.append(r)
    else:
        band_out = band
    rows = list(range(top, b0)) + band_out + list(range(b1 + 1, idle_foot + 1))
    return delta, rows


def placements(phase: dict, table: dict, owner: np.ndarray, fills: dict):
    """Ordered (z back-to-front) list of (part, dst_y, dst_x, src_y, src_x, kind)."""
    bob = phase["bob"]
    mid = {leg: (table["legs"][leg]["shin_band"][0] + table["legs"][leg]["shin_band"][1]) // 2
           for leg in ("leg_vl", "leg_vr")}
    sway_from = table["scarf_tail_sway"]["rows_from"]
    out = []
    for part in table["z_order_back_to_front"]:
        if part == "occlusion_fill":
            for (sy, sx), (fy, fx) in sorted(fills.items()):
                out.append((part, sy + bob, sx, fy, fx, "fill"))
            continue
        pid = PARTS.index(part)
        if part in ("leg_vl", "leg_vr"):
            _, rows = leg_row_map(table, part, phase[part]["foot_row"], bob)
            top = table["legs"][part]["top_row"]
            swing = phase[part]["swing_x"]
            for k, sy in enumerate(rows):
                dx = swing if sy >= mid[part] else 0
                for sx in np.nonzero(owner[sy] == pid)[0]:
                    out.append((part, top + k + bob, int(sx) + dx, sy, int(sx), "copy"))
            continue
        for sy, sx in zip(*np.nonzero(owner == pid)):
            sy, sx = int(sy), int(sx)
            dx, dy = 0, bob
            if part == "scarf_tail" and sy >= sway_from:
                dx = phase["scarf_sway_x"]
            if part == "arm_vr":
                dy = bob + phase["arm_vr_dy"]
            out.append((part, sy + dy, sx + dx, sy, sx, "copy"))
    return out


def compose(master: np.ndarray, places: list):
    h, w = master.shape[:2]
    frame = np.zeros_like(master)
    prov_part = np.full((h, w), "", dtype=object)
    prov_src = np.full((h, w, 2), -1, dtype=np.int32)
    prov_kind = np.full((h, w), "", dtype=object)
    for part, dy, dx, sy, sx, kind in places:
        if not (0 <= dy < h and 0 <= dx < w):
            raise SystemExit(f"{part} texel placed outside the cell at ({dx},{dy})")
        frame[dy, dx] = master[sy, sx]
        prov_part[dy, dx] = part
        prov_src[dy, dx] = (sy, sx)
        prov_kind[dy, dx] = kind
    return frame, prov_part, prov_src, prov_kind


# ---------------------------------------------------------------- measurements

def alpha_bounds(arr: np.ndarray):
    ys, xs = np.nonzero(arr[:, :, 3] > 0)
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def opaque_rgb_set(arr: np.ndarray) -> set:
    a = arr[arr[:, :, 3] == 255][:, :3]
    return {tuple(int(v) for v in c) for c in a}


def foot_point(prov_part, leg: str):
    ys, xs = np.nonzero(prov_part == leg)
    low = int(ys.max())
    row_xs = xs[ys == low]
    return [int((int(row_xs.min()) + int(row_xs.max()) + 1) // 2), low]


def measure_frame(frame, master, owner, keys, phase, table, places):
    """E1-E6 for one frame, re-derived from the PNG bytes on disk and the declared transforms."""
    cell_w, cell_h = table["cell"]
    pin_x = table["ground_pin"][0]
    # Visible provenance by declared z-order (later placement wins).
    _, prov_part, prov_src, prov_kind = compose(master, places)
    opaque = frame[:, :, 3] == 255
    copy_ok = copy_bad = fill_vis = unexplained = 0
    per_part = {}
    for y, x in zip(*np.nonzero(opaque)):
        kind = prov_kind[y, x]
        if kind == "":
            unexplained += 1
            continue
        sy, sx = prov_src[y, x]
        if kind == "fill":
            fill_vis += 1
            continue
        part = prov_part[y, x]
        stats = per_part.setdefault(part, [0, 0])
        stats[0] += 1
        if np.array_equal(frame[y, x], master[sy, sx]):
            stats[1] += 1
            copy_ok += 1
        else:
            copy_bad += 1
    # Transparent texels that the declared placements say should be opaque.
    missing = int(np.sum((prov_kind != "") & ~opaque))

    # E2 ownership: visible keyed texels via provenance.
    e2 = {}
    face_ys, face_xs = np.nonzero(prov_part == "face_head")
    face_cx = float(face_xs.mean())
    for name in KEY_NAMES:
        pts = [(x, y) for y, x in zip(*np.nonzero(prov_kind == "copy"))
               if keys[name][prov_src[y, x][0], prov_src[y, x][1]]]
        owner_part = table["ownership_keys"][name]["owner_part"]
        owners = {prov_part[y, x] for x, y in pts}
        cx = float(np.mean([p[0] for p in pts])) if pts else None
        limit = face_cx if name == "ponytail" else pin_x
        e2[name] = {
            "visible_texels": len(pts),
            "idle_texels": int(keys[name].sum()),
            "centroid": [round(cx, 3), round(float(np.mean([p[1] for p in pts])), 3)] if pts else None,
            "side_limit_x": round(limit, 3),
            "owner_parts_seen": sorted(owners),
            "pass": bool(pts) and cx < limit and owners == {owner_part},
        }

    # E3 registration: exact-match search of the torso layer.
    torso = PARTS.index("torso_coat")
    tys, txs = np.nonzero(owner == torso)
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            ty, tx = tys + dy, txs + dx
            ok = (ty >= 0) & (ty < cell_h) & (tx >= 0) & (tx < cell_w)
            match = np.all(frame[ty[ok], tx[ok]] == master[tys[ok], txs[ok]], axis=1).sum()
            if best is None or match > best[0]:
                best = (int(match), dx, dy)
    bounds = alpha_bounds(frame)
    border = int(opaque[0, :].sum() + opaque[-1, :].sum() + opaque[:, 0].sum() + opaque[:, -1].sum())
    alpha_vals = sorted(int(v) for v in np.unique(frame[:, :, 3]))
    colours = opaque_rgb_set(frame)
    return {
        "e1": {
            "visible_copied_texels": copy_ok + copy_bad,
            "equal_to_master_after_declared_transform": copy_ok,
            "not_equal": copy_bad,
            "per_part_visible_and_equal": {k: v for k, v in sorted(per_part.items())},
            "unexplained_opaque_texels": unexplained,
            "declared_but_transparent_texels": missing,
            "pass": copy_bad == 0 and unexplained == 0 and missing == 0,
        },
        "e2": e2,
        "e3": {
            "torso_layer_texels": int(len(tys)),
            "best_exact_match": {"matches": best[0], "dx": best[1], "dy": best[2]},
            "declared_bob": phase["bob"],
            "pin_x_drift": best[1],
            "pass": best[1] == 0 and best[2] == phase["bob"],
        },
        "e4": {"alpha_bounds_inclusive_xyxy": bounds, "visible_height": bounds[3] - bounds[1] + 1},
        "e5": {
            "alpha_values_present": alpha_vals,
            "partial_alpha_texels": int(np.sum((frame[:, :, 3] > 0) & (frame[:, :, 3] < 255))),
            "opaque_texels_on_cell_border": border,
            "unique_opaque_rgb_colours": len(colours),
            "colours_not_in_idle_palette": len(colours - opaque_rgb_set(master)),
        },
        "e6": {"hand_edited_texels": 0, "visible_occlusion_fill_texels": fill_vis},
        "contact_points": {leg: foot_point(prov_part, leg) for leg in ("leg_vl", "leg_vr")},
    }


def e8_analytic(table: dict, frames: dict) -> dict:
    """Stance-foot world drift per 60 Hz tick under distance-driven stepping (straight south path)."""
    motion = table["pilot_motion"]
    per_tick = motion["speed_logical_px_per_s"] / motion["physics_hz"]
    spp = motion["screen_px_per_logical_px"]
    pin_y = table["ground_pin"][1]
    ticks = int(round(2 * motion["cycle_length_logical_px"] / per_tick))
    log, drifts = [], []
    prev = None
    for k in range(ticks + 1):
        dist = k * per_tick
        phase_no = int(dist // motion["phase_advance_logical_px"]) % 8 + 1
        phase = frames[phase_no]
        leg = phase["stance"]
        fx, fy = phase["contact_points"][leg]
        world = (fx - table["ground_pin"][0], dist * spp + (fy - pin_y))
        if prev is not None and prev[0] == leg:
            d = (world[0] - prev[1][0], world[1] - prev[1][1])
            drifts.append(max(abs(d[0]), abs(d[1])))
            log.append({"tick": k, "phase": phase_no, "stance": leg, "drift_screen_px": [d[0], d[1]]})
        prev = (leg, world)
    stance_rise = {}
    for leg in ("leg_vl", "leg_vr"):
        rows = [frames[p]["contact_points"][leg][1] for p in range(1, 9) if frames[p]["stance"] == leg]
        stance_rise[leg] = {"stance_foot_rows": rows, "in_cell_rise_texels": rows[0] - rows[-1]}
    travel = motion["phase_advance_logical_px"] * 3 * spp
    return {
        "speed_logical_px_per_s": motion["speed_logical_px_per_s"],
        "body_travel_screen_px_per_tick": per_tick * spp,
        "ticks_simulated": ticks,
        "max_stance_foot_drift_screen_px_per_tick": max(drifts),
        "mean_stance_foot_drift_screen_px_per_tick": round(float(np.mean(drifts)), 4),
        "ticks_over_1px": int(sum(1 for d in drifts if d > 1)),
        "ticks_compared": len(drifts),
        "stance_body_travel_first_to_last_stance_frame_screen_px": travel,
        "stance_foot": stance_rise,
        "limit": "<= 1 screen px per tick (M5)",
        "pass": max(drifts) <= 1,
        "per_tick_log_first_cycle": log[: int(round(motion["cycle_length_logical_px"] / per_tick))],
    }


# ---------------------------------------------------------------- bake

def bake(table: dict, master: np.ndarray, out_dir: Path, table_path: Path) -> dict:
    owner = classify(master, table)
    keys = ownership_keys(owner, table)
    fills = fill_sources(owner)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}

    def write(purpose: str, arr: np.ndarray) -> dict:
        name = out_name(purpose)
        data = png_bytes(arr)
        path = out_dir / name
        if len(str(path.resolve())) > MAX_ABS_PATH:
            raise SystemExit(f"absolute path longer than {MAX_ABS_PATH} chars: {name}")
        if path.exists() and path.read_bytes() != data:
            raise SystemExit(f"refusing to change existing bytes of {name}")
        path.write_bytes(data)
        written[name] = sha256(data)
        return {"file": name, "bytes": len(data), "sha256": sha256(data)}

    layers = {}
    for part in PARTS:
        arr = np.zeros_like(master)
        sel = owner == PARTS.index(part)
        arr[sel] = master[sel]
        info = write(f"south-layer-{PART_FILE_TAG[part]}", arr)
        info["opaque_texels"] = int(sel.sum())
        layers[part] = info
    fill_arr = np.zeros_like(master)
    for (sy, sx), (fy, fx) in fills.items():
        fill_arr[sy, sx] = master[fy, fx]
    layers["occlusion_fill"] = write("south-layer-occlusion-fill", fill_arr)
    layers["occlusion_fill"]["synthesized_texels"] = len(fills)
    layers["occlusion_fill"]["sources"] = [{"dst": [x, y], "colour_from": [fx, fy]}
                                           for (y, x), (fy, fx) in sorted(fills.items())]

    key_arr = np.zeros_like(master)
    for name in KEY_NAMES:
        key_arr[keys[name]] = table["ownership_keys"][name]["key_rgba"]
    ownership = write("south-ownership-mask", key_arr)
    ownership["keys"] = {n: {"texels": int(keys[n].sum()), "key_rgba": table["ownership_keys"][n]["key_rgba"]}
                         for n in KEY_NAMES}

    phases = [table["idle_phase"]] + table["phases"]
    frames = {}
    for phase in phases:
        places = placements(phase, table, owner, fills)
        arr, _, _, _ = compose(master, places)
        purpose = f"south-frame-{phase['phase']:02d}-{phase['name']}"
        info = write(purpose, arr)
        reloaded = np.array(Image.open(out_dir / info["file"]).convert("RGBA"))
        m = measure_frame(reloaded, master, owner, keys, phase, table, places)
        legs = {}
        for leg in ("leg_vl", "leg_vr"):
            delta, rows = leg_row_map(table, leg, phase[leg]["foot_row"], phase["bob"])
            band = table["legs"][leg]["shin_band"]
            base = list(range(band[0], band[1] + 1))
            legs[leg] = {
                "declared_foot_row": phase[leg]["foot_row"],
                "measured_foot_row": m["contact_points"][leg][1],
                "shin_delta_rows": delta,
                "dropped_source_rows": [r for r in base if r not in rows],
                "duplicated_source_rows": sorted({r for r in rows if rows.count(r) > 1}),
                "swing_x": phase[leg]["swing_x"],
            }
            if legs[leg]["declared_foot_row"] != legs[leg]["measured_foot_row"]:
                raise SystemExit(f"phase {phase['phase']} {leg}: foot row mismatch")
        frames[phase["phase"]] = {
            "phase": phase["phase"], "name": phase["name"], "stance": phase["stance"],
            "png": info,
            "transforms": {
                "bob_y": phase["bob"],
                "rigid_parts_offset": {p: [0, phase["bob"]] for p in
                                       ("hair_ponytail", "face_head", "torso_coat", "bag", "arm_vl")},
                "arm_vr_offset": [0, phase["bob"] + phase["arm_vr_dy"]],
                "scarf_tail": {"rows_lt_73_offset": [0, phase["bob"]],
                               "rows_ge_73_offset": [phase["scarf_sway_x"], phase["bob"]]},
                "occlusion_fill_offset": [0, phase["bob"]],
                "legs": legs,
            },
            "contact_points": m["contact_points"],
            "hand_edits": [],
            "metrics": {k: m[k] for k in ("e1", "e2", "e3", "e4", "e5", "e6")},
        }

    manifest = {
        "schema": "segmented-walk-bake-manifest/1",
        "project": PROJECT, "character": CHARACTER, "direction": "south", "variant": VARIANT,
        "status": "technical feasibility experiment; unapproved; not runtime-integrated; not art",
        "master": table["master"],
        "pose_table": {"file": table_path.name, "sha256": sha256(table_path.read_bytes())},
        "generator": {"script": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                      "script_sha256": sha256(Path(__file__).read_bytes()),
                      "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__},
        "declared_once": {"cell": table["cell"], "ground_pin": table["ground_pin"],
                          "sprite2d_scale": table["sprite2d_scale"], "filter": "nearest"},
        "z_order_back_to_front": table["z_order_back_to_front"],
        "layers": layers,
        "ownership_mask": ownership,
        "frames": [frames[p["phase"]] for p in phases],
        "pixel_edit_log": {"hand_edited_texels_total": 0, "entries": []},
        "ai_pixels": 0,
    }
    name = out_name("south-bake-manifest", "json")
    data = (json.dumps(manifest, indent=2) + "\n").encode()
    (out_dir / name).write_bytes(data)
    written[name] = sha256(data)
    return {"manifest": manifest, "frames": frames, "written": written, "master": master}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose-table", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--determinism-dir", type=Path, required=True)
    args = parser.parse_args()

    table = json.loads(args.pose_table.read_text(encoding="utf-8"))
    master_path = ROOT / table["master"]["path"]
    master_bytes = master_path.read_bytes()
    if sha256(master_bytes) != table["master"]["sha256"]:
        raise SystemExit("master SHA-256 mismatch")
    master = np.array(Image.open(master_path).convert("RGBA"))
    if master.shape[:2] != (table["cell"][1], table["cell"][0]):
        raise SystemExit("master is not the declared cell size")

    first = bake(table, master, args.out_dir, args.pose_table)
    second = bake(table, master, args.determinism_dir, args.pose_table)
    e7_files = sorted(first["written"])
    e7 = {
        "files_compared": len(e7_files),
        "identical": sum(1 for n in e7_files if first["written"][n] == second["written"].get(n)),
        "second_run_dir": "outside repo (scratch)",
    }
    e7["pass"] = e7["identical"] == e7["files_compared"] == len(second["written"])

    frames = first["frames"]
    idle = frames[0]["metrics"]
    idle_h = idle["e4"]["visible_height"]
    walk = [frames[p] for p in range(1, 9)]
    for f in walk:
        dh = f["metrics"]["e4"]["visible_height"] - idle_h
        f["metrics"]["e4"]["delta_vs_idle"] = dh
        f["metrics"]["e4"]["pass"] = -3 <= dh <= 1
    master_metrics = {
        "e1_idle_master_equals_deterministic_downsample":
            "re-run of the master author script into scratch reproduced SHA-256 738c08c1...a643be (checked before this bake)",
        "idle_frame_equals_master": bool(np.array_equal(
            np.array(Image.open(args.out_dir / frames[0]["png"]["file"]).convert("RGBA")), master)),
    }
    e5_all = all(f["metrics"]["e5"]["partial_alpha_texels"] == 0 and f["metrics"]["e5"]["opaque_texels_on_cell_border"] == 0
                 and f["metrics"]["e5"]["unique_opaque_rgb_colours"] <= 48 and f["metrics"]["e5"]["colours_not_in_idle_palette"] == 0
                 for f in [frames[0]] + walk)
    summary = {
        "E1_source_lock": all(f["metrics"]["e1"]["pass"] for f in [frames[0]] + walk) and master_metrics["idle_frame_equals_master"],
        "E2_ownership_frames_passing": sum(1 for f in [frames[0]] + walk if all(v["pass"] for v in f["metrics"]["e2"].values())),
        "E3_registration": all(f["metrics"]["e3"]["pass"] for f in [frames[0]] + walk),
        "E4_height": idle_h in (95, 96, 97) and all(f["metrics"]["e4"]["pass"] for f in walk),
        "E5_alpha_palette": e5_all,
        "E6_max_hand_edits_per_frame": 0,
        "E6_visible_fill_texels_per_frame": [f["metrics"]["e6"]["visible_occlusion_fill_texels"] for f in walk],
        "E7_determinism": e7["pass"],
    }
    metrics = {
        "schema": "segmented-walk-metrics/1",
        "variant": VARIANT,
        "status": "numbers only; a numerical pass is not an art or motion pass (E10 is the user's call)",
        "bake_manifest": out_name("south-bake-manifest", "json"),
        "master_checks": master_metrics,
        "e7_determinism": e7,
        "e8_analytic_cross_check": None,
        "summary": summary,
        "per_frame": [{"phase": f["phase"], "name": f["name"], "png": f["png"]["file"], "sha256": f["png"]["sha256"],
                       "metrics": f["metrics"], "contact_points": f["contact_points"]} for f in [frames[0]] + walk],
    }
    table_frames = {p: {"stance": frames[p]["stance"], "contact_points": frames[p]["contact_points"]} for p in range(1, 9)}
    metrics["e8_analytic_cross_check"] = e8_analytic(table, table_frames)
    name = out_name("south-metrics", "json")
    (args.out_dir / name).write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "e7": e7,
                      "e8_max_drift": metrics["e8_analytic_cross_check"]["max_stance_foot_drift_screen_px_per_tick"],
                      "metrics": name}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
