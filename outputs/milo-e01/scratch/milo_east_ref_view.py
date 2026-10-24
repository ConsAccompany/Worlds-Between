"""Scratch QA (not source): x5 side-by-side view of existing statics for east reference. Reads only; writes argv[1]."""
import glob, os, sys
from PIL import Image

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
pats = ["game/assets/characters/milo-native-v01/south/*static_*.png", "game/assets/characters/milo-native-v01/north/*static_*.png",
        "game/assets/characters/milo-native-v01/west/*static_*.png", "game/assets/characters/lin-que-native-v01/east/*static_*.png"]
pats += sys.argv[2:]
ims = [Image.open(glob.glob(os.path.join(R, p))[0]).convert("RGBA") for p in pats]
out = Image.new("RGBA", (80 * 5 * len(ims), 112 * 5), (120, 130, 120, 255))
for i, im in enumerate(ims):
    out.alpha_composite(im.resize((400, 560), Image.NEAREST), (400 * i, 0))
out.save(sys.argv[1])
