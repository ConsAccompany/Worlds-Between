#!/usr/bin/env python3
"""Bounded builder: existing v2 sentry pixels -> editable native PXO + manifest.

Source is the existing, read-only v2 21-frame sentry animation
(manifest ffefdc6f, 112x62 cells, runtime anchor 46,60).  The builder does not
draw, re-pose, resample, recolour or retime the art.  It classifies every opaque
source pixel by the v2 author's own Part paint order (interior or 1 px outline),
groups those Parts into six disjoint paint roles, and verifies that the role
composite is byte-identical to each source frame.

Only the bundled Python/Pillow and the existing native-format helper are used.
The source is opened read-only through a Windows extended-length prefix.  This
script builds all artefacts and checks them in memory; with --dry-run it writes
nothing.  A non-dry-run invocation writes exactly one package revision.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image

sys.dont_write_bytecode = True

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "sentry"
PURPOSE = "editable-native"
VARIANT = "v01"
PACKAGE_DIRNAME = "sentry-editable-v01"
SOURCE_DIR_REL = "game/assets/enemies/sentry-automaton-pilot-0b9664e2"
V2_MANIFEST_NAME = (
    "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-"
    "manifest_m8-anim-v02_20261014-230329-ffefdc6f.json"
)
HELPER_NAME = (
    "rpg-2-star-ocean-the-second_benchmark_native-format-helper_v01_"
    "20261018-234437-8dfccbf6.py"
)
W, H = 112, 62
FRAME_COUNT = 21
FPS = 12
PIVOT = [46, 60]
ANCHOR_ROW = 60
BODY_CENTER_X = 64
STATIC_PLATE_OFFSET = [16, 0]
PXO_DT = (2026, 10, 19, 0, 0, 0)

# Bottom-to-top editorial order.  The layers are disjoint, so this order is
# stable for editing and does not affect the exact composite.
LAYERS = ["legs", "mechanisms", "body", "claw", "eye", "impact"]
ROLE_BY_PART = {
    "far_rear_leg": "legs",
    "far_front_leg": "legs",
    "near_rear_leg": "legs",
    "near_front_leg": "claw",
    "belly": "mechanisms",
    "dome": "mechanisms",
    "shell": "body",
    "far_fin": "body",
    "cheek_plate": "body",
    "eye_housing": "eye",
    "eye": "eye",
    "fx": "impact",
}
ROLE_SOURCE_PARTS = {
    "legs": ["far_rear_leg", "far_front_leg", "near_rear_leg"],
    "mechanisms": ["belly", "dome"],
    "body": ["shell", "far_fin", "cheek_plate"],
    "claw": ["near_front_leg"],
    "eye": ["eye_housing", "eye"],
    "impact": [],
}
ROLE_NOTES = {
    "legs": "The three non-strike legs; existing far/near slate, brass hip/knee and toe-capped foot paints.",
    "mechanisms": "The underslung ribbed drive housing/gear and top sensor dome; existing mechanism paints.",
    "body": "The main carapace, far visor fin and near cheek plate; existing slate/brass body paint.",
    "claw": "The near-front strike limb the v2 author raises and stamps as the claw, including thigh, shin, knee and foot.",
    "eye": "The octagonal eye housing and large cyan lens, including the existing lens-state paints.",
    "impact": "Only the v2 author's explicit fx spark pixels, applied after the Part composite; no new effect is created.",
}
EXPECTED_PARTS = [
    "far_rear_leg",
    "far_front_leg",
    "belly",
    "shell",
    "dome",
    "far_fin",
    "near_rear_leg",
    "near_front_leg",
    "eye_housing",
    "eye",
    "cheek_plate",
]
TAG_COLORS = {
    "idle": "188a92",
    "move": "4c5562",
    "windup": "cbb077",
    "strike": "c6fff6",
    "hit": "806439",
    "defeat": "4b3627",
}
STATE_TIMING_SOURCE = {
    "idle": "source states.idle.frameTime 0.22 s (the source gif sequence also uses 220 ms)",
    "move": "source states.move is distance-driven (one frame per 4 px step); the PXO linearizes at 59 ms/step from previews.loopGif3x.sequence without retiming the 4 px step",
    "windup": "source states.windup is progress-driven; the PXO linearizes at 240 ms/frame from previews.loopGif3x.sequence",
    "strike": "source states.strike.frameTime 0.15 s",
    "hit": "source states.hit.frameTime 0.12 s",
    "defeat": "source states.defeat.frameTime 0.16 s with hold-last; the hold is runtime behavior and no 22nd frame is added",
}
REP_FRAMES = {"idle": 0, "move": 4, "windup": 12, "strike": 14, "hit": 16, "defeat": 20}
SHADOW_BOUNDARY = (
    "The v2 author geometry, palette and all 21 v2 frames contain no contact-shadow "
    "part or shadow-coloured pixels; the only ground contact is the opaque near-foot "
    "sole row at y=60. Adding a shadow layer would add new art, so this package does "
    "not invent one. The sixth role is impact, made only from the v2 author's existing "
    "explicit fx spark pixels."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ext_path(path: os.PathLike | str) -> str:
    """Windows extended-length prefix for reads and writes, including long paths."""
    text = os.path.abspath(os.fspath(path))
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        text = "\\\\?\\" + text
    return text


def read_bytes(path: os.PathLike | str) -> bytes:
    with open(ext_path(path), "rb") as handle:
        return handle.read()


def write_bytes(path: os.PathLike | str, data: bytes) -> None:
    with open(ext_path(path), "wb") as handle:
        handle.write(data)


def path_exists(path: os.PathLike | str) -> bool:
    return os.path.exists(ext_path(path))


def makedirs(path: os.PathLike | str) -> None:
    os.makedirs(ext_path(path), exist_ok=True)


def sha256_text_lf(path: os.PathLike | str) -> str:
    text = read_bytes(path).decode("utf-8")
    return sha256_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def load_module(name: str, path: os.PathLike | str):
    spec = importlib.util.spec_from_file_location(name, ext_path(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def flat(image: Image.Image):
    return image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()


def default_root(here: Path) -> Path:
    candidates = []
    for depth in (6, 3):
        try:
            candidates.append(here.parents[depth])
        except IndexError:
            pass
    for candidate in candidates:
        if path_exists(candidate / SOURCE_DIR_REL / V2_MANIFEST_NAME):
            return candidate
    raise SystemExit(
        "cannot locate the project root; pass --source-root with the checkout that "
        f"contains {SOURCE_DIR_REL}/{V2_MANIFEST_NAME}"
    )


def parse_build_identity(script_name: str) -> tuple[str, str]:
    match = re.search(r"_(\d{8}-\d{6})-([0-9a-f]{8})\.py$", script_name)
    if not match:
        raise SystemExit(
            "builder filename must end with _ACTUALUTCtimestamp-8hexid.py "
            "(lowercase 8 hex), e.g. ..._20261019-215808-765b18c6.py"
        )
    return match.group(1), match.group(2)


def observed_state_seconds(manifest: dict) -> tuple[dict, dict]:
    observed: dict[str, list[tuple[int, int]]] = {}
    for state, index, milliseconds, _dx in manifest["previews"]["loopGif3x"]["sequence"]:
        observed.setdefault(state, []).append((int(index), int(milliseconds)))
    seconds = {}
    for state, spec in manifest["states"].items():
        if spec.get("frameTime") is not None:
            value = float(spec["frameTime"])
            for index, milliseconds in observed.get(state, []):
                if state == "defeat" and index == 20 and milliseconds == 900:
                    continue  # review-only hold-last duplicate, not a source frame
                if abs(milliseconds / 1000.0 - value) > 1e-9:
                    raise RuntimeError(f"{state}: gif time {milliseconds} ms != frameTime {value}s")
        else:
            entries = observed.get(state, [])
            if not entries:
                raise RuntimeError(f"{state}: no source preview timing")
            value = entries[0][1] / 1000.0
            for index, milliseconds in entries:
                if abs(milliseconds / 1000.0 - value) > 1e-9:
                    raise RuntimeError(f"{state}: inconsistent gif times {entries}")
        seconds[state] = value
    return seconds, observed


def patch_pxo(raw: bytes, tags: list, user_data: str) -> bytes:
    """Add native tags and a self-describing user_data string without re-encoding cels."""
    with zipfile.ZipFile(io.BytesIO(raw), "r") as source:
        data = json.loads(source.read("data.json"))
        data["tags"] = tags
        data["user_data"] = user_data
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
            for info in source.infolist():
                payload = source.read(info.filename)
                if info.filename == "data.json":
                    payload = json.dumps(data, separators=(",", ":")).encode("utf-8")
                entry = zipfile.ZipInfo(info.filename, PXO_DT)
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = info.external_attr
                entry.internal_attr = info.internal_attr
                entry.create_system = info.create_system
                target.writestr(entry, payload)
    return output.getvalue()


def check_pxo(
    raw: bytes,
    frames: list[dict[str, Image.Image]],
    composites: list[Image.Image],
    source_images: list[Image.Image],
    tags: list,
    native_durations: list[float],
) -> dict:
    with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError("PXO zip CRC failed")
        data = json.loads(archive.read("data.json"))
        expected_entries = 3 + FRAME_COUNT + FRAME_COUNT * len(LAYERS) * 2
        if len(archive.namelist()) != expected_entries:
            raise RuntimeError(
                f"PXO entry count {len(archive.namelist())} != {expected_entries}"
            )
        checks = {
            "size": (data["size_x"], data["size_y"]),
            "fps": data["fps"],
            "pxoVersion": data["pxo_version"],
            "colorMode": data["color_mode"],
            "frameCount": len(data["frames"]),
            "layers": [layer["name"] for layer in data["layers"]],
            "tags": data["tags"],
        }
        if checks["size"] != (W, H):
            raise RuntimeError(f"PXO size {checks['size']} != {(W, H)}")
        if checks["fps"] != FPS or checks["pxoVersion"] != 7 or checks["colorMode"] != 5:
            raise RuntimeError(f"PXO native header mismatch: {checks}")
        if checks["frameCount"] != FRAME_COUNT or checks["layers"] != LAYERS:
            raise RuntimeError(f"PXO frame/layer mismatch: {checks}")
        if checks["tags"] != tags:
            raise RuntimeError("PXO tags do not match the source state map")
        if json.loads(data["user_data"])["pivot"] != PIVOT:
            raise RuntimeError("PXO user_data pivot mismatch")
        preview = Image.open(io.BytesIO(archive.read("preview.png"))).convert("RGBA")
        if preview.tobytes() != composites[0].tobytes():
            raise RuntimeError("PXO preview is not the frame-0 composite")
        for index in range(FRAME_COUNT):
            frame = data["frames"][index]
            if len(frame["cels"]) != len(LAYERS):
                raise RuntimeError(f"frame {index}: cel count mismatch")
            if abs(float(frame["duration"]) - native_durations[index]) > 1e-12:
                raise RuntimeError(f"frame {index}: duration mismatch")
            composite = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for layer_index, role in enumerate(LAYERS, start=1):
                raw_cel = archive.read(f"image_data/frames/{index + 1}/layer_{layer_index}")
                if len(raw_cel) != W * H * 4:
                    raise RuntimeError(f"frame {index}/{role}: raw cel size mismatch")
                cel = Image.frombytes("RGBA", (W, H), raw_cel)
                if cel.tobytes() != frames[index][role].tobytes():
                    raise RuntimeError(f"frame {index}/{role}: raw cel content mismatch")
                if not archive.read(
                    f"image_data/frames/{index + 1}/indices_layer_{layer_index}"
                ):
                    raise RuntimeError(f"frame {index}/{role}: missing indices marker")
                composite = Image.alpha_composite(composite, cel)
            if composite.tobytes() != source_images[index].tobytes():
                raise RuntimeError(f"frame {index}: PXO composite != source")
    return checks


def check_ora(
    raw: bytes,
    frame_layers: dict[str, Image.Image],
    source_image: Image.Image,
    state: str,
    index: int,
) -> None:
    with zipfile.ZipFile(io.BytesIO(raw), "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"ORA {state} zip CRC failed")
        if archive.read("mimetype") != b"image/openraster":
            raise RuntimeError(f"ORA {state}: mimetype mismatch")
        root = ET.fromstring(archive.read("stack.xml"))
        layers = root.findall(".//layer")
        if len(layers) != len(LAYERS) or {el.get("name") for el in layers} != set(LAYERS):
            raise RuntimeError(f"ORA {state}: stack layer mismatch")
        for element in layers:
            name = element.get("name")
            src = element.get("src")
            image = Image.open(io.BytesIO(archive.read(src))).convert("RGBA")
            if image.tobytes() != frame_layers[name].tobytes():
                raise RuntimeError(f"ORA {state}/{name}: layer pixels differ")
        merged = Image.open(io.BytesIO(archive.read("mergedimage.png"))).convert("RGBA")
        if merged.tobytes() != source_image.tobytes():
            raise RuntimeError(f"ORA {state}: merged image != source frame {index}")
        expected_entries = 2 + len(LAYERS) + 1
        if len(archive.namelist()) != expected_entries:
            raise RuntimeError(f"ORA {state}: entry count mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--helper", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    builder_path = Path(__file__).resolve()
    builder_bytes = read_bytes(builder_path)
    builder_sha = sha256_bytes(builder_bytes)
    stamp, run_id = parse_build_identity(builder_path.name)
    package_id = f"{stamp}-{run_id}"
    prefix = f"{PROJECT}_{SUBJECT}_{PURPOSE}_{VARIANT}_{package_id}"

    root = (args.source_root.resolve() if args.source_root else default_root(here))
    helper_path = (
        args.helper.resolve()
        if args.helper
        else here.parents[1] / "inputs" / HELPER_NAME
    )
    out_dir = args.out.resolve() if args.out else here

    manifest_path = root / SOURCE_DIR_REL / V2_MANIFEST_NAME
    if not path_exists(manifest_path):
        raise SystemExit(f"source manifest missing: {manifest_path}")
    manifest_bytes = read_bytes(manifest_path)
    manifest_sha = sha256_bytes(manifest_bytes)
    source_manifest = json.loads(manifest_bytes.decode("utf-8"))

    if source_manifest.get("project") != PROJECT:
        raise RuntimeError("source project mismatch")
    if source_manifest.get("revision") != "m8-anim-v02":
        raise RuntimeError("source revision is not the existing v2")
    if source_manifest.get("frameCount") != FRAME_COUNT:
        raise RuntimeError("source frame count is not 21")
    if list(source_manifest.get("cellSize", [])) != [W, H]:
        raise RuntimeError("source cell size is not 112x62")
    if list(source_manifest.get("runtimeAnchor", [])) != PIVOT:
        raise RuntimeError("source anchor is not 46,60")
    if list(source_manifest.get("staticPlateOffsetInCell", [])) != STATIC_PLATE_OFFSET:
        raise RuntimeError("source static plate offset changed")

    if not path_exists(helper_path):
        raise SystemExit(f"native helper missing: {helper_path}")
    helper_bytes = read_bytes(helper_path)
    helper_sha = sha256_bytes(helper_bytes)
    helper = load_module("sentry_native_format_helper", helper_path)
    helper.W, helper.H = W, H

    strip_bytes = read_bytes(root / source_manifest["file"])
    if sha256_bytes(strip_bytes) != source_manifest["sha256"]:
        raise RuntimeError("source strip hash mismatch")
    source_strip = Image.open(io.BytesIO(strip_bytes)).convert("RGBA")
    if source_strip.size != (W * FRAME_COUNT, H):
        raise RuntimeError("source strip size mismatch")

    source_images: list[Image.Image] = []
    frame_files = []
    for index, entry in enumerate(source_manifest["frameFiles"]):
        if int(entry["index"]) != index:
            raise RuntimeError("source frame index order mismatch")
        raw = read_bytes(root / entry["file"])
        if sha256_bytes(raw) != entry["sha256"]:
            raise RuntimeError(f"source frame {index} hash mismatch")
        image = Image.open(io.BytesIO(raw)).convert("RGBA")
        if image.size != (W, H):
            raise RuntimeError(f"source frame {index} size mismatch")
        if set(flat(image.getchannel("A"))) - {0, 255}:
            raise RuntimeError(f"source frame {index} is not binary alpha")
        for pixel in flat(image):
            if pixel[3] == 0 and pixel[:3] != (0, 0, 0):
                raise RuntimeError(f"source frame {index} has non-zero RGB under alpha 0")
        if image.tobytes() != source_strip.crop(
            (index * W, 0, (index + 1) * W, H)
        ).tobytes():
            raise RuntimeError(f"source strip cell {index} != frame PNG {index}")
        source_images.append(image)
        frame_files.append(
            {
                "index": index,
                "state": entry["state"],
                "path": entry["file"],
                "sha256": entry["sha256"],
                "rgbaSha256": sha256_bytes(image.tobytes()),
                "size": [W, H],
            }
        )

    static_path = root / source_manifest["staticPilot"]["file"]
    static_bytes = read_bytes(static_path)
    if sha256_bytes(static_bytes) != source_manifest["staticPilot"]["sha256"]:
        raise RuntimeError("static pilot hash mismatch")
    static_image = Image.open(io.BytesIO(static_bytes)).convert("RGBA")
    if source_images[0].crop((16, 0, 16 + 96, H)).tobytes() != static_image.tobytes():
        raise RuntimeError("neutral idle frame no longer equals the static pilot")

    author_path = root / source_manifest["authorScript"]
    author_bytes = read_bytes(author_path)
    author_sha = sha256_bytes(author_bytes)
    author_lf = sha256_text_lf(author_path)
    if author_lf != source_manifest["authorScriptSha256"]:
        raise RuntimeError("v2 author script text-lf hash mismatch")
    author = load_module("sentry_v2_source_author", author_path)
    if (author.W, author.H) != (W, H) or tuple(author.RUNTIME_ANCHOR) != tuple(PIVOT):
        raise RuntimeError("v2 author geometry constants mismatch")
    if len(author.FRAMES) != FRAME_COUNT:
        raise RuntimeError("v2 author frame count mismatch")

    static_author_path = root / source_manifest["staticAuthorScript"]
    static_author_bytes = read_bytes(static_author_path)
    static_author_sha = sha256_bytes(static_author_bytes)
    static_author_lf = sha256_text_lf(static_author_path)
    if static_author_lf != source_manifest["staticAuthorScriptSha256"]:
        raise RuntimeError("static author script text-lf hash mismatch")

    state_frame_list = []
    for state, spec in source_manifest["states"].items():
        state_frame_list.extend((int(index), state) for index in spec["frames"])
    state_frame_list.sort()
    if [state for _, state in state_frame_list] != [state for state, _pose in author.FRAMES]:
        raise RuntimeError("v2 author frame order != source manifest state order")
    if [index for index, _state in state_frame_list] != list(range(FRAME_COUNT)):
        raise RuntimeError("source state frames are not exactly 0..20")

    state_seconds, observed_times = observed_state_seconds(source_manifest)
    native_durations = []
    for state, _pose in author.FRAMES:
        value = round(state_seconds[state] * FPS, 6)
        if abs(value / FPS - state_seconds[state]) > 1e-9:
            raise RuntimeError(f"{state}: native duration rounding drift")
        native_durations.append(value)

    frames: list[dict[str, Image.Image]] = []
    composites: list[Image.Image] = []
    frame_cels = []
    role_pixel_totals = {role: 0 for role in LAYERS}
    role_bbox_union = {role: None for role in LAYERS}
    role_frames_present = {role: 0 for role in LAYERS}

    for index, (state, pose) in enumerate(author.FRAMES):
        source = source_images[index]
        rendered = author.render(pose).convert("RGBA")
        if rendered.tobytes() != source.tobytes():
            raise RuntimeError(f"v2 author render {index} != existing source pixels")
        parts = author.build_parts(pose)
        if [part.name for part in parts] != EXPECTED_PARTS:
            raise RuntimeError(f"frame {index}: v2 author Part order changed")

        owner: dict[tuple[int, int], str] = {}
        for part in parts:
            layer = part.layer.load()
            inside = {
                (x, y)
                for y in range(H)
                for x in range(W)
                if layer[x, y]
            }
            for x, y in inside:
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in inside:
                        owner[(nx, ny)] = part.name
            for key in inside:
                owner[key] = part.name
        for x, y, _key in pose["fx"]:
            owner[(x + author.MARGIN, y)] = "fx"
        unknown = [part for part in {value for value in owner.values()} if part not in ROLE_BY_PART]
        if unknown:
            raise RuntimeError(f"frame {index}: unmapped Part(s) {unknown}")

        role_images = {role: Image.new("RGBA", (W, H), (0, 0, 0, 0)) for role in LAYERS}
        role_pixels = {role: role_images[role].load() for role in LAYERS}
        for y in range(H):
            for x in range(W):
                pixel = source.getpixel((x, y))
                if pixel[3] == 0:
                    if (x, y) in owner:
                        raise RuntimeError(f"frame {index}: authored pixel missing at {x},{y}")
                    continue
                part_name = owner.get((x, y))
                if part_name is None:
                    raise RuntimeError(f"frame {index}: source pixel unowned at {x},{y}")
                role_pixels[ROLE_BY_PART[part_name]][x, y] = pixel

        composite = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for role in LAYERS:
            composite = Image.alpha_composite(composite, role_images[role])
        if composite.tobytes() != source.tobytes():
            raise RuntimeError(f"frame {index}: role composite != source pixels")
        if composite.tobytes() != rendered.tobytes():
            raise RuntimeError(f"frame {index}: role composite != author render")

        source_opaque = sum(1 for pixel in flat(source) if pixel[3])
        total_opaque = 0
        present_pixels = set()
        for role in LAYERS:
            alpha = role_images[role].getchannel("A")
            counts = list(flat(alpha))
            if set(counts) - {0, 255}:
                raise RuntimeError(f"frame {index}/{role}: non-binary alpha")
            count = sum(1 for value in counts if value)
            total_opaque += count
            bbox = role_images[role].getbbox()
            bbox_inclusive = [] if bbox is None else [bbox[0], bbox[1], bbox[2] - 1, bbox[3] - 1]
            if count:
                role_frames_present[role] += 1
                if role_bbox_union[role] is None:
                    role_bbox_union[role] = list(bbox_inclusive)
                else:
                    union = role_bbox_union[role]
                    union[0] = min(union[0], bbox_inclusive[0])
                    union[1] = min(union[1], bbox_inclusive[1])
                    union[2] = max(union[2], bbox_inclusive[2])
                    union[3] = max(union[3], bbox_inclusive[3])
                for y in range(H):
                    for x in range(W):
                        if alpha.getpixel((x, y)):
                            key = (x, y)
                            if key in present_pixels:
                                raise RuntimeError(f"frame {index}: role overlap at {x},{y}")
                            present_pixels.add(key)
            role_pixel_totals[role] += count
        if total_opaque != source_opaque or len(present_pixels) != source_opaque:
            raise RuntimeError(f"frame {index}: roles are not disjoint")
        if role_images["legs"].tobytes() == source.tobytes():
            raise RuntimeError(f"frame {index}: legs layer duplicates the flattened frame")
        if len({role_images[role].tobytes() for role in LAYERS}) != len(LAYERS):
            raise RuntimeError(f"frame {index}: duplicate role layer content")

        frames.append(role_images)
        composites.append(composite)
        frame_cels.append(
            {
                "frame": index,
                "state": state,
                "compositeRgbaSha256": sha256_bytes(source.tobytes()),
                "cels": {
                    role: {
                        "rgbaSha256": sha256_bytes(role_images[role].tobytes()),
                        "opaquePixels": sum(
                            1 for pixel in flat(role_images[role].getchannel("A")) if pixel
                        ),
                        "bboxInclusive": (
                            []
                            if role_images[role].getbbox() is None
                            else [
                                role_images[role].getbbox()[0],
                                role_images[role].getbbox()[1],
                                role_images[role].getbbox()[2] - 1,
                                role_images[role].getbbox()[3] - 1,
                            ]
                        ),
                    }
                    for role in LAYERS
                },
            }
        )

    tags = [
        {
            "name": state,
            "from": min(source_manifest["states"][state]["frames"]) + 1,
            "to": max(source_manifest["states"][state]["frames"]) + 1,
            "color": TAG_COLORS[state],
        }
        for state in source_manifest["states"]
    ]
    for tag in tags:
        if not (1 <= tag["from"] <= tag["to"] <= FRAME_COUNT):
            raise RuntimeError(f"bad tag range: {tag}")

    user_data = json.dumps(
        {
            "package": package_id,
            "pivot": PIVOT,
            "anchorRow": ANCHOR_ROW,
            "bodyCenterX": BODY_CENTER_X,
            "roles": LAYERS,
            "fps": FPS,
            "durationSemantics": "frames[].duration is a multiplier of 1/fps",
            "sourceManifestSha256": manifest_sha,
            "sourceStripSha256": source_manifest["sha256"],
            "noNewPixels": True,
            "noV1OrV3Mix": True,
        },
        separators=(",", ":"),
    )

    pxo_name = f"{prefix}.pxo"
    preview_png = png_bytes(composites[0])
    raw_pxo = helper.make_pxo(
        frames,
        native_durations,
        preview_png,
        pxo_name,
        FPS,
        order=LAYERS,
        dt=PXO_DT,
    )
    pxo_bytes = patch_pxo(raw_pxo, tags, user_data)
    pxo_check = check_pxo(
        pxo_bytes, frames, composites, source_images, tags, native_durations
    )

    strip = Image.new("RGBA", (W * FRAME_COUNT, H), (0, 0, 0, 0))
    for index, composite in enumerate(composites):
        strip.paste(composite, (index * W, 0))
    if strip.tobytes() != source_strip.tobytes():
        raise RuntimeError("composite strip pixels != source strip")
    for index in range(FRAME_COUNT):
        if strip.crop((index * W, 0, (index + 1) * W, H)).tobytes() != source_images[index].tobytes():
            raise RuntimeError(f"composite strip cell {index} != source frame")
    strip_bytes_out = png_bytes(strip)
    strip_byte_identical = strip_bytes_out == strip_bytes
    strip_name = f"{PROJECT}_{SUBJECT}_{PURPOSE}-strip_{VARIANT}_{package_id}.png"

    ora_names = []
    ora_bytes_map = {}
    for state, index in REP_FRAMES.items():
        if index not in source_manifest["states"][state]["frames"]:
            raise RuntimeError(f"representative frame {index} not in state {state}")
        ora_name = (
            f"{PROJECT}_{SUBJECT}_{PURPOSE}-{state}-representative_{VARIANT}_{package_id}.ora"
        )
        ora_bytes = helper.ora_bytes(frames[index])
        check_ora(ora_bytes, frames[index], source_images[index], state, index)
        ora_names.append((state, index, ora_name))
        ora_bytes_map[ora_name] = ora_bytes

    states_out = {}
    for state, spec in source_manifest["states"].items():
        entry = {
            "frames": list(spec["frames"]),
            "frameTime": spec.get("frameTime"),
            "mode": spec["mode"],
            "purposeDurationSeconds": state_seconds[state],
            "nativeDuration": round(state_seconds[state] * FPS, 6),
            "timingSource": STATE_TIMING_SOURCE[state],
        }
        if spec.get("stepPx") is not None:
            entry["stepPx"] = spec["stepPx"]
        states_out[state] = entry

    timeline = []
    for index, (state, _pose) in enumerate(author.FRAMES):
        state_spec = source_manifest["states"][state]
        timeline.append(
            {
                "frame": index,
                "state": state,
                "stateFrame": list(state_spec["frames"]).index(index),
                "sourceIndex": index,
                "durationSeconds": state_seconds[state],
                "durationNative": native_durations[index],
                "pivot": PIVOT,
                "mode": state_spec["mode"],
                "timingSource": STATE_TIMING_SOURCE[state],
            }
        )

    roles_manifest = []
    for role in LAYERS:
        roles_manifest.append(
            {
                "name": role,
                "sourceParts": ROLE_SOURCE_PARTS[role],
                "pixelCount": role_pixel_totals[role],
                "framesPresent": role_frames_present[role],
                "bboxUnionInclusive": role_bbox_union[role] or [],
                "note": ROLE_NOTES[role],
            }
        )

    artifacts = {
        builder_path.name: builder_sha,
        pxo_name: sha256_bytes(pxo_bytes),
        strip_name: sha256_bytes(strip_bytes_out),
        **{name: sha256_bytes(data) for name, data in ora_bytes_map.items()},
    }
    artifacts = dict(sorted(artifacts.items()))
    manifest_name = f"{PROJECT}_{SUBJECT}_{PURPOSE}-manifest_{VARIANT}_{package_id}.json"

    created = datetime.now(timezone.utc)
    created_iso = created.strftime("%Y-%m-%dT%H:%M:%SZ")
    filename_iso = (
        datetime.strptime(stamp, "%Y%m%d-%H%M%S")
        .replace(tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    manifest = {
        "schemaVersion": 1,
        "project": PROJECT,
        "subject": SUBJECT,
        "purpose": PURPOSE,
        "variant": VARIANT,
        "packageId": package_id,
        "status": "native_editable_unapproved",
        "artAccepted": False,
        "artAcceptanceCount": 0,
        "humanReview": (
            "none - this package proves native editability of the existing v2 pixels; "
            "it makes no art, motion, runtime or GUI reliability claim"
        ),
        "runtimeIntegrated": False,
        "createdAtUtc": created_iso,
        "filenameTimestampUtc": filename_iso,
        "builder": {
            "file": builder_path.name,
            "path": os.path.relpath(builder_path, root).replace("\\", "/"),
            "sha256": builder_sha,
        },
        "helper": {
            "file": helper_path.name,
            "path": os.path.relpath(helper_path, root).replace("\\", "/"),
            "sha256": helper_sha,
        },
        "native": {
            "format": "PXO v7 (Pixelorama 1.2.3 native project)",
            "pxoVersion": 7,
            "pixeloramaVersion": "v1.2.3-stable",
            "colorMode": 5,
            "size": [W, H],
            "frameCount": FRAME_COUNT,
            "layerCount": len(LAYERS),
            "layerOrderBottomToTop": LAYERS,
            "fps": FPS,
            "durationUnit": "multiplier of 1/fps",
            "durationSemantics": "playback seconds = frames[].duration / fps",
            "pivot": PIVOT,
            "anchorRow": ANCHOR_ROW,
            "bodyCenterX": BODY_CENTER_X,
            "tags": tags,
            "allCelsRgba": True,
            "binaryAlpha": True,
            "flattenedLayer": False,
            "previewFrame": 0,
        },
        "source": {
            "manifest": {
                "file": V2_MANIFEST_NAME,
                "path": os.path.relpath(manifest_path, root).replace("\\", "/"),
                "sha256": manifest_sha,
            },
            "strip": {
                "file": os.path.basename(source_manifest["file"]),
                "path": source_manifest["file"],
                "sha256": source_manifest["sha256"],
                "rgbaSha256": sha256_bytes(source_strip.tobytes()),
                "size": [W * FRAME_COUNT, H],
            },
            "staticPilot": {
                "file": os.path.basename(source_manifest["staticPilot"]["file"]),
                "path": source_manifest["staticPilot"]["file"],
                "sha256": source_manifest["staticPilot"]["sha256"],
                "size": list(static_image.size),
            },
            "authorScript": {
                "file": author_path.name,
                "path": source_manifest["authorScript"],
                "sha256Bytes": author_sha,
                "sha256TextLf": author_lf,
                "declaredSha256TextLf": source_manifest["authorScriptSha256"],
                "declaredAlgorithm": source_manifest["authorScriptSha256Algorithm"],
                "matchesDeclared": True,
            },
            "staticAuthorScript": {
                "file": static_author_path.name,
                "path": source_manifest["staticAuthorScript"],
                "sha256Bytes": static_author_sha,
                "sha256TextLf": static_author_lf,
                "declaredSha256TextLf": source_manifest["staticAuthorScriptSha256"],
                "declaredAlgorithm": source_manifest["staticAuthorScriptSha256Algorithm"],
                "matchesDeclared": True,
            },
            "frameFiles": frame_files,
            "frameCount": FRAME_COUNT,
            "cellSize": [W, H],
            "stripSize": [W * FRAME_COUNT, H],
            "neutralFrameEqualsStaticPilot": True,
            "palette": source_manifest.get("palette", {}),
            "stateTimingNote": source_manifest.get("stateTimingNote"),
            "readOnly": True,
            "longPathReadMode": "Windows extended-length prefix (\\\\?\\)",
        },
        "existingIndices": {
            "frameOrder": list(range(FRAME_COUNT)),
            "states": {
                state: {
                    "frames": list(spec["frames"]),
                    "frameTime": spec.get("frameTime"),
                    "mode": spec["mode"],
                    "stepPx": spec.get("stepPx"),
                }
                for state, spec in source_manifest["states"].items()
            },
            "pivot": PIVOT,
            "runtimeAnchor": PIVOT,
            "anchorRow": ANCHOR_ROW,
            "bodyCenterX": BODY_CENTER_X,
            "staticPlateOffsetInCell": STATIC_PLATE_OFFSET,
            "facing": source_manifest.get("facing"),
            "sourceFrameReport": source_manifest.get("frameReport", []),
        },
        "states": states_out,
        "timeline": timeline,
        "roles": roles_manifest,
        "shadow": {
            "present": False,
            "boundary": SHADOW_BOUNDARY,
        },
        "frameCels": frame_cels,
        "compositeCheck": {
            "sourceFrameHashesMatchManifest": True,
            "sourceStripHashMatchesManifest": True,
            "sourceStripCellsEqualFramePngs": True,
            "authorRenderEqualsAll21SourceFrames": True,
            "roleCompositeEqualsAll21SourceFrames": True,
            "roleLayersDisjoint": True,
            "noFlattenedOrDuplicatedLayers": True,
            "compositeStripPixelsEqualSourceStrip": True,
            "compositeStripBytesEqualSourceStrip": strip_byte_identical,
            "neutralFrameEqualsStaticPilot": True,
            "pivot": PIVOT,
            "stripCellOrder": "left-to-right frames 0..20",
            "sourceStripFileSha256": source_manifest["sha256"],
            "compositeStripFileSha256": sha256_bytes(strip_bytes_out),
            "sourceStripRgbaSha256": sha256_bytes(source_strip.tobytes()),
            "compositeStripRgbaSha256": sha256_bytes(strip.tobytes()),
            "all21CellsExact": True,
            "pxoFrameCount": pxo_check["frameCount"],
        },
        "provenance": {
            "source": "existing v2 21-frame strip + 21 frame PNGs + v2 author geometry",
            "method": (
                "Each opaque v2 source pixel is assigned to the topmost v2 author Part "
                "that paints it, including the Part's 1 px interior/outline footprint; "
                "explicit v2 fx pixels are assigned to impact. Parts are grouped into "
                "six disjoint editable paint roles. Role images are copied pixel-for-pixel "
                "from the existing v2 frames; their alpha composite is verified "
                "byte-identical to every source frame and to the existing source strip."
            ),
            "roleDerivation": (
                "body=shell+far_fin+cheek_plate; mechanisms=belly+dome; "
                "legs=three non-strike legs; claw=near_front_leg; "
                "eye=eye_housing+eye; impact=explicit v2 fx pixels"
            ),
            "visibleRasterBoundary": (
                "Roles are derived from the visible v2 raster. Pixels fully hidden by a "
                "later author Part were overwritten in the existing PNGs and cannot be "
                "recovered without inventing geometry or colours, so none are added."
            ),
            "noNewPixels": True,
            "noResampling": True,
            "noRecoloring": True,
            "noV1OrV3Mix": True,
            "v1OrV3FilesRead": [],
            "sourceWrites": 0,
            "v2AuthorImportsStaticPaletteAndCompositor": True,
            "shadowBoundary": SHADOW_BOUNDARY,
            "approval": "none; no art/motion approval; no GUI reliability claim",
            "artAcceptanceCount": 0,
            "runtimeIntegrated": False,
            "guiReliabilityClaimed": False,
        },
        "artifacts": artifacts,
        "package": {
            "directory": os.path.relpath(out_dir, root).replace("\\", "/"),
            "fileCount": 1 + 1 + 1 + len(ora_names) + 1,
            "files": sorted(
                [
                    builder_path.name,
                    pxo_name,
                    strip_name,
                    *ora_bytes_map.keys(),
                    manifest_name,
                ]
            ),
            "oneRevision": True,
        },
    }

    summary = {
        "package": package_id,
        "pxo": pxo_name,
        "pxoSize": len(pxo_bytes),
        "strip": strip_name,
        "stripBytesEqualSource": strip_byte_identical,
        "oras": [name for _state, _index, name in ora_names],
        "roles": [
            {"name": role["name"], "pixels": role["pixelCount"], "frames": role["framesPresent"]}
            for role in roles_manifest
        ],
        "timelineSeconds": round(sum(native_durations) / FPS, 6),
        "dryRun": args.dry_run,
    }

    if args.dry_run:
        print(json.dumps(summary, indent=2))
        return

    if os.path.abspath(out_dir) != os.path.abspath(here):
        raise SystemExit("a writing build must output to the builder's own package directory")
    makedirs(out_dir)
    output_names = [pxo_name, strip_name, *ora_bytes_map.keys(), manifest_name]
    existing = [name for name in output_names if path_exists(out_dir / name)]
    if existing:
        raise SystemExit(f"refusing to overwrite existing package files: {existing}")

    write_bytes(out_dir / pxo_name, pxo_bytes)
    write_bytes(out_dir / strip_name, strip_bytes_out)
    for name, data in ora_bytes_map.items():
        write_bytes(out_dir / name, data)
    manifest_bytes_out = (
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    write_bytes(out_dir / manifest_name, manifest_bytes_out)
    print(json.dumps(summary, indent=2))
    print(f"manifest: {out_dir / manifest_name}")


if __name__ == "__main__":
    main()
