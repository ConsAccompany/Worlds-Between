"""Heroine Sea-of-Stars exploration source v08: v07 authored walk arms (standalone copy, v07 untouched) with
(1) the glove hole repaired by an authored coat panel: per row, the back contour is interpolated between the coat
edge above and below the glove, interior texture is the adjacent original coat row band shifted across the hole
(navy pixels kept, brown strap pixels replaced by the row's nearest navy), new contour outlined; no flat block;
(2) side bridge b1 = all original idle0 layers exactly (authored arm layers blank) -> b1 == idle0, 0 px change;
b0 = v06 legs at half stance + the ORIGINAL idle glove pixels translated halfway from the contact hand toward idle;
(3) transition manifest schema worlds-between.exploration-stop-transition.supplemental.v1 (same as v06).
v07 notes below are historical.

v07: UNAPPROVED, test-only. Writes only outputs/hsea-arms12/src-v08-<tag>/. Imports the v06 tool (8a4c2e61) read-only;
its v04/v03 chain regenerates north/south and all idle0 unchanged; east walk legs come from v06 paint_leg unchanged.
Decoded v06 east layers: v04 "near-arm" (x51-57, y44-72) is only the coat front edge; the visible gloved arm sits in
v04 "far-arm" (x30-38, y47-66) and only shifts 0-1 px. v07 (east walk + bridges only):
- coat front edge kept static (bob only), renamed "coat-front-edge"; idle glove layer renamed "idle-arm-glove" and
  emptied in walk/bridges (the upper-body layer under it is already row-filled by v04 -> no torso hole).
- new "near-arm-sleeve" above the coat: shoulder cap, navy sleeve (shoulder->elbow), brown gauntlet (elbow->wrist),
  glove hand; two angles per frame (upper arm, forearm), forearm lags 0.6 phase, elbow always bends forward (relaxed).
  Swing is counter to the near leg (near foot forward at p0 -> arm back). Colours are actual base-palette colours.
- new "far-arm-sleeve" under the upper body (darker ramp), opposite phase; shows only where it clears the torso.
- scarf tail (follow-layer rows >= 50) sways 1 px one-and-a-half phases late; ponytail keeps v04 vertical lag; face
  is in upper-body and never moves except with bob.
- bridges per contact: b0 = v06 painted legs at 1/2 of contact stance + arm at 1/2 between contact and rest;
  b1 = exact idle0 leg/torso/coat/hair layers + authored arm at its rest pose (matches the idle glove position).
West = east mirrored (disclosed). Usage: python -I <this> [--out-tag YYYYMMDD-HHMMSS]
"""
import importlib.util, json, sys, datetime, math, zipfile, io
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V06 = "tools/rpg-2-star-ocean-the-second_heroine-sea-explore_side-guide-source-author_test-only-v06_20261020-175810-8a4c2e61.py"
_s = importlib.util.spec_from_file_location("v06", ROOT / V06); v6 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v6)
v4, v3 = v6.v4, v6.v3
W, H, SOLE, N = v3.W, v3.H, v3.SOLE, 12

SHOULDER, FAR_SHOULDER = (42, 41), (38, 42)
UPPER, FORE = 11, 9
REST = (-25.0, -15.0)                  # deg from straight down, + = toward facing; hand lands on the idle glove (~35, 60)
SLEEVE = [(19, 16, 26), (26, 35, 51), (32, 44, 68), (55, 64, 93)]        # outline, dark, mid, light (base colours)
GAUNT = [(40, 27, 30), (79, 51, 43), (119, 73, 53), (171, 108, 75)]
FAR_SLEEVE = [(10, 9, 18), (19, 16, 26), (26, 35, 51), (32, 44, 68)]
FAR_GAUNT = [(19, 16, 26), (40, 27, 30), (79, 51, 43), (119, 73, 53)]
ORDER_SIDE = ["under-trouser-paint", "far-arm-sleeve", "far-leg", "near-leg", "upper-body", "idle-arm-glove",
              "coat-front-edge", "near-arm-sleeve", "hair-scarf-follow"]


def arm_angles(p):
    """Upper-arm and forearm angle (deg) at phase p for the arm swinging counter to the near leg."""
    up = lambda q: -10.0 - 24.0 * math.cos(2 * math.pi * q / N)
    bend = 8.0 + 22.0 * (0.5 - 0.5 * math.cos(2 * math.pi * (p - 0.6) / N))
    return up(p), up(p - 0.6) + bend


def paint_arm(shoulder, a_up, a_fore, sleeve, gaunt, facing=1):
    """Two tapered capsules + shoulder cap + hand blob; per-pixel shade by side (front/top lit), 1 px outline."""
    rad = lambda d: math.radians(d)
    sx, sy = shoulder
    ex, ey = sx + UPPER * math.sin(rad(a_up)) * facing, sy + UPPER * math.cos(rad(a_up))
    wx, wy = ex + FORE * math.sin(rad(a_fore)) * facing, ey + FORE * math.cos(rad(a_fore))
    hx, hy = wx + 2.2 * math.sin(rad(a_fore)) * facing, wy + 2.2 * math.cos(rad(a_fore))
    part = np.zeros((H, W), np.int8); shade = np.zeros((H, W), np.int8)   # part: 1 sleeve, 2 gauntlet/hand

    def seg(a, b, w0, w1, pid):
        ax, ay = a; bx, by = b; vx, vy = bx - ax, by - ay; L2 = vx * vx + vy * vy or 1.0; L = math.sqrt(L2)
        for y in range(max(0, int(min(ay, by)) - 5), min(H, int(max(ay, by)) + 6)):
            for x in range(max(0, int(min(ax, bx)) - 5), min(W, int(max(ax, bx)) + 6)):
                px, py = x + 0.5, y + 0.5
                u = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
                qx, qy = ax + u * vx - px, ay + u * vy - py
                r = (w0 + (w1 - w0) * u) / 2
                if math.hypot(qx, qy) <= r:
                    across = ((px - ax) * vy - (py - ay) * vx) / L * facing   # + = behind/below the bone
                    sh = 3 if across < -r * 0.25 else (1 if across > r * 0.45 else 2)
                    if part[y, x] == 0 or pid >= part[y, x]:
                        part[y, x] = pid; shade[y, x] = sh

    def disc(c, r, pid, sh):
        for y in range(int(c[1] - r) - 1, int(c[1] + r) + 2):
            for x in range(int(c[0] - r) - 1, int(c[0] + r) + 2):
                if 0 <= y < H and 0 <= x < W and math.hypot(x + 0.5 - c[0], y + 0.5 - c[1]) <= r:
                    part[y, x] = pid; shade[y, x] = sh

    disc((sx + 0.5 * facing, sy + 1.0), 3.4, 1, 2)
    seg((sx, sy + 1), (ex, ey), 7.0, 5.6, 1)
    seg((ex, ey), (wx, wy), 5.4, 4.4, 2)
    disc((hx, hy), 2.8, 2, 3)
    out = np.zeros((H, W, 4), np.uint8)
    for (y, x) in zip(*np.nonzero(part)):
        ramp = sleeve if part[y, x] == 1 else gaunt
        edge = any(not (0 <= y + dy < H and 0 <= x + dx < W) or part[y + dy, x + dx] == 0
                   for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        out[y, x, :3] = ramp[0] if edge else ramp[shade[y, x]]; out[y, x, 3] = 255
    # cuff seam: one darker row where the sleeve meets the gauntlet
    for (y, x) in zip(*np.nonzero(part == 2)):
        if any(0 <= y + dy < H and 0 <= x + dx < W and part[y + dy, x + dx] == 1 for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[y, x, :3] = gaunt[1]
    return out, (round(ex, 2), round(ey, 2)), (round(wx, 2), round(wy, 2))


def sway(follow, dx):
    """Shift only the scarf tail (rows >= 50) horizontally; ponytail/crown rows untouched."""
    o = follow.copy()
    if dx:
        o[50:] = 0; o[50:] = np.roll(follow[50:], dx, 1)
    return o


def main():
    tag = sys.argv[sys.argv.index("--out-tag") + 1] if "--out-tag" in sys.argv else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = v3.sha(("v08" + tag).encode())[:8]
    run = ROOT / "outputs" / "hsea-arms12" / f"src-v08-{tag}"
    if sys.platform == "win32" and not str(run).startswith("\\\\?\\"): run = Path("\\\\?\\" + str(run))   # names exceed MAX_PATH
    run.mkdir(parents=True, exist_ok=True)
    raw = (ROOT / v3.SOUTH).read_bytes(); assert v3.sha(raw) == v3.SOUTH_SHA
    south = np.array(Image.open(io.BytesIO(raw)).convert("RGBA")); pal = v3.palette_of(south)
    bases = {"south": south}
    for d, p in v3.GEN.items(): bases[d], _ = v3.adapt(p, pal)
    spec_dirs = {"south": ("front", 68, 41, 14, (27, 55), 12), "north": ("front", 71, 41, 14, (29, 52), 3),
                 "east": ("side", 73, 44, 13, (29, 57), 0)}
    out = {d: list(v4.build_dir(bases[d], *s)) for d, s in spec_dirs.items()}
    ef, ew, eb, order, _ = out["east"]
    idle_L = ef[0][1]
    trouser = v6.ramp(idle_L["near-leg"], (74, 92), lambda c: c[2] > c[0])
    boot = v6.ramp(idle_L["near-leg"], (93, 104), lambda c: c[0] > c[2])
    v6.SRC["near"], v6.SRC["far"] = idle_L["near-leg"], idle_L["far-leg"]; v6.PAL = pal.astype(float)
    palset = {tuple(int(v) for v in c) for c in pal}
    for c in SLEEVE + GAUNT + FAR_SLEEVE + FAR_GAUNT: assert tuple(c) in palset, c
    blank = v3.blank()
    ren = {"near-arm": "coat-front-edge", "far-arm": "idle-arm-glove"}
    side_idle = {ren.get(k, k): v for k, v in idle_L.items()}
    side_idle["near-arm-sleeve"] = blank.copy(); side_idle["far-arm-sleeve"] = blank.copy()
    assert np.array_equal(v3.compose(side_idle, ORDER_SIDE), ef[0][0])
    anchors, arms = [], []

    def legs(L, hip, nf, nl, ff, fl):
        L["near-leg"], _, _ = v6.paint_leg(hip, nf, nl, 1, trouser, boot, False)
        L["far-leg"], _, _ = v6.paint_leg(hip, ff, fl, 1, trouser, boot, True)
        L["under-trouser-paint"] = blank.copy()

    glove = idle_L["far-arm"][..., 3] > 0

    up0 = idle_L["upper-body"]
    gy = np.nonzero(glove.any(1))[0]; gy0, gy1 = int(gy[0]), int(gy[-1])
    left = lambda row: int(np.nonzero(row[:, 3] > 0)[0][0])
    e_top, e_bot = left(up0[gy0 - 1]), left(up0[gy1 + 1])     # coat back edge just above / below the glove
    navy = lambda c: int(c[2]) >= int(c[0])
    panel = up0.copy(); panel_info = {"glove_rows": [gy0, gy1], "edge_above": e_top, "edge_below": e_bot}
    for y in range(gy0, gy1 + 1):
        xs = np.nonzero(glove[y])[0]
        if not len(xs): continue
        edge = int(round(e_top + (e_bot - e_top) * (y - gy0) / max(1, gy1 - gy0))); w = int(xs.max() - xs.min() + 1)
        navy_row = [x for x in range(xs.max() + 1, W) if up0[y, x, 3] and navy(up0[y, x]) and not glove[y, x]]
        for x in xs:
            if x < edge: panel[y, x] = 0; continue
            sx = x + w
            if 0 <= sx < W and up0[y, sx, 3] and navy(up0[y, sx]) and not glove[y, sx]: panel[y, x] = up0[y, sx]
            elif navy_row: panel[y, x] = up0[y, min(navy_row, key=lambda q: abs(q - sx))]
            else: panel[y, x, :3] = SLEEVE[1]; panel[y, x, 3] = 255
            if x == edge: panel[y, x, :3] = SLEEVE[0]

    def put_arms(L, near_ang, far_ang, b):
        L["idle-arm-glove"] = blank.copy()
        L["upper-body"] = np.roll(panel, b, 0)
        na, ne, nw = paint_arm((SHOULDER[0], SHOULDER[1] + b), *near_ang, SLEEVE, GAUNT)
        fa, fe, fw = paint_arm((FAR_SHOULDER[0], FAR_SHOULDER[1] + b), *far_ang, FAR_SLEEVE, FAR_GAUNT)
        L["near-arm-sleeve"], L["far-arm-sleeve"] = na, fa
        return {"near_elbow": ne, "near_wrist": nw, "far_elbow": fe, "far_wrist": fw}

    walk = []
    for p in range(N):
        b = v4.BOB[p]; src = ew[p][1]
        L = {"upper-body": src["upper-body"].copy(), "coat-front-edge": np.roll(idle_L["near-arm"], b, 0),
             "hair-scarf-follow": sway(src["hair-scarf-follow"], -int(round(math.sin(2 * math.pi * (p - 1.5) / N))))}
        nf, nl = v6.foot_x(p); ff, fl = v6.foot_x(p + 6)
        legs(L, (v6.HIP[0], v6.HIP[1] + b), nf, nl, ff, fl)
        na = arm_angles(p); fa = arm_angles(p + 6)
        g = put_arms(L, na, fa, b)
        for k in L: L[k][SOLE + 1:] = 0
        walk.append((v3.compose(L, ORDER_SIDE), L))
        anchors.append({"phase": p, "near_painted": v6.sole_anchor(L["near-leg"]), "far_painted": v6.sole_anchor(L["far-leg"])})
        arms.append({"phase": p, "near_deg": [round(v, 2) for v in na], "far_deg": [round(v, 2) for v in fa], **g})
    bridges, bridge_info = {}, {}
    def hand_x(layer):
        a = layer[..., 3] > 0; yb = int(np.nonzero(a.any(1))[0][-1]); return float(np.nonzero(a[yb - 2:yb + 1].any(0))[0].mean())
    idle_hand = hand_x(idle_L["far-arm"])
    for c in (0, 6):
        nf0, _ = v6.foot_x(c); ff0, _ = v6.foot_x(c + 6)
        dx = int(round((hand_x(walk[c][1]["near-arm-sleeve"]) - idle_hand) / 2))
        # b0: half stance legs + original glove pixels moved halfway; b1: every original idle0 layer exactly
        L0 = {kk: v.copy() for kk, v in side_idle.items()}
        legs(L0, v6.HIP, 52 + (nf0 - 52) * 0.5, 0, 36 + (ff0 - 36) * 0.5, 0)
        L0["upper-body"] = panel.copy(); L0["idle-arm-glove"] = np.roll(idle_L["far-arm"], dx, 1)
        L1 = {kk: v.copy() for kk, v in side_idle.items()}
        fr = []
        for L in (L0, L1):
            for kk in L: L[kk][SOLE + 1:] = 0
            fr.append((v3.compose(L, ORDER_SIDE), L))
        assert np.array_equal(fr[1][0], ef[0][0])
        bridges[c] = fr
        bridge_info[f"contact{c}"] = [{"bridge": 0, "legs": "v06 painted, stance k=0.5", "arm": "original idle glove pixels shifted x",
                                       "glove_dx": dx, "contact_hand_x": round(hand_x(walk[c][1]["near-arm-sleeve"]), 1), "idle_hand_x": round(idle_hand, 1)},
                                      {"bridge": 1, "legs": "exact idle0", "arm": "exact idle0 glove", "equals_idle0": True}]
    out["east"] = [[(ef[0][0], side_idle)], walk, bridges, ORDER_SIDE, None]
    mir = lambda L: {k: v[:, ::-1].copy() for k, v in L.items()}
    mf = lambda fr: [(a[:, ::-1].copy(), mir(L)) for a, L in fr]
    e = out["east"]
    out["west"] = [mf(e[0]), mf(e[1]), {c: mf(v) for c, v in e[2].items()}, ORDER_SIDE, None]
    spec = importlib.util.spec_from_file_location("pxo_writer", ROOT / v3.WRITER)
    wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
    wr.W, wr.H = W, H; wr.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    pre = "rpg-2-star-ocean-the-second_heroine-sea"
    actions = {"idle": {}, "walk": {}}; src = []; trans = {}; layer_names = {}
    for d in ("south", "west", "north", "east"):
        idle, wk, br, order, _ = out[d]; allf = []; layer_names[d] = list(order)
        for act, fr in (("idle", idle), ("walk", wk)):
            actions[act][d] = []
            for i, (arr, L) in enumerate(fr):
                b = raw if (d == "south" and act == "idle") else v3.png(arr)
                fn = f"{pre}_explore-{d}-{act}-f{i:02d}_unapproved-v08_{tag}-{uid}.png"
                (run / fn).write_bytes(b)
                actions[act][d].append({"file": fn, "duration_ms": v4.IDLE_MS if act == "idle" else v4.FRAME_MS})
                allf.append((L, (v4.IDLE_MS if act == "idle" else v4.FRAME_MS) / 1000))
        trans[d] = {}
        for c, fr in br.items():
            lst = []
            for k, (arr, L) in enumerate(fr):
                fn = f"{pre}_explore-{d}-stop-c{c:02d}-b{k}_unapproved-v08_{tag}-{uid}.png"
                (run / fn).write_bytes(v3.png(arr)); lst.append({"file": fn, "sha256": v3.sha((run / fn).read_bytes())})
                allf.append((L, v4.FRAME_MS / 1000))
            trans[d][f"contact{c}"] = {"from_walk_frame": c, "bridge": lst, "final": actions["idle"][d][0]["file"]}
        per = [{k: L[k] for k in order} for L, _ in allf]
        pxo = f"{pre}_explore-{d}-layers_unapproved-v08_{tag}-{uid}.pxo"
        (run / pxo).write_bytes(wr.make_pxo(per, [t for _, t in allf], v3.png(v3.compose(per[0], order)), pxo[:-4] + ".png", 16, order=order, dt=v3.DT))
        ora = f"{pre}_explore-{d}-idle0-layers_unapproved-v08_{tag}-{uid}.ora"
        with zipfile.ZipFile(run / ora, "w") as z:
            z.writestr(zipfile.ZipInfo("mimetype", v3.DT), "image/openraster")
            z.writestr(zipfile.ZipInfo("mergedimage.png", v3.DT), v3.png(v3.compose(per[0], order)))
            root = ET.Element("image", {"w": str(W), "h": str(H)}); st = ET.SubElement(root, "stack")
            for i, k in enumerate(order[::-1]):
                z.writestr(zipfile.ZipInfo(f"data/l{i}.png", v3.DT), v3.png(per[0][k]))
                ET.SubElement(st, "layer", {"name": k, "src": f"data/l{i}.png", "x": "0", "y": "0"})
            z.writestr(zipfile.ZipInfo("stack.xml", v3.DT), ET.tostring(root, encoding="utf8"))
        src += [{"direction": d, "file": pxo, "format": "pixelorama-pxo", "sha256": v3.sha((run / pxo).read_bytes()),
                 "frame_order": "idle f00, walk f00-f11, stop c00 b0-b1, stop c06 b0-b1", "layers_bottom_to_top": list(order)},
                {"direction": d, "file": ora, "format": "openraster-supplemental-idle0", "sha256": v3.sha((run / ora).read_bytes())}]
    tool = {"file": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
            "sha256TextLf": v3.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))}
    man = {"schema": "worlds-between.exploration-source.v1", "actor_id": "protagonist-female", "density": 2,
           "frame_size": [W, H], "pivot": [40, 104], "actions": actions, "source_files": src,
           "status": "UNAPPROVED test-only candidate; authored side arms over v06 legs, coat panel, exact-idle b1; no runtime/default change",
           "author_tool": tool, "reused_v06_module": {"file": V06, "sha256TextLf": v3.sha((ROOT / V06).read_bytes().replace(b"\r\n", b"\n"))},
           "side_arms": {"shoulder": SHOULDER, "far_shoulder": FAR_SHOULDER, "upper_px": UPPER, "fore_px": FORE, "rest_deg": REST,
                         "sleeve_ramp": SLEEVE, "gauntlet_ramp": GAUNT, "far_sleeve_ramp": FAR_SLEEVE, "far_gauntlet_ramp": FAR_GAUNT,
                         "per_phase": arms, "coat_panel": panel_info},
           "disclosure": ["west = east mirrored; asymmetric straps/scarf tail and the arm side flip",
                          "north/south and all idle0 are regenerated v04 output unchanged; front arms still fixed to torso",
                          "east/west walk legs are v06 paint_leg output with the same targets (protected)",
                          "authored arm is a 2-angle drawn limb (not the generated base's arm pixels); idle0 keeps the original glove",
                          "walk -> b0 swaps the authored arm for the original glove (moved halfway); b1 == idle0 exactly", "glove hole repaired by row-band coat panel, not original art"]}
    mp = run / f"{pre}_explore-source-manifest_unapproved-v08_{tag}-{uid}.json"
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8", newline="\n")
    tp = run / f"{pre}_explore-stop-transition-manifest_unapproved-v08_{tag}-{uid}.json"
    tp.write_text(json.dumps({"schema": "worlds-between.exploration-stop-transition.supplemental.v1",
                              "source_manifest": mp.name,
                              "rule": "on release: continue to next contact (0 or 6) within <=120 ms, play its 2 bridge frames, then exact idle0",
                              "directions": trans, "side_bridge_poses": bridge_info,
                              "east_sole_anchors_source_px": anchors, "author_tool": tool}, indent=1), encoding="utf-8", newline="\n")
    print(mp)


if __name__ == "__main__":
    main()
