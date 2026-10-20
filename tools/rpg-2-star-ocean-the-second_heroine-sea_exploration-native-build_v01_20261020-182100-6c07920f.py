"""Generated-art adaptation, not hand-authored pixel art or creator acceptance.

Prepare one static exploration candidate at the existing 48-logical-pixel size.
Editable layers are explicit nonoverlapping region slices of the generated input.
"""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, io, json, uuid, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WRITER = "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    src = Path(args.input).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    tag = now.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    prefix = "rpg-2-star-ocean-the-second_heroine-sea_exploration"
    name = lambda role, ext: f"{prefix}-{role}_unapproved-v01_{tag}.{ext}"
    rgba = Image.open(src).convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda x: 255 if x >= 128 else 0)
    rgba.putalpha(alpha)
    bbox = alpha.getbbox()
    assert bbox, "Input must have an actual nonempty alpha silhouette"
    crop = rgba.crop(bbox)
    width = round(crop.width * 96 / crop.height)
    assert width <= 72, "Do not squeeze or distort the silhouette"
    sampled = crop.resize((width, 96), Image.Resampling.NEAREST)
    a = np.array(sampled)
    opaque = a[a[:, :, 3] == 255, :3]
    palette_image = Image.fromarray(opaque.reshape(1, -1, 3), "RGB").quantize(colors=32, dither=Image.Dither.NONE)
    rgb = sampled.convert("RGB").quantize(palette=palette_image, dither=Image.Dither.NONE).convert("RGBA")
    rgb.putalpha(sampled.getchannel("A"))
    canvas = Image.new("RGBA", (80, 112))
    canvas.paste(rgb, ((80-width)//2, 8))
    ar = np.array(canvas)
    ar[ar[:, :, 3] == 0] = 0
    canvas = Image.fromarray(ar)
    assert canvas.getchannel("A").getbbox()[1::2] == (8, 104)
    masks = {}
    yy, xx = np.indices((112, 80))
    masks["head-hair-ponytail-slice"] = yy < 40
    masks["upper-body-arms-slice"] = (yy >= 40) & (yy < 66)
    masks["left-leg-boot-slice"] = (yy >= 66) & (xx < 40)
    masks["right-leg-boot-slice"] = (yy >= 66) & (xx >= 40)
    layers = {k: np.where(m[:, :, None], ar, 0).astype(np.uint8) for k,m in masks.items()}
    combined = np.zeros_like(ar)
    for im in layers.values():
        combined[im[:, :, 3] != 0] = im[im[:, :, 3] != 0]
    assert np.array_equal(combined, ar), "Region slicing must reconstruct exact RGBA"
    spec = importlib.util.spec_from_file_location("existing_pxo_writer", ROOT / WRITER)
    writer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(writer)
    writer.W, writer.H = 80, 112
    writer.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    image_bytes = png(canvas)
    paths = {"png": name("native80x112", "png"), "ora": name("region-layered", "ora"), "pxo": name("region-editable", "pxo")}
    (out / paths["png"]).write_bytes(image_bytes)
    (out / paths["pxo"]).write_bytes(writer.make_pxo([layers], [1.0], image_bytes, paths["png"], 8, order=list(layers), dt=tuple(now.timetuple()[:6])))
    with zipfile.ZipFile(out / paths["ora"], "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("mergedimage.png", image_bytes)
        root = ET.Element("image", {"w":"80", "h":"112", "name":"generated-art regional slices"})
        stack = ET.SubElement(root, "stack")
        for i, (key, im) in enumerate(reversed(list(layers.items()))):
            path = f"data/layer{i}.png"
            z.writestr(path, png(Image.fromarray(im)))
            ET.SubElement(stack, "layer", {"name":key,"src":path,"x":"0","y":"0","opacity":"1.0","visibility":"visible","composite-op":"svg:src-over"})
        z.writestr("stack.xml", ET.tostring(root, encoding="utf8"))
    manifest = {"status":"UNAPPROVED generated-art adaptation, static only", "createdAt":now.isoformat(), "input":{"file":str(src),"sha256":digest(src.read_bytes()),"generator":"built-in image_gen","sourceSize":list(rgba.size),"alphaCrop":list(bbox)}, "conversion":{"resampling":"nearest", "opaqueColorLimit":32,"dither":False,"alphaThreshold":128,"bodyHeightNative":96,"displayScale":0.5,"bodyHeightLogical":48,"canvas":[80,112],"offsetNative":[-40,-104],"layers":"Nonoverlapping generated-image region slices; not separately painted or independently authored anatomy"}, "source":{"file":str(Path(__file__).relative_to(ROOT)),"sha256TextLf":digest(Path(__file__).read_bytes().replace(b"\r\n",b"\n"))},"writer":{"file":WRITER,"sha256TextLf":digest((ROOT/WRITER).read_bytes().replace(b"\r\n",b"\n"))},"files":{k:{"file":v,"sha256":digest((out/v).read_bytes())} for k,v in paths.items()},"nativeAppExportVerified":False,"guiSaveReopenVerified":False,"creatorApproved":False,"runtimeDefaultChanged":False}
    mf = out / name("adaptation-manifest", "json")
    mf.write_text(json.dumps(manifest, indent=2)+"\n",encoding="utf8")
    print(json.dumps({"manifest":str(mf),"candidate":str(out/paths["png"]),"nativeFiles":paths,"bodyHeightLogical":48}))

if __name__ == "__main__":
    main()
