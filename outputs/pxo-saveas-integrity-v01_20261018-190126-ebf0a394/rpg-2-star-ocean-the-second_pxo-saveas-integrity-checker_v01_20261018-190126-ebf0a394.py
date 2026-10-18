"""Pixelorama .pxo Save As round-trip integrity checker (v01, stdlib only).

Compares a source .pxo with a .pxo produced by a GUI "Save As" and proves
that every raw cel payload, every index payload, every non-thumbnail ZIP
payload and every semantic data.json field is identical, except for a
small, explicit allow-list:

  * current_frame / current_layer       (UI selection)
  * export_profile.directory_path / file_name   (Save As bookkeeping)
  * tags[*].color  opaque RGB6 hex -> the same RGBA8 hex with "ff" alpha
  * preview.png    derived UI thumbnail: validated as a PNG, NOT compared

Usage:
  python -I <this file> --source C:/abs/a.pxo --saved C:/abs/b.pxo [--report C:/abs/r.json]

stdout is one JSON object. Exit 0 = PASS, 1 = FAIL (mismatch),
2 = ERROR (malformed, unsupported, unreadable or bad arguments).
The output never contains file paths, exception text, layer/tag names,
author fields or any other string value from the inputs; only SHA-256
digests, counts, numeric timing/size facts and difference key locations.
Only RGBA8 pixel layers are supported; anything else fails closed.
"""

import argparse
import hashlib
import io
import json
import math
import os
import re
import struct
import sys
import zipfile
import zlib

TOOL = "rpg-2-star-ocean-the-second_pxo-saveas-integrity-checker"
VERSION = "v01"
MAX_FILE_BYTES = 256 * 1024 * 1024
MAX_ENTRY_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_ENTRIES = 200000
MAX_LOCATIONS = 50
SUPPORTED_PXO_VERSIONS = (7,)
RGBA8_COLOR_MODE = 5  # Godot Image.FORMAT_RGBA8

TOP_KEYS = frozenset([
    "author_company", "author_contact", "author_display_name", "author_real_name",
    "brushes", "color_mode", "current_frame", "current_layer", "export_profile",
    "fps", "frames", "guides", "layers", "license", "metadata", "next_keyframe_id",
    "palettes", "pixelorama_version", "project_current_palette_name", "pxo_version",
    "reference_images", "size_x", "size_y", "symmetry_points", "tags",
    "tile_mode_x_basis_x", "tile_mode_x_basis_y", "tile_mode_y_basis_x",
    "tile_mode_y_basis_y", "tilesets", "user_data", "vanishing_points",
])
AUTHOR_KEYS = ("author_company", "author_contact", "author_display_name",
               "author_real_name", "license", "user_data")
LAYER_KEYS = frozenset([
    "animated_params", "blend_mode", "clipping_mask", "effects", "locked",
    "metadata", "name", "new_cels_linked", "opacity", "parent", "type",
    "ui_color", "visible",
])
FRAME_KEYS = frozenset(["cels", "duration", "metadata"])
CEL_KEYS = frozenset(["metadata", "opacity", "ui_color", "z_index"])
TAG_KEYS = frozenset(["name", "from", "to", "color"])
# Free-form containers: differences are reported at this location only,
# never by inner key name (inner keys may be author-controlled strings).
OPAQUE_FIELDS = frozenset(["metadata", "effects", "brushes", "guides", "palettes",
                           "reference_images", "symmetry_points", "vanishing_points",
                           "tilesets"])
ALLOWED_TOP_DIFF = ("current_frame", "current_layer")
ALLOWED_EXPORT_DIFF = ("directory_path", "file_name")

ENTRY_RE = re.compile(r"^image_data/frames/([1-9][0-9]*)/(?:(layer|indices_layer)_([1-9][0-9]*))?$")
HEX6 = re.compile(r"^[0-9a-fA-F]{6}$")
HEX8 = re.compile(r"^[0-9a-fA-F]{8}$")


class CheckError(Exception):
    """Fail-closed refusal; carries only a fixed code and a safe location."""

    def __init__(self, code, where=None, location=None):
        super().__init__(code)
        self.code = code
        self.where = where
        self.location = location

    def as_dict(self):
        d = {"code": self.code}
        if self.where:
            d["input"] = self.where
        if self.location:
            d["location"] = self.location
        return d


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # never echo argument values
        raise CheckError("bad_arguments")


def _extended(path):
    """Absolute path with the Windows extended-length prefix (MAX_PATH safe)."""
    p = os.path.abspath(path)
    if os.name != "nt" or p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC\\" + p[2:]
    return "\\\\?\\" + p


def _read_input(raw, where):
    if not raw or not os.path.isabs(raw):
        raise CheckError("path_not_absolute", where)
    ext = _extended(raw)
    try:
        st = os.stat(ext)
    except OSError:
        raise CheckError("input_missing_or_unreadable", where)
    if not os.path.isfile(ext):
        raise CheckError("input_not_a_file", where)
    if st.st_size > MAX_FILE_BYTES:
        raise CheckError("input_too_large", where)
    try:
        with open(ext, "rb") as fh:
            return fh.read(MAX_FILE_BYTES + 1)
    except OSError:
        raise CheckError("input_missing_or_unreadable", where)


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _no_dup_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise CheckError("duplicate_json_key")
        out[k] = v
    return out


def _bad_constant(_):
    raise CheckError("non_finite_json_number")


def _load_zip(blob, where):
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
        infos = zf.infolist()
    except CheckError:
        raise
    except Exception:
        raise CheckError("zip_unreadable", where)
    if not infos or len(infos) > MAX_ENTRIES:
        raise CheckError("zip_entry_count_invalid", where)
    names = [i.filename for i in infos]
    seen = set()
    for n in names:
        if n in seen:
            raise CheckError("duplicate_zip_entry", where)
        seen.add(n)
    entries = {}
    dirs = set()
    total = 0
    for info in infos:
        n = info.filename
        parts = n.rstrip("/").split("/")
        if (n.startswith("/") or "\\" in n or ":" in n or "\x00" in n
                or any(p in ("", ".", "..") for p in parts)):
            raise CheckError("zip_entry_name_invalid", where)
        if info.flag_bits & 0x1:
            raise CheckError("zip_entry_encrypted", where)
        if n.endswith("/"):
            if info.file_size != 0:
                raise CheckError("zip_directory_has_payload", where)
            dirs.add(n)
            continue
        if info.file_size > MAX_ENTRY_BYTES:
            raise CheckError("zip_entry_too_large", where)
        total += info.file_size
        if total > MAX_TOTAL_BYTES:
            raise CheckError("zip_total_too_large", where)
        try:
            with zf.open(info) as fh:
                data = fh.read(MAX_ENTRY_BYTES + 1)
        except Exception:
            raise CheckError("zip_entry_corrupt", where)
        if len(data) != info.file_size:
            raise CheckError("zip_entry_corrupt", where)
        entries[n] = data
    return entries, dirs, len(infos)


def _is_num(x):
    return type(x) in (int, float) and math.isfinite(x)


def _is_int(x):
    return type(x) is int


def _need(cond, code, where, location=None):
    if not cond:
        raise CheckError(code, where, location)


def _check_png(data, where):
    """Structural PNG validation (signature, chunk CRCs, IHDR, complete IDAT zlib stream and size, IEND)."""
    _need(data[:8] == b"\x89PNG\r\n\x1a\n", "preview_png_invalid", where)
    pos, chunks, idat = 8, [], b""
    while pos < len(data):
        _need(pos + 12 <= len(data), "preview_png_invalid", where)
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        _need(len(body) == length and pos + 12 + length <= len(data), "preview_png_invalid", where)
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        _need(zlib.crc32(ctype + body) & 0xFFFFFFFF == crc, "preview_png_invalid", where)
        chunks.append(ctype)
        if ctype == b"IHDR":
            _need(length == 13, "preview_png_invalid", where)
            w, h, depth, ctype_id, comp, filt, interlace = struct.unpack(">IIBBBBB", body)
        elif ctype == b"IDAT":
            idat += body
        pos += 12 + length
        if ctype == b"IEND":
            break
    _need(chunks and chunks[0] == b"IHDR" and chunks[-1] == b"IEND" and pos == len(data)
          and b"IDAT" in chunks, "preview_png_invalid", where)
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype_id)
    _need(channels and w > 0 and h > 0 and depth in (1, 2, 4, 8, 16) and comp == 0
          and filt == 0 and interlace == 0, "preview_png_unsupported", where)
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(idat, MAX_ENTRY_BYTES)
    except zlib.error:
        raise CheckError("preview_png_invalid", where)
    # complete stream (Adler-32 trailer verified), nothing left over or trailing
    _need(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail,
          "preview_png_invalid", where)
    row = (w * channels * depth + 7) // 8
    _need(len(raw) == h * (row + 1), "preview_png_invalid", where)
    _need(all(raw[y * (row + 1)] <= 4 for y in range(h)), "preview_png_invalid", where)
    return {"width": w, "height": h}


def _validate(doc, entries, dirs, where):
    """Fail-closed structural validation; returns the derived frame/layer shape."""
    _need(isinstance(doc, dict), "data_json_not_object", where)
    keys = set(doc)
    _need(not (keys - TOP_KEYS), "unexpected_top_level_key", where)
    _need(not (TOP_KEYS - keys), "missing_top_level_key", where)
    _need(doc["pxo_version"] in SUPPORTED_PXO_VERSIONS and _is_int(doc["pxo_version"]),
          "unsupported_pxo_version", where)
    _need(_is_int(doc["color_mode"]) and doc["color_mode"] == RGBA8_COLOR_MODE,
          "unsupported_color_mode", where)
    w, h = doc["size_x"], doc["size_y"]
    _need(_is_int(w) and _is_int(h) and 0 < w <= 16384 and 0 < h <= 16384,
          "invalid_dimensions", where)
    _need(_is_num(doc["fps"]) and doc["fps"] > 0, "invalid_fps", where, "fps")
    for k in AUTHOR_KEYS + ("pixelorama_version", "project_current_palette_name"):
        _need(isinstance(doc[k], str), "invalid_string_field", where, k)
    for k in ("next_keyframe_id", "tile_mode_x_basis_x", "tile_mode_x_basis_y",
              "tile_mode_y_basis_x", "tile_mode_y_basis_y"):
        _need(_is_int(doc[k]), "invalid_integer_field", where, k)
    for k in ("brushes", "guides", "palettes", "reference_images", "symmetry_points",
              "tilesets", "vanishing_points", "tags", "frames", "layers"):
        _need(isinstance(doc[k], list), "invalid_list_field", where, k)
    _need(isinstance(doc["metadata"], dict), "invalid_metadata", where, "metadata")
    _need(not doc["tilesets"], "unsupported_tilesets", where, "tilesets")
    _need(not doc["reference_images"], "unsupported_reference_images", where, "reference_images")
    ep = doc["export_profile"]
    _need(isinstance(ep, dict) and all(isinstance(v, str) for v in ep.values()),
          "invalid_export_profile", where, "export_profile")
    for k in ALLOWED_EXPORT_DIFF:
        _need(k in ep, "invalid_export_profile", where, "export_profile." + k)

    layers, frames = doc["layers"], doc["frames"]
    n_layers, n_frames = len(layers), len(frames)
    _need(0 < n_layers <= 1000 and 0 < n_frames <= 100000, "invalid_frame_layer_count", where)
    for i, layer in enumerate(layers):
        loc = "layers[%d]" % i
        _need(isinstance(layer, dict) and set(layer) == LAYER_KEYS, "invalid_layer_keys", where, loc)
        _need(_is_int(layer["type"]), "invalid_layer_metadata", where, loc + ".type")
        _need(layer["type"] == 0, "unsupported_layer_type", where, loc + ".type")
        for b in ("visible", "locked", "clipping_mask", "new_cels_linked"):
            _need(type(layer[b]) is bool, "invalid_layer_metadata", where, loc + "." + b)
        _need(_is_int(layer["parent"]) and layer["parent"] == -1,
              "unsupported_layer_parent", where, loc + ".parent")
        _need(_is_num(layer["opacity"]) and 0 <= layer["opacity"] <= 1,
              "invalid_layer_metadata", where, loc + ".opacity")
        _need(_is_int(layer["blend_mode"]), "invalid_layer_metadata", where, loc + ".blend_mode")
        for s in ("name", "ui_color", "animated_params"):
            _need(isinstance(layer[s], str), "invalid_layer_metadata", where, loc + "." + s)
        _need(isinstance(layer["effects"], list) and isinstance(layer["metadata"], dict),
              "invalid_layer_metadata", where, loc)
    for f, frame in enumerate(frames):
        loc = "frames[%d]" % f
        _need(isinstance(frame, dict) and set(frame) == FRAME_KEYS, "invalid_frame_keys", where, loc)
        _need(_is_num(frame["duration"]) and frame["duration"] > 0,
              "invalid_frame_metadata", where, loc + ".duration")
        _need(isinstance(frame["metadata"], dict), "invalid_frame_metadata", where, loc + ".metadata")
        cels = frame["cels"]
        _need(isinstance(cels, list) and len(cels) == n_layers, "invalid_cel_count", where, loc + ".cels")
        for c, cel in enumerate(cels):
            cloc = "%s.cels[%d]" % (loc, c)
            _need(isinstance(cel, dict) and set(cel) == CEL_KEYS, "invalid_cel_keys", where, cloc)
            _need(_is_num(cel["opacity"]) and 0 <= cel["opacity"] <= 1,
                  "invalid_cel_metadata", where, cloc + ".opacity")
            _need(_is_int(cel["z_index"]) and isinstance(cel["ui_color"], str)
                  and isinstance(cel["metadata"], dict), "invalid_cel_metadata", where, cloc)
    for t, tag in enumerate(doc["tags"]):
        loc = "tags[%d]" % t
        _need(isinstance(tag, dict) and set(tag) == TAG_KEYS, "invalid_tag_keys", where, loc)
        _need(isinstance(tag["name"], str), "invalid_tag_metadata", where, loc + ".name")
        _need(_is_int(tag["from"]) and _is_int(tag["to"]) and 1 <= tag["from"] <= tag["to"] <= n_frames,
              "invalid_tag_range", where, loc)
        _need(isinstance(tag["color"], str) and (HEX6.match(tag["color"]) or HEX8.match(tag["color"])),
              "unsupported_tag_color", where, loc + ".color")
    for k, n in (("current_frame", n_frames), ("current_layer", n_layers)):
        _need(_is_int(doc[k]) and 0 <= doc[k] < n, "invalid_selection", where, k)

    # ZIP entry grammar: only the derived frame/layer cells are accepted.
    cel_bytes = w * h * 4
    for name in entries:
        if name in ("mimetype", "data.json", "preview.png"):
            continue
        m = ENTRY_RE.match(name)
        _need(m and m.group(2), "unexpected_zip_entry", where)
        _need(int(m.group(1)) <= n_frames and int(m.group(3)) <= n_layers,
              "zip_entry_outside_frame_layer_range", where)
    for name in dirs:
        m = ENTRY_RE.match(name)
        _need(name in ("image_data/", "image_data/frames/")
              or (m and not m.group(2) and int(m.group(1)) <= n_frames),
              "unexpected_zip_entry", where)
    for f in range(1, n_frames + 1):
        for l in range(1, n_layers + 1):
            key = "image_data/frames/%d/layer_%d" % (f, l)
            _need(key in entries, "missing_cel_payload", where, "frame %d layer %d" % (f, l))
            _need(len(entries[key]) == cel_bytes, "cel_payload_size_invalid", where,
                  "frame %d layer %d" % (f, l))
    return n_frames, n_layers


def _strict_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_strict_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_strict_equal(x, y) for x, y in zip(a, b))
    return a == b


def _diff(a, b, loc, out, opaque_ok=True):
    """Collect difference locations (never values, never free-form key names)."""
    if _strict_equal(a, b):
        return
    leaf = loc.rsplit(".", 1)[-1].split("[", 1)[0]
    if type(a) is not type(b) or not isinstance(a, (dict, list)) or (opaque_ok and leaf in OPAQUE_FIELDS):
        out.append(loc)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append(loc + " (length)")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(x, y, "%s[%d]" % (loc, i), out)
        return
    if a.keys() != b.keys():
        out.append(loc + " (key set)")
    for k in sorted(set(a) & set(b)):
        _diff(a[k], b[k], (loc + "." + k) if loc else k, out)


def _compare(src_doc, sav_doc):
    diffs, allowed, normalized = [], [], []
    src = dict(src_doc)
    sav = dict(sav_doc)
    for k in ALLOWED_TOP_DIFF:
        if not _strict_equal(src[k], sav[k]):
            allowed.append(k)
        src.pop(k)
        sav.pop(k)
    sep, vep = dict(src.pop("export_profile")), dict(sav.pop("export_profile"))
    for k in ALLOWED_EXPORT_DIFF:
        if sep[k] != vep[k]:
            allowed.append("export_profile." + k)
        sep.pop(k)
        vep.pop(k)
    # export_profile keys are input-controlled strings: report a fixed location only.
    if sep.keys() != vep.keys():
        diffs.append("export_profile (key set)")
    if any(not _strict_equal(sep[k], vep[k]) for k in set(sep) & set(vep)):
        diffs.append("export_profile (non-SaveAs field value)")
    stags, vtags = src.pop("tags"), sav.pop("tags")
    if len(stags) != len(vtags):
        diffs.append("tags (length)")
    else:
        for i, (st, vt) in enumerate(zip(stags, vtags)):
            st, vt = dict(st), dict(vt)
            sc, vc = st.pop("color"), vt.pop("color")
            if sc != vc:
                if HEX6.match(sc) and HEX8.match(vc) and vc.lower() == sc.lower() + "ff":
                    normalized.append("tags[%d].color" % i)
                else:
                    diffs.append("tags[%d].color" % i)
            _diff(st, vt, "tags[%d]" % i, diffs)
    _diff(src, sav, "", diffs)
    return diffs, allowed, normalized


def _side_summary(blob, entries, dirs, n_entries, preview):
    return {
        "sha256": _sha(blob),
        "bytes": len(blob),
        "zip_entries": n_entries,
        "zip_directory_entries": len(dirs),
        "zip_payload_entries": len(entries),
        "data_json_sha256": _sha(entries["data.json"]),
        "preview_png_sha256": _sha(entries["preview.png"]),
        "preview_png_size": preview,
    }


def run(argv):
    parser = _Parser(add_help=False)
    parser.add_argument("--source", required=True)
    parser.add_argument("--saved", required=True)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    if args.report is not None and not os.path.isabs(args.report):
        raise CheckError("path_not_absolute", "report")

    sides = {}
    for where, raw in (("source", args.source), ("saved", args.saved)):
        blob = _read_input(raw, where)
        entries, dirs, n_entries = _load_zip(blob, where)
        for req in ("mimetype", "data.json", "preview.png"):
            _need(req in entries, "missing_required_entry", where, req)
        _need(entries["mimetype"] == b"application/x-pixelorama", "not_a_pixelorama_project", where)
        try:
            text = entries["data.json"].decode("utf-8")
            doc = json.loads(text, object_pairs_hook=_no_dup_pairs, parse_constant=_bad_constant)
        except CheckError as e:
            raise CheckError(e.code, where)
        except Exception:
            raise CheckError("data_json_malformed", where)
        shape = _validate(doc, entries, dirs, where)
        preview = _check_png(entries["preview.png"], where)
        sides[where] = (blob, entries, dirs, n_entries, doc, shape, preview)

    sb, se, sd, sn, sdoc, (sf, sl), sp = sides["source"]
    vb, ve, vd, vn, vdoc, (vf, vl), vp = sides["saved"]
    differences = []
    if (sf, sl) != (vf, vl):
        differences.append("frame/layer count")
    if sd != vd or set(se) != set(ve):
        differences.append("zip path set")

    cells_compared = cells_equal = idx_compared = idx_equal = 0
    cell_mismatch = []
    for f in range(1, min(sf, vf) + 1):
        for l in range(1, min(sl, vl) + 1):
            key = "image_data/frames/%d/layer_%d" % (f, l)
            cells_compared += 1
            if se[key] == ve[key]:
                cells_equal += 1
            else:
                cell_mismatch.append("frame %d layer %d raw cel" % (f, l))
            ikey = "image_data/frames/%d/indices_layer_%d" % (f, l)
            if ikey in se and ikey in ve:
                idx_compared += 1
                if se[ikey] == ve[ikey]:
                    idx_equal += 1
                else:
                    cell_mismatch.append("frame %d layer %d index payload" % (f, l))
    other_compared = other_equal = 0
    for name in sorted(set(se) & set(ve)):
        if name in ("data.json", "preview.png") or name.startswith("image_data/"):
            continue
        other_compared += 1
        if se[name] == ve[name]:
            other_equal += 1
        else:
            differences.append("zip payload " + name)  # fixed-grammar names only
    differences.extend(cell_mismatch)

    sem_diffs, allowed, normalized = _compare(sdoc, vdoc)
    differences.extend("data.json " + d for d in sem_diffs)

    durations = {}
    for fr in sdoc["frames"]:
        key = repr(fr["duration"])
        durations[key] = durations.get(key, 0) + 1
    passed = not differences
    report = {
        "tool": TOOL,
        "version": VERSION,
        "result": "PASS" if passed else "FAIL",
        "exit_code": 0 if passed else 1,
        "source": _side_summary(sb, se, sd, sn, sp),
        "saved": _side_summary(vb, ve, vd, vn, vp),
        "derived_shape": {
            "frames": sf, "layers": sl, "width": sdoc["size_x"], "height": sdoc["size_y"],
            "fps": sdoc["fps"], "frame_duration_histogram": durations,
            "hidden_layers": sum(1 for x in sdoc["layers"] if not x["visible"]),
            "locked_layers": sum(1 for x in sdoc["layers"] if x["locked"]),
            "tags": len(sdoc["tags"]),
        },
        "comparison": {
            "raw_cels_compared": cells_compared,
            "raw_cels_byte_equal": cells_equal,
            "index_payloads_compared": idx_compared,
            "index_payloads_byte_equal": idx_equal,
            "other_payloads_compared": other_compared,
            "other_payloads_byte_equal": other_equal,
            "zip_path_sets_equal": sd == vd and set(se) == set(ve),
            "data_json_semantic_differences": len(sem_diffs),
            "allowed_differences_observed": allowed,
            "normalizations_applied": [n + ": opaque RGB6 hex == RGBA8 hex with ff alpha"
                                       for n in normalized],
            "preview_png_bytes_equal": se["preview.png"] == ve["preview.png"],
        },
        "differences_total": len(differences),
        "differences": differences[:MAX_LOCATIONS],
        "proof_scope": [
            "every raw image_data/frames/<f>/layer_<l> payload byte-compared for all derived frames x layers",
            "every indices_layer payload, mimetype and the full ZIP path set (incl. directories) compared exactly",
            "all data.json fields compared type-strictly (layer visible/locked/props, frame durations, cel metadata, fps, size, tags, author/license/user_data, export profile, version, palettes, guides, metadata)",
            "allowed only: current_frame, current_layer, export_profile.directory_path, export_profile.file_name, tag colour RGB6->RGBA8 'ff'",
            "author/license/user_data fields compared silently; values never output",
        ],
        "excluded_from_proof": [
            "preview.png thumbnail content (UI-derived; structurally validated as PNG only)",
            "ZIP container bytes, compression and entry order (payloads are compared instead)",
        ],
        "non_claims": [
            "file-integrity check only: no claim about GUI behaviour, clean app state, rendering or art approval",
        ],
    }
    return report


def _emit(obj, report_path):
    text = json.dumps(obj, indent=2, sort_keys=False) + "\n"
    if report_path:
        try:
            with open(_extended(report_path), "x", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        except FileExistsError:
            return _emit(_error(CheckError("report_already_exists", "report")), None)
        except OSError:
            return _emit(_error(CheckError("report_unwritable", "report")), None)
    sys.stdout.buffer.write(text.encode("utf-8"))  # LF bytes, identical to the report
    sys.stdout.flush()
    return obj["exit_code"]


def _error(err):
    return {"tool": TOOL, "version": VERSION, "result": "ERROR", "exit_code": 2,
            "errors": [err.as_dict()],
            "non_claims": ["no file-integrity, GUI or art claim is made when the check errors"]}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    report_path = None
    try:
        if "--report" in argv:
            i = argv.index("--report")
            if i + 1 < len(argv) and os.path.isabs(argv[i + 1]):
                report_path = argv[i + 1]
        obj = run(argv)
    except CheckError as e:
        obj = _error(e)
    except RecursionError:
        obj = _error(CheckError("data_json_too_deep"))
    except BaseException:  # never leak exception text
        obj = _error(CheckError("internal_error"))
    try:
        return _emit(obj, report_path)
    except BaseException:
        return 2


if __name__ == "__main__":
    sys.exit(main())
