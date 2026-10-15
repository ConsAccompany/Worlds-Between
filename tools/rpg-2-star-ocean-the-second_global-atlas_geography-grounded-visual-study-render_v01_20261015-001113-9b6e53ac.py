"""Render a geography-grounded visual study, never a gameplay map or route source."""

import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


SOURCE = Path(sys.argv[1])
OUTPUT = Path(sys.argv[2])
data = json.loads(SOURCE.read_text(encoding="utf-8"))

W, H = 1920, 1080
box = (65, 168, 1855, 913)
image = Image.new("RGB", (W, H))
pixels = image.load()
for y in range(H):
    t = y / (H - 1)
    for x in range(W):
        v = int(2 * math.sin(x / 33) + 2 * math.sin((x + y) / 61))
        pixels[x, y] = (max(0, 8 + int(4 * t) + v), 25 + int(8 * t) + v, 37 + int(9 * t) + v)

draw = ImageDraw.Draw(image, "RGBA")
draw.rounded_rectangle((33, 31, 1887, 1037), radius=19, outline=(185, 171, 126, 120), width=2)
draw.rounded_rectangle((45, 153, 1875, 927), radius=8, fill=(6, 25, 37, 170), outline=(115, 158, 154, 105), width=2)


def xy(lon, lat):
    return (box[0] + (lon + 180) / 360 * (box[2] - box[0]),
            box[1] + (80 - lat) / 160 * (box[3] - box[1]))


for lon in range(-150, 181, 30):
    x, _ = xy(lon, 0)
    draw.line((x, box[1], x, box[3]), fill=(104, 151, 157, 39), width=1)
for lat in range(-60, 61, 30):
    _, y = xy(0, lat)
    draw.line((box[0], y, box[2], y), fill=(104, 151, 157, 39), width=1)
    draw.text((box[0] + 8, y + 3), f"{abs(lat):02d}°{'N' if lat >= 0 else 'S'}", fill=(167, 194, 187, 115))

land_mask = Image.new("L", (W, H))
mdraw = ImageDraw.Draw(land_mask)
coasts = []
for feature in data["features"]:
    geom = feature["geometry"]
    polygons = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for polygon in polygons:
        if not polygon:
            continue
        exterior = [xy(*point[:2]) for point in polygon[0]]
        if len(exterior) < 3:
            continue
        mdraw.polygon(exterior, fill=255)
        coasts.append(exterior)
        for interior in polygon[1:]:
            mdraw.polygon([xy(*point[:2]) for point in interior], fill=0)

clip = Image.new("L", (W, H))
ImageDraw.Draw(clip).rectangle(box, fill=255)
land_mask = ImageChops.multiply(land_mask, clip)
land = Image.new("RGB", (W, H))
lp = land.load()
rng = random.Random(20261015)
for y in range(H):
    latitude = 80 - (y - box[1]) / (box[3] - box[1]) * 160
    polar = max(0, abs(latitude) - 48) / 40
    for x in range(W):
        wave = 3 * math.sin(x / 42 + y / 23) + 2 * math.sin((x - y) / 17)
        grain = rng.randint(-5, 5)
        lp[x, y] = (max(0, 74 - int(14 * polar) + int(wave) + grain),
                    max(0, 100 - int(20 * polar) + int(wave) + grain),
                    max(0, 89 - int(7 * polar) + int(wave) + grain))
image.paste(land, (0, 0), land_mask)
coast_layer = Image.new("RGBA", (W, H))
draw = ImageDraw.Draw(coast_layer, "RGBA")
for coast in coasts:
    draw.line(coast, fill=(192, 191, 143, 152), width=2, joint="curve")
coast_layer.putalpha(ImageChops.multiply(coast_layer.getchannel("A"), clip))
image = Image.alpha_composite(image.convert("RGBA"), coast_layer)
draw = ImageDraw.Draw(image, "RGBA")

font_path = "C:/Windows/Fonts/msyh.ttc"
title = ImageFont.truetype(font_path, 37)
subtitle = ImageFont.truetype(font_path, 20)
small = ImageFont.truetype(font_path, 17)
medium = ImageFont.truetype(font_path, 23)
draw.text((69, 53), "全球地图  /  WORLD ATLAS", font=title, fill=(235, 229, 192))
draw.text((72, 110), "真实地理坐标 · 目的地由剧情与发现解锁", font=subtitle, fill=(160, 197, 188))
draw.text((1363, 109), "地球  /  EARTH", font=medium, fill=(199, 216, 194))

lon, lat = 121.4737, 31.2304  # Shanghai city-centre marker, visual positioning only.
mx, my = xy(lon, lat)
glow = Image.new("RGBA", (W, H))
gd = ImageDraw.Draw(glow, "RGBA")
gd.ellipse((mx - 42, my - 42, mx + 42, my + 42), fill=(75, 221, 218, 180))
glow = glow.filter(ImageFilter.GaussianBlur(19))
image = Image.alpha_composite(image.convert("RGBA"), glow)
draw = ImageDraw.Draw(image, "RGBA")
draw.ellipse((mx - 13, my - 13, mx + 13, my + 13), fill=(10, 41, 47, 255), outline=(135, 246, 226, 255), width=3)
draw.ellipse((mx - 4, my - 4, mx + 4, my + 4), fill=(234, 239, 179, 255))
draw.line((mx + 15, my - 2, mx + 45, my - 30), fill=(190, 233, 215, 210), width=2)
draw.rounded_rectangle((mx + 41, my - 72, mx + 213, my - 28), radius=8,
                       fill=(6, 31, 42, 230), outline=(128, 196, 178, 220), width=2)
draw.text((mx + 52, my - 65), "上海  SHANGHAI", font=small, fill=(236, 235, 196))

draw.rounded_rectangle((69, 936, 1852, 1009), radius=10, fill=(10, 29, 39, 245), outline=(89, 133, 137, 130), width=1)
draw.text((92, 953), "首个可玩地点：上海（暂定）", font=medium, fill=(233, 229, 193))
draw.text((1130, 956), "放大地区后查看道路与遗址", font=small, fill=(169, 204, 198))
draw.text((1608, 54), "VISUAL STUDY 01", font=small, fill=(153, 187, 183))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
image.convert("RGB").save(OUTPUT, optimize=True)
print(OUTPUT)
