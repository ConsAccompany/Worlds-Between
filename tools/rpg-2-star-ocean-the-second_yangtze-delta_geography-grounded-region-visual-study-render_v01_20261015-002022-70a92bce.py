"""Render a location/road-grounded regional UI study; no playable map behavior."""

import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


land_data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
road_data = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
output = Path(sys.argv[3])

W, H = 1920, 1080
view = (60, 177, 1400, 924)
geo = (118.3, 29.5, 122.55, 31.85)


def xy(lon, lat):
    return (view[0] + (lon - geo[0]) / (geo[2] - geo[0]) * (view[2] - view[0]),
            view[1] + (geo[3] - lat) / (geo[3] - geo[1]) * (view[3] - view[1]))


im = Image.new("RGB", (W, H))
p = im.load()
for y in range(H):
    for x in range(W):
        v = 2 * math.sin((x + y) / 73)
        p[x, y] = (int(7 + v), int(25 + y * 0.005 + v), int(36 + y * 0.005 + v))
draw = ImageDraw.Draw(im, "RGBA")
draw.rounded_rectangle((28, 28, 1890, 1042), radius=18, outline=(169, 179, 145, 115), width=2)
draw.rounded_rectangle((45, 161, 1414, 939), radius=9, fill=(7, 31, 43, 230), outline=(94, 156, 160, 130), width=2)
draw.rounded_rectangle((1432, 161, 1875, 939), radius=9, fill=(10, 33, 43, 242), outline=(94, 156, 160, 130), width=2)
for lon in (119, 120, 121, 122):
    x, _ = xy(lon, 30)
    draw.line((x, view[1], x, view[3]), fill=(113, 164, 173, 36), width=1)
for lat in (30, 31):
    _, y = xy(120, lat)
    draw.line((view[0], y, view[2], y), fill=(113, 164, 173, 36), width=1)

clip = Image.new("L", (W, H))
ImageDraw.Draw(clip).rectangle(view, fill=255)
mask = Image.new("L", (W, H))
md = ImageDraw.Draw(mask)
coasts = []
for feature in land_data["features"]:
    geom = feature["geometry"]
    polygons = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for poly in polygons:
        exterior = [xy(*point[:2]) for point in poly[0]]
        if len(exterior) < 3:
            continue
        md.polygon(exterior, fill=255)
        coasts.append(exterior)
        for hole in poly[1:]:
            md.polygon([xy(*point[:2]) for point in hole], fill=0)
mask = ImageChops.multiply(mask, clip)

terrain = Image.new("RGB", (W, H))
tp = terrain.load()
rng = random.Random(1015)
for y in range(H):
    for x in range(W):
        grain = rng.randint(-4, 4)
        wave = int(3 * math.sin((x - y) / 39) + 2 * math.sin(y / 15))
        tp[x, y] = (77 + grain + wave, 102 + grain + wave, 88 + grain + wave)
im.paste(terrain, (0, 0), mask)

coast_layer = Image.new("RGBA", (W, H))
cd = ImageDraw.Draw(coast_layer, "RGBA")
for points in coasts:
    cd.line(points, fill=(190, 203, 155, 160), width=2, joint="curve")
coast_layer.putalpha(ImageChops.multiply(coast_layer.getchannel("A"), clip))
im = Image.alpha_composite(im.convert("RGBA"), coast_layer)

road_layer = Image.new("RGBA", (W, H))
rd = ImageDraw.Draw(road_layer, "RGBA")
for feature in road_data["features"]:
    rank = feature["properties"].get("scalerank", 10)
    if rank > 7:
        continue
    geom = feature["geometry"]
    lines = [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]
    for line in lines:
        if len(line) > 1:
            points = [xy(*point[:2]) for point in line]
            rd.line(points, fill=(215, 177, 109, 130 if rank <= 4 else 75),
                    width=3 if rank <= 4 else 2, joint="curve")
road_layer.putalpha(ImageChops.multiply(road_layer.getchannel("A"), clip))
im = Image.alpha_composite(im, road_layer)

font_path = "C:/Windows/Fonts/msyh.ttc"
title = ImageFont.truetype(font_path, 38)
medium = ImageFont.truetype(font_path, 24)
body = ImageFont.truetype(font_path, 21)
small = ImageFont.truetype(font_path, 17)
draw = ImageDraw.Draw(im, "RGBA")
draw.text((67, 49), "地区地图  /  YANGTZE DELTA", font=title, fill=(237, 228, 193))
draw.text((70, 111), "真实城市、遗址及道路位置 · 科技区首段（暂定）", font=body, fill=(160, 198, 189))
draw.text((1509, 81), "目的地  /  DESTINATIONS", font=medium, fill=(230, 222, 187))

places = [
    ("上海  SHANGHAI", 121.434559, 31.218398, (19, -51), True),
    ("松江  SONGJIANG", 121.223256, 31.034427, (-177, 20), False),
    ("良渚古城遗址  LIANGZHU", 119.991, 30.396, (-12, -49), False),
    ("杭州  HANGZHOU", 120.168073, 30.251920, (19, 17), False),
]
glow = Image.new("RGBA", (W, H))
gd = ImageDraw.Draw(glow, "RGBA")
for name, lon, lat, label_offset, active in places:
    mx, my = xy(lon, lat)
    if active:
        gd.ellipse((mx - 38, my - 38, mx + 38, my + 38), fill=(75, 226, 217, 175))
im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(16)))
draw = ImageDraw.Draw(im, "RGBA")
for name, lon, lat, label_offset, active in places:
    mx, my = xy(lon, lat)
    color = (143, 241, 224) if active else (238, 218, 155)
    draw.ellipse((mx - 10, my - 10, mx + 10, my + 10), fill=(5, 35, 44), outline=color, width=3)
    draw.ellipse((mx - 3, my - 3, mx + 3, my + 3), fill=color)
    lx, ly = mx + label_offset[0], my + label_offset[1]
    bbox = draw.textbbox((lx + 10, ly + 7), name, font=small)
    draw.rounded_rectangle((lx, ly, bbox[2] + 10, bbox[3] + 6), radius=7,
                           fill=(7, 29, 38, 231), outline=(*color, 180), width=1)
    draw.text((lx + 10, ly + 7), name, font=small, fill=(239, 232, 195))

cards = [
    (188, "上海", "SHANGHAI", "当前地点 / CURRENT"),
    (405, "松江郊外", "SONGJIANG OUTSKIRTS", "汽车 · 34.8 km · 26 分钟参考"),
    (622, "良渚古城遗址", "LIANGZHU RUINS", "汽车 · 187.9 km · 约 2 小时参考"),
]
for top, cn, en, detail in cards:
    draw.rounded_rectangle((1455, top, 1852, top + 172), radius=11,
                           fill=(15, 45, 54, 240), outline=(111, 161, 151, 143), width=2)
    draw.text((1481, top + 19), cn, font=medium, fill=(237, 227, 186))
    draw.text((1483, top + 64), en, font=small, fill=(167, 202, 191))
    draw.text((1483, top + 111), detail, font=small, fill=(216, 209, 174))

draw.rounded_rectangle((69, 955, 1853, 1014), radius=9, fill=(9, 31, 40, 247),
                       outline=(96, 151, 148, 120), width=1)
draw.text((91, 969), "全球地图 → 地区地图 → 场景步行", font=body, fill=(227, 226, 186))
draw.text((1543, 971), "VISUAL STUDY 01", font=small, fill=(159, 192, 183))

output.parent.mkdir(parents=True, exist_ok=True)
im.convert("RGB").save(output, optimize=True)
print(output)
