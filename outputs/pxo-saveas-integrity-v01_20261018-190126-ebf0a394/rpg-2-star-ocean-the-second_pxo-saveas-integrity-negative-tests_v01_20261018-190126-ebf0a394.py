"""Negative/positive tests for the pxo Save As integrity checker (v01, stdlib only).

Builds tiny synthetic .pxo files (a few pixels, a few frames/layers) in a
fresh directory under %LOCALAPPDATA%\\Temp, runs the checker as a
subprocess (python -I) for each case, and asserts exit code, result and
that no private sentinel (path, author, names, user_data) appears in
stdout, stderr or the written report. No real art is copied.

Usage: python -I <this file>   (the checker is the sibling v01 file)
Prints one JSON summary; exit 0 if every case behaves as expected.
"""

import copy
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import uuid
import warnings
import zipfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "rpg-2-star-ocean-the-second_pxo-saveas-integrity-checker_v01_20261018-190126-ebf0a394.py")
PRIVATE_DIR = "SENTINEL_PRIVATE_PATH_7f3c"
AUTHOR = "SENTINEL_AUTHOR_9d2e"
AUTHOR2 = "SENTINEL_AUTHOR_CHANGED_44aa"
SENTINELS = (PRIVATE_DIR, AUTHOR, AUTHOR2, "SENTINEL_LAYER_NAME", "SENTINEL_TAG_NAME",
             "SENTINEL_USER_DATA", "SENTINEL_KEY_NAME")


def ext(p):
    p = os.path.abspath(p)
    if os.name != "nt" or p.startswith("\\\\?\\"):
        return p
    return "\\\\?\\" + p


def png(w, h, seed=0, idat_edit=None):
    raw = b"".join(b"\x00" + bytes(((x + y + seed) * 37) & 0xFF for x in range(w * 4)) for y in range(h))

    def chunk(t, body):
        return struct.pack(">I", len(body)) + t + body + struct.pack(">I", zlib.crc32(t + body) & 0xFFFFFFFF)
    idat = zlib.compress(raw)
    if idat_edit:
        idat = idat_edit(idat)  # chunk CRCs stay correct; only the zlib stream is damaged
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def ep_private_key(value):
    def apply(p):
        p["doc"]["export_profile"]["C:/%s/profile" % PRIVATE_DIR] = value
    return apply


def make_project(frames=3, layers=2, w=4, h=3):
    doc = {
        "author_company": AUTHOR, "author_contact": AUTHOR, "author_display_name": AUTHOR,
        "author_real_name": AUTHOR, "brushes": [], "color_mode": 5, "current_frame": 0,
        "current_layer": 0,
        "export_profile": {"crop_mode": "0", "directory_path": '"C:/%s/out"' % PRIVATE_DIR,
                           "file_name": '"%s_export"' % AUTHOR, "resize": "100",
                           "split_layers": "false"},
        "fps": 12.0,
        "frames": [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)",
                              "z_index": 0} for _ in range(layers)],
                    "duration": 0.25 * (1 + f % 2), "metadata": {}} for f in range(frames)],
        "guides": [],
        "layers": [{"animated_params": "Dictionary[String, Dictionary]({})", "blend_mode": 0,
                    "clipping_mask": False, "effects": [], "locked": i == layers - 1,
                    "metadata": {}, "name": "SENTINEL_LAYER_NAME_%d" % i, "new_cels_linked": False,
                    "opacity": 1.0, "parent": -1, "type": 0, "ui_color": "(0.0, 0.0, 0.0, 0.0)",
                    "visible": i != layers - 1} for i in range(layers)],
        "license": AUTHOR, "metadata": {}, "next_keyframe_id": 0, "palettes": [],
        "pixelorama_version": "v1.2.3-stable", "project_current_palette_name": "",
        "pxo_version": 7, "reference_images": [], "size_x": w, "size_y": h,
        "symmetry_points": [[2.0, 1.5], [2.0, 1.5]],
        "tags": [{"name": "SENTINEL_TAG_NAME", "from": 1, "to": frames, "color": "1a9999"}],
        "tile_mode_x_basis_x": w, "tile_mode_x_basis_y": 0, "tile_mode_y_basis_x": 0,
        "tile_mode_y_basis_y": h, "tilesets": [], "user_data": "SENTINEL_USER_DATA " + PRIVATE_DIR,
        "vanishing_points": [],
    }
    entries = [("mimetype", b"application/x-pixelorama"), ("data.json", None),
               ("preview.png", png(w, h))]
    for f in range(1, frames + 1):
        entries.append(("image_data/frames/%d/" % f, b""))
        for l in range(1, layers + 1):
            entries.append(("image_data/frames/%d/layer_%d" % (f, l),
                            bytes(((f * 7 + l * 13 + i) & 0xFF) for i in range(w * h * 4))))
            entries.append(("image_data/frames/%d/indices_layer_%d" % (f, l), b"\x00"))
    return {"doc": doc, "entries": entries, "json_text": None}


def write_project(proj, path, reverse=False, compression=zipfile.ZIP_DEFLATED):
    text = proj["json_text"] if proj["json_text"] is not None else json.dumps(proj["doc"], indent=1)
    items = [(n, text.encode("utf-8") if b is None else b) for n, b in proj["entries"]]
    if reverse:
        items = items[:1] + items[1:][::-1]
    with open(ext(path), "wb") as fh, warnings.catch_warnings():
        warnings.simplefilter("ignore")  # the duplicate-entry case is deliberate
        with zipfile.ZipFile(fh, "w", compression) as zf:
            for n, b in items:
                zf.writestr(n, b)


def set_entry(proj, name, data):
    proj["entries"] = [(n, data if n == name else b) for n, b in proj["entries"]]


def drop_entry(proj, name):
    proj["entries"] = [(n, b) for n, b in proj["entries"] if n != name]


def flip_cel(p):
    k = "image_data/frames/2/layer_2"
    b = bytearray(dict(p["entries"])[k]); b[5] ^= 0x01
    set_entry(p, k, bytes(b))


def mut(fn):
    def apply(p):
        fn(p["doc"])
    return apply


def reorder_keys(p):
    d = p["doc"]
    p["doc"] = {k: d[k] for k in sorted(d, reverse=True)}
    p["doc"]["tags"] = [{k: t[k] for k in ("color", "to", "from", "name")} for t in d["tags"]]


def add_dup_zip(p):
    p["entries"].append(("image_data/frames/1/layer_1", dict(p["entries"])["image_data/frames/1/layer_1"]))


def dup_json(p):
    text = json.dumps(p["doc"])
    p["json_text"] = text[:-1] + ', "fps": 12.0}'


def unknown_top(d):
    d["SENTINEL_KEY_NAME_top"] = 1


CASES = [
    # name, saved-mutation, expected exit, extra kwargs
    ("baseline_identical_pass", None, 0, {}),
    ("selection_and_saveas_fields_pass",
     mut(lambda d: (d.update(current_frame=2, current_layer=1),
                    d["export_profile"].update(directory_path='"user://"', file_name='"x"'))), 0,
     {"allowed": ["current_frame", "current_layer", "export_profile.directory_path",
                  "export_profile.file_name"]}),
    ("opaque_tag_color_rgb6_to_rgba8_pass", mut(lambda d: d["tags"][0].update(color="1A9999FF")), 0,
     {"normalized": 1}),
    ("key_order_zip_order_compression_pass", reorder_keys, 0, {"reverse": True, "stored": True}),
    ("preview_thumbnail_change_excluded_pass", lambda p: set_entry(p, "preview.png", png(9, 5, 3)), 0, {}),
    ("generic_other_shape_5x4_pass", None, 0, {"shape": (5, 4, 3, 2)}),
    ("long_windows_path_pass", None, 0, {"long": True}),
    ("report_file_written_pass", None, 0, {"report": True}),
    ("raw_cel_byte_flip_fail", flip_cel, 1, {"location": "frame 2 layer 2 raw cel"}),
    ("index_payload_change_fail",
     lambda p: set_entry(p, "image_data/frames/3/indices_layer_1", b"\x01"), 1, {}),
    ("frame_duration_change_fail", mut(lambda d: d["frames"][1].update(duration=0.3)), 1,
     {"location": "data.json frames[1].duration"}),
    ("fps_change_fail", mut(lambda d: d.update(fps=13.0)), 1, {}),
    ("fps_int_vs_float_type_fail", mut(lambda d: d.update(fps=12)), 1, {}),
    ("layer_hidden_toggle_fail", mut(lambda d: d["layers"][1].update(visible=True)), 1,
     {"location": "data.json layers[1].visible"}),
    ("layer_lock_toggle_fail", mut(lambda d: d["layers"][1].update(locked=False)), 1, {}),
    ("cel_opacity_change_fail", mut(lambda d: d["frames"][0]["cels"][0].update(opacity=0.5)), 1, {}),
    ("author_field_change_fail", mut(lambda d: d.update(author_real_name=AUTHOR2)), 1,
     {"location": "data.json author_real_name"}),
    ("user_data_change_fail", mut(lambda d: d.update(user_data="SENTINEL_USER_DATA x")), 1, {}),
    ("layer_name_change_fail", mut(lambda d: d["layers"][0].update(name="SENTINEL_LAYER_NAME_x")), 1, {}),
    ("unexpected_frame_metadata_fail",
     mut(lambda d: d["frames"][0]["metadata"].update({"SENTINEL_KEY_NAME_meta": AUTHOR2})), 1,
     {"location": "data.json frames[0].metadata"}),
    ("unexpected_project_metadata_fail", mut(lambda d: d["metadata"].update(x=1)), 1, {}),
    ("tag_color_alpha_change_fail", mut(lambda d: d["tags"][0].update(color="1a999980")), 1,
     {"location": "data.json tags[0].color"}),
    ("tag_color_rgb_change_fail", mut(lambda d: d["tags"][0].update(color="1a9998ff")), 1, {}),
    ("tag_range_change_fail", mut(lambda d: d["tags"][0].update(to=2)), 1, {}),
    ("unexpected_export_profile_key_refused",
     mut(lambda d: d["export_profile"].update({"SENTINEL_KEY_NAME_ep": AUTHOR2})), 1,
     {"location": "data.json export_profile (key set)"}),
    ("export_profile_other_value_fail", mut(lambda d: d["export_profile"].update(resize="200")), 1,
     {"location": "data.json export_profile (non-SaveAs field value)"}),
    # correction regression: same private-path key on both sides, values 'a' vs 'b'
    ("export_profile_private_key_value_no_echo_fail", ep_private_key("b"), 1,
     {"source_mutation": ep_private_key("a"),
      "location": "data.json export_profile (non-SaveAs field value)"}),
    ("layer_count_differs_fail", None, 1, {"saved_shape": (3, 3, 4, 3)}),
    ("frame_count_differs_fail", None, 1, {"saved_shape": (4, 2, 4, 3)}),
    ("missing_cel_error", lambda p: drop_entry(p, "image_data/frames/2/layer_1"), 2,
     {"code": "missing_cel_payload"}),
    ("malformed_json_error", lambda p: p.update(json_text='{"fps": 12.0, '), 2,
     {"code": "data_json_malformed"}),
    ("duplicate_json_key_error", dup_json, 2, {"code": "duplicate_json_key"}),
    ("duplicate_zip_path_error", add_dup_zip, 2, {"code": "duplicate_zip_entry"}),
    ("not_a_zip_error", "notzip", 2, {"code": "zip_unreadable"}),
    ("unexpected_zip_entry_error", lambda p: p["entries"].append(("SENTINEL_KEY_NAME.txt", b"x")), 2,
     {"code": "unexpected_zip_entry"}),
    ("wrong_cel_size_error",
     lambda p: set_entry(p, "image_data/frames/1/layer_1", b"\x00" * 47), 2,
     {"code": "cel_payload_size_invalid"}),
    ("mimetype_wrong_error", lambda p: set_entry(p, "mimetype", b"application/zip"), 2,
     {"code": "not_a_pixelorama_project"}),
    ("unsupported_layer_type_error", mut(lambda d: d["layers"][0].update(type=1)), 2,
     {"code": "unsupported_layer_type"}),
    ("unsupported_tag_color_type_error", mut(lambda d: d["tags"][0].update(color=1710489)), 2,
     {"code": "unsupported_tag_color"}),
    ("unsupported_tag_color_format_error", mut(lambda d: d["tags"][0].update(color="#1a9999")), 2,
     {"code": "unsupported_tag_color"}),
    ("unsupported_color_mode_error", mut(lambda d: d.update(color_mode=4)), 2,
     {"code": "unsupported_color_mode"}),
    ("unexpected_top_level_key_error", mut(unknown_top), 2, {"code": "unexpected_top_level_key"}),
    ("invalid_frame_duration_error", mut(lambda d: d["frames"][0].update(duration=-1)), 2,
     {"code": "invalid_frame_metadata"}),
    ("cel_count_mismatch_error", mut(lambda d: d["frames"][0]["cels"].pop()), 2,
     {"code": "invalid_cel_count"}),
    ("invalid_layer_metadata_error", mut(lambda d: d["layers"][0].update(visible=1)), 2,
     {"code": "invalid_layer_metadata"}),
    ("non_finite_json_number_error", lambda p: p.update(json_text=json.dumps(p["doc"]).replace('"fps": 12.0', '"fps": NaN')), 2,
     {"code": "non_finite_json_number"}),
    ("invalid_preview_png_error", lambda p: set_entry(p, "preview.png", b"\x89PNG\r\n\x1a\nbroken"), 2,
     {"code": "preview_png_invalid"}),
    # correction regressions: CRC-correct PNG, 4x3 RGBA8, IDAT zlib stream damaged
    ("preview_png_truncated_zlib_error",
     lambda p: set_entry(p, "preview.png", png(4, 3, idat_edit=lambda z: z[:-2])), 2,
     {"code": "preview_png_invalid"}),
    ("preview_png_trailing_zlib_data_error",
     lambda p: set_entry(p, "preview.png", png(4, 3, idat_edit=lambda z: z + b"\x00\x00")), 2,
     {"code": "preview_png_invalid"}),
    ("preview_png_illegal_filter_byte_error",
     lambda p: set_entry(p, "preview.png", png(4, 3, idat_edit=lambda z: zlib.compress(bytes([5]) + zlib.decompress(z)[1:]))), 2,
     {"code": "preview_png_invalid"}),
    ("relative_path_error", None, 2, {"relative": True, "code": "path_not_absolute"}),
    ("missing_file_error", None, 2, {"missing": True, "code": "input_missing_or_unreadable"}),
    ("unknown_argument_error", None, 2, {"badarg": True, "code": "bad_arguments"}),
    ("report_already_exists_error", None, 2, {"report_exists": True, "code": "report_already_exists"}),
]


def run_case(root, case, py):
    name, mutation, want, kw = case
    cdir = os.path.join(root, PRIVATE_DIR, name)
    if kw.get("long"):
        cdir = os.path.join(cdir, *(["L" + "x" * 60] * 4))
    os.makedirs(ext(cdir))
    shape = kw.get("shape", (3, 2, 4, 3))
    src_path = os.path.join(cdir, "source_" + AUTHOR + ".pxo")
    sav_path = os.path.join(cdir, "saved_" + AUTHOR + ".pxo")
    source = make_project(*shape)
    if kw.get("source_mutation"):
        kw["source_mutation"](source)
    write_project(source, src_path)
    saved = make_project(*kw.get("saved_shape", shape))
    if mutation == "notzip":
        with open(ext(sav_path), "wb") as fh:
            fh.write(b"PK\x03\x04 not really a zip " + AUTHOR.encode())
    else:
        if mutation is not None:
            mutation(saved)
        write_project(saved, sav_path, reverse=kw.get("reverse", False),
                      compression=zipfile.ZIP_STORED if kw.get("stored") else zipfile.ZIP_DEFLATED)
    args = ["--source", src_path, "--saved", sav_path]
    if kw.get("relative"):
        args[1] = "source_" + AUTHOR + ".pxo"
    if kw.get("missing"):
        args[3] = os.path.join(cdir, "absent_" + AUTHOR + ".pxo")
    if kw.get("badarg"):
        args += ["--" + PRIVATE_DIR, AUTHOR]
    report_path = None
    if kw.get("report") or kw.get("report_exists"):
        report_path = os.path.join(cdir, "report_" + AUTHOR + ".json")
        args += ["--report", report_path]
        if kw.get("report_exists"):
            with open(ext(report_path), "w") as fh:
                fh.write("{}")
    proc = subprocess.run([py, "-I", CHECKER] + args, capture_output=True, timeout=120)
    out, err = proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")
    problems = []
    if proc.returncode != want:
        problems.append("exit %d != %d" % (proc.returncode, want))
    if err:
        problems.append("stderr not empty")
    try:
        obj = json.loads(out)
    except ValueError:
        obj = {}
        problems.append("stdout not JSON")
    expected_result = {0: "PASS", 1: "FAIL", 2: "ERROR"}[want]
    if obj.get("result") != expected_result:
        problems.append("result mismatch")
    texts = [out, err]
    if report_path and kw.get("report"):
        with open(ext(report_path), encoding="utf-8") as fh:
            rtext = fh.read()
        texts.append(rtext)
        if rtext != out:
            problems.append("report != stdout")
    blob = "\n".join(texts)
    leaked = [s for s in SENTINELS if s in blob]
    if leaked or "Traceback" in blob or os.path.abspath(root).lower() in blob.lower():
        problems.append("leak")
    comp = obj.get("comparison", {})
    if "allowed" in kw and comp.get("allowed_differences_observed") != kw["allowed"]:
        problems.append("allowed-diff list mismatch")
    if "normalized" in kw and len(comp.get("normalizations_applied", [])) != kw["normalized"]:
        problems.append("normalization count mismatch")
    if "location" in kw and kw["location"] not in obj.get("differences", []):
        problems.append("expected difference location missing")
    if "code" in kw and [e.get("code") for e in obj.get("errors", [])] != [kw["code"]]:
        problems.append("error code mismatch")
    if want == 0 and not kw.get("shape") and comp.get("raw_cels_compared") != 6:
        problems.append("cell count mismatch")
    if kw.get("shape") and comp.get("raw_cels_compared") != shape[0] * shape[1]:
        problems.append("generic shape cell count mismatch")
    return {"case": name, "expected_exit": want, "actual_exit": proc.returncode,
            "ok": not problems, "problems": problems,
            "max_path_len": len(os.path.abspath(sav_path)) if kw.get("long") else None}


def main():
    py = sys.executable
    base = os.environ.get("LOCALAPPDATA")
    base = os.path.join(base, "Temp") if base else tempfile.gettempdir()
    root = os.path.join(base, "pxo-saveas-neg-" + uuid.uuid4().hex[:8])
    os.makedirs(ext(root))
    try:
        results = [run_case(root, c, py) for c in CASES]
    finally:
        shutil.rmtree(ext(root), ignore_errors=True)
    long_len = max((r["max_path_len"] or 0) for r in results)
    for r in results:
        r.pop("max_path_len")
    failed = [r for r in results if not r["ok"]]
    summary = {"tool": "rpg-2-star-ocean-the-second_pxo-saveas-integrity-negative-tests", "version": "v01",
               "cases": len(results), "passed": len(results) - len(failed), "failed": len(failed),
               "long_path_case_length": long_len, "temp_root_removed": not os.path.exists(ext(root)),
               "results": results}
    sys.stdout.write(json.dumps(summary, indent=1) + "\n")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
