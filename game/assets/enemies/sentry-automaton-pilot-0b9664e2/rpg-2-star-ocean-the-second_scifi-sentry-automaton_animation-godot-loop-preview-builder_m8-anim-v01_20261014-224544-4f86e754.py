"""Build review-only loop previews from REAL Godot 1280x720 renders of every sentry animation frame.

Input: the per-frame crops written by the animation check/capture test
(game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_battle-check-capture_m8-anim-v01_20261014-224030-38da9a92.gd)
into work/sentry-animation-godot-crops-<stamp>/frame-NN.png. Each crop is an unscaled region of the
1280x720 viewport (2 physical px per logical px). Crops are only arranged and sequenced here; nothing
is resized, resampled or redrawn.

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> CROP_DIR OUT_DIR   -> new uniquely named GIF + frame sheet + JSON note in OUT_DIR
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

SLUG = "rpg-2-star-ocean-the-second"
STATES = [("idle", [0, 1, 2, 3]), ("move", [4, 5, 6, 7]), ("windup", [8, 9]), ("strike", [10, 11]), ("hit", [12, 13]), ("defeat", [14, 15, 16])]
# Runtime timings (ms): idle 0.22 s, move 0.12 s, wind-up halves of 0.48 s, strike 0.15 s, hit 0.12 s, defeat 0.16 s.
SEQUENCE = (
    [(i, 220) for i in [0, 1, 2, 3] * 2]
    + [(i, 120) for i in [4, 5, 6, 7] * 2]
    + [(8, 240), (9, 240), (10, 150), (11, 150)]
    + [(i, 220) for i in [0, 1, 2, 3]]
    + [(12, 120), (13, 120)]
    + [(i, 220) for i in [0, 1, 2, 3]]
    + [(14, 160), (15, 160), (16, 1000)]
)


def main() -> None:
    crop_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    frames = [Image.open(crop_dir / f"frame-{i:02d}.png").convert("RGB") for i in range(17)]
    size = frames[0].size
    assert all(f.size == size for f in frames)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    gif = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-loop-preview_m8-anim-v01_{stamp}-{token}.gif"
    sheet = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-frame-sheet_m8-anim-v01_{stamp}-{token}.png"
    note = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-preview-note_m8-anim-v01_{stamp}-{token}.json"
    for p in (gif, sheet, note):
        assert not p.exists(), p
    # Shared adaptive palette across all frames so the GIF does not flicker.
    pal_src = Image.new("RGB", (size[0], size[1] * 17))
    for i, f in enumerate(frames):
        pal_src.paste(f, (0, i * size[1]))
    pal = pal_src.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    seq = [frames[i].quantize(palette=pal, dither=Image.Dither.NONE) for i, _ in SEQUENCE]
    seq[0].save(gif, save_all=True, append_images=seq[1:], duration=[d for _, d in SEQUENCE], loop=0)
    cols, label_h, pad = 6, 16, 6
    rows = 3
    canvas = Image.new("RGB", (cols * (size[0] + pad) + pad, rows * (size[1] + label_h + pad) + pad + 20), (16, 20, 28))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 4), "Sentry animation pilot - real Godot 1280x720 renders, unscaled crops - UNAPPROVED, art acceptance 0", fill=(230, 230, 230))
    slot = 0
    for state, idx in STATES:
        for k, i in enumerate(idx):
            x0 = pad + (slot % cols) * (size[0] + pad)
            y0 = 20 + pad + (slot // cols) * (size[1] + label_h + pad)
            d.text((x0, y0), f"{i:02d} {state} {k}", fill=(200, 210, 220))
            canvas.paste(frames[i], (x0, y0 + label_h))
            slot += 1
    canvas.save(sheet)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    root = Path(__file__).resolve().parents[4]
    rel = lambda p: str(p.resolve().relative_to(root)).replace("\\", "/")
    note.write_text(json.dumps({
        "project": SLUG,
        "kind": "review-only preview built from real Godot renders",
        "cropDir": str(crop_dir).replace("\\", "/"),
        "cropSizePhysicalPx": list(size),
        "cropSha256": {f"frame-{i:02d}": sha(crop_dir / f"frame-{i:02d}.png") for i in range(17)},
        "gif": {"file": rel(gif), "sha256": sha(gif), "sequence": SEQUENCE},
        "frameSheet": {"file": rel(sheet), "sha256": sha(sheet)},
        "builder": rel(Path(__file__)),
        "builderSha256": sha(Path(__file__).resolve()),
        "artAcceptanceCount": 0,
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }, indent=2) + "\n", encoding="utf-8")
    print(gif)
    print(sheet)
    print(note)


if __name__ == "__main__":
    main()
