"""Three native-pixel antenna fixtures for Yonkers outskirts room 1 (antenna walkway).

Same palette, outline and contact-shadow language as the accepted Yonkers maintenance room 2
fixtures. Each fixture explains one clue: A strong but jittery, B weaker but steady with an
intact grounded cable, C a new head on a weathered mast with a cold, frosted backup battery.
Writes per fixture a merged PNG, a four-layer OpenRaster and a four-layer Pixelorama .pxo.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import io
import json
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "tools/rpg-2-star-ocean-the-second_nyc-room2-pixel-fixtures-author_v01_20261017-010000-7d3c8a91.py"
spec = spec_from_file_location("room_fixture_layers", source)
art = module_from_spec(spec)
spec.loader.exec_module(art)
art.OUT = ROOT / "outputs/yonkers-room1-antenna-pilot"
art.OUT.mkdir(parents=True, exist_ok=True)
RUNTIME = ROOT / "game/assets/props/yonkers-antenna-room1"
art.PREFIX = "rpg-2-star-ocean-the-second_yonkers-antenna-room1"
art.STAMP = "20261017-024000-9b3e6f21"
# Room 2 (accepted) palette, plus four small accents: jitter amber, frost and corridor moss.
art.C.update({"slate": "#34454a", "steel": "#577478", "edge": "#9cb7ab", "brass": "#8f835a", "brass_light": "#c6bd8c", "teal": "#55a4a1", "glow": "#9ddbc8"})
art.C.update({"warn": "#d58b4c", "warn_dark": "#7c4a2f", "frost": "#dcecea", "frost_mid": "#a6c4c8", "moss": "#5c6b3b", "moss_light": "#7e8b4d"})
C = art.C
LAYERS = ["contact-shadow", "structure", "lit-edges", "clue-detail"]
PIXELORAMA_VERSION = "v1.2.3-stable"
layer, rect, line = art.layer, art.rect, art.line


def px(d, points, colour):
    for x, y in points:
        d.point((x, y), fill=C[colour])


def antenna_a():
    """Strongest signal, readings jump: tall Yagi lattice mast, full bars, tall amber jumps."""
    shadow, d = layer()
    d.ellipse((3, 52, 62, 62), fill=C["shadow"])
    body, d = layer()
    # Readout cabinet directly under the clue marker.
    rect(d, (6, 54, 41, 58), "deep", "ink")
    rect(d, (9, 17, 38, 55), "slate", "ink", 2)
    rect(d, (12, 21, 35, 38), "teal_dark", "ink")
    rect(d, (12, 42, 35, 51), "deep", "ink")
    line(d, [(39, 30), (44, 30)], "ink", 2)
    # Lattice mast right of the marker so its array stays visible.
    rect(d, (41, 54, 57, 58), "deep", "ink")
    for x in (44, 53):
        line(d, [(x, 5), (x, 55)], "ink", 3)
        line(d, [(x, 6), (x, 54)], "steel")
    for y in range(9, 53, 9):
        line(d, [(45, y), (52, y + 8)], "slate")
        line(d, [(52, y), (45, y + 8)], "slate")
        line(d, [(44, y), (53, y)], "ink")
    # Side-view Yagi: boom and tapering elements pointing toward the city.
    line(d, [(44, 5), (63, 5)], "ink", 3)
    line(d, [(45, 5), (62, 5)], "steel")
    for x, half in [(50, 5), (54, 4), (58, 3), (62, 2)]:
        line(d, [(x, 5 - half), (x, 5 + half)], "ink", 2)
    lit, d = layer()
    line(d, [(11, 19), (36, 19)], "edge")
    line(d, [(11, 20), (11, 53)], "steel")
    line(d, [(36, 20), (36, 53)], "deep")
    line(d, [(7, 55), (40, 55)], "steel")
    line(d, [(44, 6), (44, 53)], "edge")
    for x, half in [(50, 5), (54, 4), (58, 3), (62, 2)]:
        line(d, [(x, 5 - half), (x, 4)], "edge")
    line(d, [(42, 55), (56, 55)], "steel")
    px(d, [(5, 57), (6, 58), (41, 58), (57, 57), (58, 58)], "moss")
    px(d, [(5, 56), (58, 57)], "moss_light")
    detail, d = layer()
    # Strong baseline broken by tall jumps: strongest, but not steady.
    line(d, [(13, 34), (34, 34)], "glow")
    for x, top in [(17, 23), (23, 27), (29, 22)]:
        line(d, [(x, 33), (x, top)], "warn")
        line(d, [(x + 1, 33), (x + 1, top + 4)], "warn_dark")
    # Four bars, all lit: the strongest channel.
    for i, x in enumerate((15, 20, 25, 30)):
        rect(d, (x, 49 - 2 * i, x + 2, 49), "glow")
    # Interference sparks below the array tip.
    line(d, [(60, 10), (57, 14), (61, 15), (58, 19)], "warn")
    px(d, [(63, 9), (55, 18)], "warn")
    rect(d, (48, 31, 49, 32), "warn")
    rect(d, (40, 29, 41, 31), "brass_light")
    return [shadow, body, lit, detail]


def antenna_b():
    """Weaker but steady: low compact dish, smooth trace, two bars, intact grounded cable."""
    shadow, d = layer()
    d.ellipse((6, 53, 62, 62), fill=C["shadow"])
    body, d = layer()
    rect(d, (12, 55, 46, 58), "deep", "ink")
    rect(d, (25, 34, 32, 56), "slate", "ink")
    # Dish just below the marker disc, tilted up-left toward the city.
    d.ellipse((9, 13, 43, 36), fill=C["ink"])
    d.ellipse((11, 15, 41, 34), fill=C["steel"])
    d.ellipse((16, 18, 36, 31), fill=C["slate"])
    line(d, [(26, 25), (46, 15)], "ink", 2)
    rect(d, (45, 11, 50, 16), "slate", "ink")
    # Status box on the post.
    rect(d, (13, 38, 44, 54), "slate", "ink", 2)
    rect(d, (16, 41, 41, 46), "teal_dark", "ink")
    rect(d, (16, 48, 41, 52), "deep")
    # Grounding rod and the intact cable run.
    rect(d, (54, 45, 57, 59), "brass_dark", "ink")
    line(d, [(46, 56), (49, 56), (52, 54), (54, 54)], "ink", 3)
    lit, d = layer()
    d.arc((11, 15, 41, 34), 150, 280, fill=C["edge"], width=2)
    line(d, [(46, 12), (49, 12)], "edge")
    line(d, [(15, 40), (42, 40)], "edge")
    line(d, [(15, 41), (15, 52)], "steel")
    line(d, [(42, 41), (42, 52)], "deep")
    line(d, [(26, 35), (26, 37)], "steel")
    line(d, [(31, 35), (31, 37)], "deep")
    line(d, [(55, 46), (55, 58)], "brass")
    line(d, [(13, 56), (45, 56)], "steel")
    line(d, [(47, 55), (49, 55), (52, 53), (53, 53)], "steel")
    px(d, [(11, 57), (12, 58), (46, 58), (53, 59), (58, 58)], "moss")
    px(d, [(11, 56), (58, 57)], "moss_light")
    detail, d = layer()
    # Smooth steady sine: weaker, but stable.
    line(d, [(18, 44), (20, 43), (22, 42), (24, 42), (26, 43), (28, 44), (30, 45), (32, 45), (34, 44), (36, 43), (38, 42), (39, 42)], "glow")
    # Two of four bars lit: weaker range.
    for i, x in enumerate((19, 25, 31, 37)):
        rect(d, (x, 51 - i, x + 2, 51), "glow" if i < 2 else "slate")
    # Brass clamps on the cable and at the rod head.
    for x, y in [(48, 55), (51, 53)]:
        rect(d, (x, y, x + 1, y + 2), "brass_light")
    rect(d, (53, 46, 58, 48), "brass", "ink")
    line(d, [(54, 46), (57, 46)], "brass_light")
    # Service tag on the box: checked, not replaced.
    line(d, [(43, 41), (46, 43)], "ink")
    rect(d, (45, 43, 49, 48), "paper", "ink")
    line(d, [(46, 45), (48, 45)], "teal_dark")
    rect(d, (47, 13, 48, 14), "glow")
    return [shadow, body, lit, detail]


def antenna_c():
    """Drops out in wind: bright new head on a weathered mast, wind ribbon, frosted cold battery."""
    shadow, d = layer()
    d.ellipse((2, 52, 63, 62), fill=C["shadow"])
    body, d = layer()
    rect(d, (5, 54, 20, 58), "deep", "ink")
    rect(d, (10, 10, 14, 55), "steel", "ink")
    # Guy wire to the ground, the side that takes the wind.
    line(d, [(15, 14), (22, 54)], "deep")
    # New capsule radome and whip, clearly brighter than the weathered mast.
    line(d, [(12, 0), (12, 2)], "ink")
    rect(d, (8, 2, 16, 10), "brass_light", "ink")
    # Readout clamped to the mast.
    rect(d, (14, 19, 38, 32), "slate", "ink", 2)
    rect(d, (17, 22, 35, 29), "teal_dark", "ink")
    # Squat backup battery with top terminals.
    rect(d, (22, 38, 52, 57), "slate", "ink", 2)
    rect(d, (26, 34, 31, 38), "brass_dark", "ink")
    rect(d, (43, 34, 48, 38), "brass_dark", "ink")
    rect(d, (26, 46, 48, 51), "deep", "ink")
    line(d, [(22, 54), (15, 54)], "ink", 2)
    # The same capsule head, old and dull, lying where it was swapped out.
    rect(d, (53, 51, 61, 56), "slate", "ink")
    line(d, [(62, 54), (63, 54)], "ink")
    lit, d = layer()
    line(d, [(11, 11), (11, 54)], "edge")
    px(d, [(12, 18), (13, 27), (12, 40), (13, 46), (12, 50)], "brass_dark")
    line(d, [(9, 3), (9, 8)], "frost")
    line(d, [(10, 3), (14, 3)], "frost")
    line(d, [(9, 7), (15, 7)], "brass")
    px(d, [(12, 0)], "edge")
    line(d, [(16, 21), (36, 21)], "edge")
    line(d, [(24, 40), (50, 40)], "steel")
    line(d, [(50, 41), (50, 55)], "deep")
    line(d, [(6, 55), (19, 55)], "steel")
    line(d, [(54, 52), (60, 52)], "steel")
    px(d, [(4, 57), (5, 58), (21, 58), (52, 57), (53, 58), (62, 57)], "moss")
    px(d, [(4, 56), (52, 56)], "moss_light")
    detail, d = layer()
    # Wind ribbon streaming away from the marker.
    d.polygon([(10, 12), (1, 13), (4, 15), (0, 18), (10, 16)], fill=C["warn"])
    line(d, [(2, 14), (8, 13)], "warn_dark")
    # Signal drops out: trace, gap, then dashes on the floor line.
    line(d, [(18, 26), (20, 24), (22, 26), (24, 25)], "glow")
    px(d, [(27, 27), (30, 27), (33, 27)], "teal")
    # One of four charge cells lit, in warning amber.
    rect(d, (28, 47, 31, 50), "warn")
    for x in (33, 38, 43):
        rect(d, (x, 47, x + 3, 50), "slate")
    # Frost on the cold battery: rim crust and drips.
    line(d, [(24, 40), (49, 40)], "frost")
    px(d, [(26, 41), (27, 42), (32, 41), (37, 41), (37, 42), (38, 43), (45, 41), (46, 42)], "frost_mid")
    px(d, [(24, 43), (24, 45), (25, 53)], "frost_mid")
    line(d, [(27, 34), (30, 34)], "frost")
    line(d, [(44, 34), (47, 34)], "frost")
    # Old head: cracked, dull.
    line(d, [(56, 52), (58, 55)], "ink")
    line(d, [(54, 54), (60, 54)], "brass_dark")
    return [shadow, body, lit, detail]


def merged(layers):
    out = Image.new("RGBA", (art.W, art.H), (0, 0, 0, 0))
    for img in layers:
        out.alpha_composite(img)
    return out


def ora_bytes(slug, layers, flat):
    import xml.etree.ElementTree as ET
    root = ET.Element("image", {"w": str(art.W), "h": str(art.H), "name": slug, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    buf = io.BytesIO()
    dt = (2026, 10, 17, 2, 40, 0)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), art.png_bytes(flat))
        # OpenRaster stacks list the top layer first.
        for i, (name, img) in reversed(list(enumerate(zip(LAYERS, layers)))):
            src = f"data/layer{i:02d}.png"
            z.writestr(zipfile.ZipInfo(src, dt), art.png_bytes(img))
            ET.SubElement(stack, "layer", {"name": name, "src": src, "x": "0", "y": "0", "opacity": "1.0", "visibility": "visible", "composite-op": "svg:src-over"})
        z.writestr(zipfile.ZipInfo("stack.xml", dt), ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return buf.getvalue()


def pxo_bytes(slug, layers, flat):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in LAYERS]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0} for _ in LAYERS],
                    "duration": 1.0, "metadata": {}}]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(f"yonkers-room1-{slug}"),
                      "frame_current_tag": "0", "include_tag_in_filename": "false", "interpolation": "0",
                      "lines_count": "1", "new_dir_for_each_frame_tag": "false", "number_of_digits": "4",
                      "number_of_frames": "1", "orientation": "0", "repeat_count": "0", "resize": "100",
                      "save_quality": "0.75", "separator_character": "\"_\"",
                      "sheet_layers_as_separate_files": "false", "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": len(LAYERS) - 1,
            "export_profile": export_profile, "fps": 6.0, "frames": frames_json, "guides": [], "layers": layer_json,
            "license": "", "metadata": {}, "next_keyframe_id": 0, "palettes": [],
            "pixelorama_version": PIXELORAMA_VERSION, "project_current_palette_name": "", "pxo_version": 7,
            "reference_images": [], "size_x": art.W, "size_y": art.H, "symmetry_points": [art.W - 1.0, art.H - 1.0], "tags": [],
            "tile_mode_x_basis_x": art.W, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": art.H,
            "tilesets": [], "user_data": "", "vanishing_points": []}
    buf = io.BytesIO()
    dt = (2026, 10, 17, 2, 40, 0)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", art.png_bytes(flat))
        put("image_data/frames/1/", b"")
        for i, img in enumerate(layers, start=1):
            put(f"image_data/frames/1/layer_{i}", img.tobytes())
            put(f"image_data/frames/1/indices_layer_{i}", b"\x00")
    return buf.getvalue()


def sha(data):
    return hashlib.sha256(data).hexdigest()


FIXTURES = [
    ("a-jitter-mast", antenna_a, 0, "天线 A / Antenna A: tall Yagi mast, all four bars lit, jagged amber trace and tip sparks = strongest but jumpy"),
    ("b-steady-dish", antenna_b, 1, "天线 B / Antenna B: low dish, two of four bars, smooth sine, intact clamped cable to a ground stake, service tag = weaker but steady"),
    ("c-cold-mast", antenna_c, 2, "天线 C / Antenna C: bright new radome on a weathered guyed mast, wind ribbon, dropout trace, frosted battery at one amber cell, old head on the floor = wind dropouts not fixed by a new head"),
]


def build():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    items = []
    for slug, author, clue_index, meaning in FIXTURES:
        layers = author()
        flat = merged(layers)
        stem = f"{art.PREFIX}_{slug}-pixel-fixture_unapproved-v01_{art.STAMP}"
        png = art.png_bytes(flat)
        files = {"png": png, "ora": ora_bytes(slug, layers, flat), "pxo": pxo_bytes(slug, layers, flat)}
        for ext, data in files.items():
            (art.OUT / f"{stem}.{ext}").write_bytes(data)
        (RUNTIME / f"{stem}.png").write_bytes(png)
        items.append({
            "purpose": slug, "clue": f"scifi.outskirts:{clue_index}", "reads_as": meaning,
            "size": [art.W, art.H], "layers_bottom_to_top": LAYERS,
            "screen_rect_640x360": "CLUE_POSITIONS[%d] + (-32, 2), 64x64, drawn under the clue marker and labels" % clue_index,
            "files": {ext: {"file": str((art.OUT / f"{stem}.{ext}").relative_to(ROOT)).replace("\\", "/"), "sha256": sha(data), "hash_algorithm": "sha256-bytes"} for ext, data in files.items()},
            "runtime_png": {"file": str((RUNTIME / f"{stem}.png").relative_to(ROOT)).replace("\\", "/"), "sha256": sha(png), "hash_algorithm": "sha256-bytes"},
        })
    manifest = {
        "project": "Worlds Between", "scene": "Yonkers outskirts survey annex room 1 (天线走廊 / Antenna Walkway)",
        "status": "UNAPPROVED candidate; creator has not reviewed; scene-visual counters unchanged (3/12, 40.8%)",
        "style_reference": "accepted Yonkers maintenance room 2 fixtures (a73e60b4): same palette, ink outline, contact-shadow ellipse and 64x64 placement",
        "authorship": "Hand-placed primitives in this tool by Claude (Claude Code, signed-in Claude Max, firstParty); no image generation, resampling or filtering.",
        "pixelorama": "pxo_version 7, color_mode 5, 1 frame x 4 layers; ORA lists the same 4 layers",
        "assets": items,
        "source": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
    }
    path = art.OUT / f"{art.PREFIX}_three-antenna-fixtures-manifest_unapproved-v01_{art.STAMP}.json"
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    return manifest


if __name__ == "__main__":
    build()
