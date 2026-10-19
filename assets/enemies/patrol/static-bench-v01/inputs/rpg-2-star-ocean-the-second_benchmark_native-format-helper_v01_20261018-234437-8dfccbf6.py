# Shared, identical native-format helper. Not a submission. Pillow images are RGBA.
import io,json,zipfile,xml.etree.ElementTree as ET
from PIL import Image
W=64
H=64
LAYER_ORDER=[]
def to_rgba(image):return image.convert("RGBA")
def make_pxo(per_frame_layers, durations, preview_png, fname, fps, order=None, dt=(2026, 10, 15, 3, 43, 26),
             opacity=None):
    order = order or LAYER_ORDER     # v3r3 passes its own layer order and zip time
    opacity = opacity or {}          # v03: per-layer opacity (the contact-shadow layer)
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": opacity.get(n, 1.0), "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in order]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in order], "duration": d, "metadata": {}} for d in durations]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(fname), "frame_current_tag": "0",
                      "include_tag_in_filename": "false", "interpolation": "0", "lines_count": "1",
                      "new_dir_for_each_frame_tag": "false", "number_of_digits": "4", "number_of_frames": "1",
                      "orientation": "0", "repeat_count": "0", "resize": "100", "save_quality": "0.75",
                      "separator_character": "\"_\"", "sheet_layers_as_separate_files": "false",
                      "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": min(4, len(order)-1), "export_profile": export_profile,
            "fps": fps, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": "v1.2.3-stable",
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    # dt: fixed zip time (zip needs even seconds) -> byte-identical rebuilds
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        for fi, layers in enumerate(per_frame_layers, start=1):
            put(f"image_data/frames/{fi}/", b"")
            for li, name in enumerate(order, start=1):
                put(f"image_data/frames/{fi}/layer_{li}", to_rgba(layers[name]).tobytes())
                put(f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()
def pxo_bytes(frames,durations,preview_png,name):
 global W,H,LAYER_ORDER
 LAYER_ORDER=list(frames[0]);W,H=next(iter(frames[0].values())).size
 return make_pxo(frames,durations,preview_png,name,12,order=LAYER_ORDER,dt=(2026,10,18,0,0,0))
def ora_bytes(layers):
 order=list(layers);w,h=next(iter(layers.values())).size
 merged=Image.new("RGBA",(w,h))
 for name in order:merged.alpha_composite(layers[name])
 buf=io.BytesIO();root=ET.Element("image",w=str(w),h=str(h),name="Worlds Between candidate");stack=ET.SubElement(root,"stack")
 with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED)as z:
  def put(n,b):z.writestr(zipfile.ZipInfo(n,(2026,10,18,0,0,0)),b,zipfile.ZIP_DEFLATED)
  put("mimetype",b"image/openraster")
  for i,name in reversed(list(enumerate(order))):
   f="data/layer-%d.png"%i;o=io.BytesIO();layers[name].save(o,format="PNG");put(f,o.getvalue());ET.SubElement(stack,"layer",name=name,src=f,opacity="1.0",visibility="visible",x="0",y="0",**{"composite-op":"svg:src-over"})
  o=io.BytesIO();merged.save(o,format="PNG");put("mergedimage.png",o.getvalue());put("stack.xml",ET.tostring(root,encoding="utf-8"))
 return buf.getvalue()
