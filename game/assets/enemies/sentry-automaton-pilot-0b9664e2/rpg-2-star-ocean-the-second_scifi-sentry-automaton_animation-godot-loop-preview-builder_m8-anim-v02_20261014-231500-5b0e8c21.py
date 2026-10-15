"""Build review-only loop GIFs from REAL Godot 1280x720 renders of the sentry animation pilot v2.

Input: the crops written by the v2 check/capture test
(game/tests/rpg-2-star-ocean-the-second_sentry-automaton-animation-pilot_battle-check-capture_m8-anim-v02_20261014-230639-ad3f9d97.gd)
into work/sentry-animation-v2-godot-crops-<stamp>/. Each crop is an unscaled region of the 1280x720
viewport (2 physical px per logical px):
  solo-NN.png        every strip frame with the party out of contact (window x 300-540, y 186-280)
  walk-NN.png        16 consecutive real gait steps of the sentry walking in (same window, so the floor stays put)
  contact-v2-NN.png  wind-up, strike, the hero's blow and the flinch at the 53 px melee spacing (window x 320-520, y 190-280)
  contact-v1-NN.png  the same sequence with the v1 strip replayed through the same runtime, for comparison
Crops are only sequenced here; nothing is resized, resampled or redrawn.

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> CROP_DIR OUT_DIR   -> three new uniquely named GIFs + a JSON note in OUT_DIR
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image

SLUG = "rpg-2-star-ocean-the-second"
TAG = "m8-anim-v02"
# Runtime timings (ms): idle 0.22 s, gait one 4 px step per 1/17 s at 68 px/s, wind-up halves of 0.48 s, strike 0.15 s, hit 0.12 s, defeat 0.16 s.
STEP_MS = 59
SOLO_SEQUENCE = (
    [("solo", i, 220) for i in [0, 1, 2, 3] * 2]
    + [("walk", i, STEP_MS) for i in range(16)]
    + [("solo", 12, 240), ("solo", 13, 240), ("solo", 14, 150), ("solo", 15, 150)]
    + [("solo", i, 220) for i in [0, 1, 2, 3]]
    + [("solo", 16, 120), ("solo", 17, 120)]
    + [("solo", i, 220) for i in [0, 1, 2, 3]]
    + [("solo", 18, 160), ("solo", 19, 160), ("solo", 20, 1000)]
)
# Contact crops: 0 idle, 1-2 wind-up, 3-4 strike on the hero, 5 idle, 6-7 flinch under the hero's attack, 8 idle as the attack ends, 9 idle.
CONTACT_TIMING = [220, 240, 240, 150, 150, 220, 120, 120, 130, 500]


def load(crop_dir: Path, group: str, index: int) -> Image.Image:
    return Image.open(crop_dir / f"{group}-{index:02d}.png").convert("RGB")


def save_gif(frames: list, durations: list, path: Path) -> None:
    # Shared adaptive palette across all frames so the GIF does not flicker.
    size = frames[0].size
    assert all(f.size == size for f in frames)
    pal_src = Image.new("RGB", (size[0], size[1] * len(frames)))
    for i, f in enumerate(frames):
        pal_src.paste(f, (0, i * size[1]))
    pal = pal_src.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    seq = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    seq[0].save(path, save_all=True, append_images=seq[1:], duration=durations, loop=0)


def main() -> None:
    crop_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    solo_gif = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-loop-preview_{TAG}_{stamp}-{token}.gif"
    contact_gif = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-contact-loop_{TAG}_{stamp}-{token}.gif"
    v1_gif = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-contact-loop-v1-replay_{TAG}_{stamp}-{token}.gif"
    note = out_dir / f"{SLUG}_scifi-sentry-automaton-animation-pilot_godot-render-preview-note_{TAG}_{stamp}-{token}.json"
    for p in (solo_gif, contact_gif, v1_gif, note):
        assert not p.exists(), p
    save_gif([load(crop_dir, g, i) for g, i, _ in SOLO_SEQUENCE], [d for _, _, d in SOLO_SEQUENCE], solo_gif)
    for group, path in (("contact-v2", contact_gif), ("contact-v1", v1_gif)):
        save_gif([load(crop_dir, group, i) for i in range(len(CONTACT_TIMING))], CONTACT_TIMING, path)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    root = Path(__file__).resolve().parents[4]
    rel = lambda p: str(p.resolve().relative_to(root)).replace("\\", "/")
    crops = sorted(crop_dir.glob("*.png"))
    note.write_text(json.dumps({
        "project": SLUG,
        "revision": TAG,
        "kind": "review-only previews built from real Godot renders (unscaled 1280x720 viewport crops)",
        "status": "animation_pilot_unapproved",
        "artAcceptanceCount": 0,
        "cropDir": str(crop_dir).replace("\\", "/"),
        "cropSha256": {p.name: sha(p) for p in crops},
        "gifs": {
            "soloLoop": {"file": rel(solo_gif), "sha256": sha(solo_gif), "sequence": SOLO_SEQUENCE,
                          "note": "party out of contact; the walk section is 16 real consecutive gait steps in a fixed window (the sentry travels 64 px), then the loop returns to the in-place frames"},
            "contactLoopV2": {"file": rel(contact_gif), "sha256": sha(contact_gif), "timingMs": CONTACT_TIMING,
                               "note": "hero at enemy_x - 53 (the AI melee spacing): idle, wind-up, strike (sentry drawn over the hero), idle, flinch under the hero's attack (hero on top), idle"},
            "contactLoopV1Replay": {"file": rel(v1_gif), "sha256": sha(v1_gif), "timingMs": CONTACT_TIMING,
                                     "note": "same sequence with the v1 strip replayed through the same runtime (v1 cell, anchor 48, heroes always on top), for before/after comparison"},
        },
        "builder": rel(Path(__file__)),
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(solo_gif)
    print(contact_gif)
    print(v1_gif)
    print(note)


if __name__ == "__main__":
    main()
