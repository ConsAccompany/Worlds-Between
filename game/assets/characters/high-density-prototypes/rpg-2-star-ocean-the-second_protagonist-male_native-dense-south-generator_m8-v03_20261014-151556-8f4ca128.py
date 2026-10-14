"""Hand-authored south-facing protagonist pixel experiment.

All anatomy, clothing, and highlights are drawn as intentional native pixel
clusters. This script never reads, scales, traces, or composites prior art.
Run with the bundled Python/Pillow runtime; output is one transparent PNG.
"""

from pathlib import Path
from PIL import Image, ImageDraw


OUT = Path(__file__).with_name(
    "rpg-2-star-ocean-the-second_protagonist-male_native-dense-south-idle_m8-v03_20261014-151556-75c4d0a1.png"
)
im = Image.new("RGBA", (192, 224), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

# Colored outlines and a constrained material palette. No random noise.
ink = "#22232a"
hair_0 = "#28242a"
hair_1 = "#3b3030"
hair_2 = "#544039"
hair_3 = "#705244"
hair_4 = "#96705a"
skin_0 = "#8d543f"
skin_1 = "#bd7956"
skin_2 = "#d99568"
skin_3 = "#efb687"
skin_4 = "#ffcca0"
coat_0 = "#302e30"
coat_1 = "#4c403b"
coat_2 = "#665247"
coat_3 = "#856b55"
coat_4 = "#a78768"
coat_5 = "#c2a27a"
cloth_0 = "#55504b"
cloth_1 = "#847565"
cloth_2 = "#b3a28a"
cloth_3 = "#dacdb1"
cloth_4 = "#f1e1c5"
teal_0 = "#143b40"
teal_1 = "#1e5960"
teal_2 = "#2c7878"
teal_3 = "#55a0a0"
teal_4 = "#8cc2b4"
metal_0 = "#53565a"
metal_1 = "#929997"
metal_2 = "#c5c8b2"
gold_0 = "#7e5736"
gold_1 = "#b58b56"
gold_2 = "#e1c085"


def poly(points, fill, outline=None, width=1):
    d.polygon(points, fill=fill)
    if outline is not None:
        d.line(points + [points[0]], fill=outline, width=width, joint="curve")


def rect(box, fill, outline=None, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)


def line(points, fill, width=1):
    d.line(points, fill=fill, width=width, joint="curve")


# Rear equipment: compact rolled blanket and straps. It sits behind the head
# and shoulder instead of forming a broad, anonymous dark silhouette.
poly([(121, 92), (134, 91), (145, 97), (151, 105), (148, 117), (137, 123),
      (122, 118), (116, 109)], teal_0, ink, 2)
poly([(126, 95), (139, 96), (146, 102), (147, 112), (140, 118), (126, 114),
      (121, 106)], teal_1)
poly([(126, 97), (138, 98), (143, 102), (142, 112), (135, 116), (126, 111)], teal_2)
poly([(133, 99), (142, 101), (144, 107), (139, 114), (131, 112), (127, 105)], teal_0)
line([(136, 101), (140, 104), (139, 109), (134, 111), (131, 108)], teal_3, 2)
line([(119, 98), (130, 94), (142, 98)], coat_4, 3)
rect((123, 111, 143, 115), coat_1)
rect((131, 112, 135, 116), gold_1)
rect((132, 112, 134, 114), gold_2)
poly([(121, 111), (142, 118), (145, 139), (133, 147), (117, 132)], coat_0, ink)
poly([(124, 116), (138, 121), (139, 136), (131, 141), (120, 127)], coat_2)

# Long asymmetric scarf tail, drawn before the torso so the folds emerge from
# under the shoulder. The brighter lower edge keeps it distinct from the coat.
poly([(78, 106), (88, 108), (87, 129), (82, 148), (75, 164), (66, 172),
      (68, 150), (72, 130)], teal_0, ink, 2)
poly([(77, 112), (84, 111), (83, 129), (76, 151), (72, 164), (70, 163),
      (72, 139)], teal_1)
poly([(81, 116), (85, 117), (79, 139), (76, 145), (76, 126)], teal_2)
line([(71, 157), (69, 168), (72, 164)], teal_3, 2)
line([(75, 151), (72, 156)], teal_4, 2)

# Legs: distinct stance and multiple large value clusters, never an enlarged
# copy of the previous 32x48 sprite.
poly([(80, 149), (99, 152), (101, 172), (96, 187), (94, 194), (78, 193),
      (75, 176)], coat_0, ink, 2)
poly([(82, 153), (96, 155), (96, 174), (91, 188), (80, 187), (79, 172)], cloth_0)
poly([(82, 157), (88, 157), (85, 181), (79, 182), (78, 171)], cloth_1)
poly([(88, 156), (94, 158), (95, 171), (91, 180), (87, 179)], coat_2)
line([(80, 169), (84, 173), (91, 173)], coat_3, 2)
line([(83, 185), (90, 186), (95, 182)], cloth_2, 2)
poly([(99, 151), (119, 151), (122, 176), (120, 195), (103, 194),
      (100, 180), (96, 169)], coat_0, ink, 2)
poly([(101, 157), (116, 156), (119, 178), (116, 188), (106, 188),
      (102, 175)], cloth_0)
poly([(105, 159), (111, 157), (114, 176), (112, 186), (106, 185)], cloth_1)
poly([(114, 164), (119, 166), (119, 181), (115, 188), (111, 181)], coat_2)
line([(101, 171), (109, 174), (116, 173)], coat_3, 2)
line([(105, 186), (112, 184), (118, 188)], cloth_2, 2)

# Left boot, with leather planes, separate cuff, sole, laces and toe facet.
poly([(79, 186), (95, 187), (98, 204), (94, 208), (74, 208), (72, 203),
      (75, 195)], ink)
poly([(79, 189), (92, 189), (95, 202), (91, 204), (76, 203), (75, 200)], coat_1)
poly([(78, 190), (91, 190), (92, 195), (78, 196)], coat_3)
rect((79, 189, 92, 191), coat_4)
poly([(78, 197), (88, 196), (92, 201), (89, 204), (75, 203)], coat_2)
line([(76, 202), (87, 202), (94, 204)], coat_4, 2)
line([(74, 206), (91, 206)], coat_0, 2)
for y in (194, 198, 201):
    line([(82, y), (89, y + 1)], gold_1, 1)
rect((82, 192, 84, 193), gold_2)
rect((87, 195, 89, 196), gold_2)

# Right boot is pushed slightly forward. The two soles share y=208 anchor.
poly([(103, 187), (120, 187), (123, 199), (125, 205), (121, 208),
      (102, 208), (99, 204)], ink)
poly([(105, 189), (118, 189), (120, 201), (122, 204), (103, 204),
      (102, 201)], coat_1)
poly([(105, 190), (118, 190), (119, 195), (105, 195)], coat_3)
rect((106, 189, 119, 191), coat_4)
poly([(109, 197), (119, 198), (122, 204), (107, 204), (103, 201)], coat_2)
line([(105, 203), (118, 203), (123, 205)], coat_4, 2)
line([(103, 206), (122, 206)], coat_0, 2)
for y in (194, 198, 201):
    line([(108, y + 1), (115, y)], gold_1, 1)
rect((114, 192, 116, 193), gold_2)
rect((108, 195, 110, 196), gold_2)

# Right coat tail, split from the left for a readable asymmetric traveler coat.
poly([(114, 114), (132, 111), (138, 133), (139, 151), (132, 165),
      (119, 170), (114, 155)], coat_0, ink, 2)
poly([(119, 115), (130, 115), (135, 137), (134, 152), (127, 161),
      (119, 164)], coat_2)
poly([(127, 122), (133, 124), (136, 144), (132, 154), (126, 160)], coat_3)
line([(128, 120), (131, 136), (130, 153), (124, 163)], coat_4, 2)
line([(121, 165), (130, 160), (134, 154)], coat_1, 2)
poly([(64, 113), (84, 116), (80, 154), (77, 168), (66, 164),
      (60, 149)], coat_0, ink, 2)
poly([(65, 119), (79, 120), (76, 154), (73, 164), (66, 159)], coat_2)
poly([(67, 121), (72, 121), (70, 146), (66, 155), (63, 145)], coat_3)
line([(72, 124), (74, 146), (70, 160)], coat_4, 2)
line([(65, 159), (73, 163), (77, 157)], coat_1, 2)
rect((67, 149, 74, 152), coat_1)
rect((68, 150, 71, 151), gold_1)

# Shirt and upper torso, ivory center panel under open brown lapels.
poly([(79, 100), (116, 99), (125, 117), (119, 152), (79, 153),
      (71, 116)], coat_0, ink, 2)
poly([(83, 106), (113, 105), (117, 115), (113, 149), (82, 149),
      (78, 116)], cloth_1)
poly([(86, 108), (110, 108), (113, 118), (110, 146), (86, 146),
      (82, 118)], cloth_3)
poly([(91, 111), (100, 109), (101, 145), (89, 143)], cloth_4)
poly([(101, 111), (109, 110), (111, 132), (108, 143), (104, 143)], cloth_2)
line([(97, 117), (99, 145)], coat_3, 1)
for y in (123, 132, 141):
    rect((99, y, 101, y + 2), gold_0)
    rect((99, y, 100, y), gold_2)
line([(85, 136), (90, 138), (94, 137)], cloth_1, 1)
line([(103, 139), (108, 137)], cloth_4, 1)

# Outer shoulders, sleeves and gloves use separate overlapping planes.
poly([(74, 99), (88, 106), (77, 129), (71, 132), (57, 122),
      (59, 109)], coat_0, ink, 2)
poly([(62, 109), (74, 104), (82, 110), (74, 127), (59, 119)], coat_2)
poly([(63, 109), (72, 105), (75, 110), (68, 116), (61, 115)], coat_4)
poly([(61, 120), (73, 129), (70, 143), (61, 145), (55, 133)], coat_0, ink, 2)
poly([(60, 124), (70, 131), (67, 140), (60, 141), (57, 134)], coat_2)
poly([(61, 124), (65, 127), (61, 136), (57, 133)], coat_3)
line([(59, 137), (67, 141)], coat_4, 2)
poly([(58, 141), (71, 141), (72, 149), (58, 150)], cloth_2, coat_0, 1)
rect((60, 143, 68, 145), cloth_4)
poly([(60, 150), (70, 148), (73, 157), (68, 162), (58, 158)], coat_0, ink)
poly([(61, 151), (67, 151), (69, 158), (64, 159), (59, 156)], coat_2)
rect((59, 155, 62, 159), coat_4)
rect((65, 159, 67, 162), skin_1)

poly([(110, 104), (126, 99), (137, 110), (139, 123), (124, 132),
      (116, 125)], coat_0, ink, 2)
poly([(121, 104), (130, 106), (135, 116), (128, 126), (119, 123)], coat_2)
poly([(126, 104), (132, 111), (131, 119), (125, 122)], coat_4)
poly([(126, 126), (140, 121), (144, 137), (138, 146), (128, 142)], coat_0, ink, 2)
poly([(128, 128), (138, 125), (141, 137), (135, 142), (130, 140)], coat_2)
poly([(135, 126), (139, 128), (141, 136), (137, 138)], coat_3)
line([(134, 140), (140, 138)], coat_4, 2)
poly([(130, 141), (142, 139), (144, 148), (131, 150)], cloth_2, coat_0)
rect((134, 142, 141, 144), cloth_4)
poly([(133, 150), (142, 148), (145, 158), (139, 163), (131, 159)], coat_0, ink)
poly([(135, 152), (141, 151), (143, 157), (139, 160), (134, 158)], coat_2)
rect((140, 159, 143, 162), skin_1)

# Lapels, diagonal leather straps, belt and map pouch.
poly([(78, 101), (87, 108), (85, 127), (78, 145), (70, 130),
      (72, 115)], coat_1, coat_0, 2)
poly([(77, 104), (84, 110), (81, 129), (77, 136), (73, 126)], coat_3)
line([(76, 105), (81, 112), (78, 128)], coat_5, 2)
poly([(115, 102), (125, 112), (122, 133), (115, 146), (109, 128),
      (109, 111)], coat_1, coat_0, 2)
poly([(117, 105), (122, 113), (119, 132), (116, 137), (113, 126)], coat_3)
line([(118, 107), (121, 114), (117, 130)], coat_5, 2)
line([(68, 112), (83, 126), (91, 143)], gold_0, 5)
line([(67, 109), (83, 124), (93, 142)], coat_4, 2)
rect((75, 118, 80, 122), metal_0)
rect((76, 119, 79, 121), gold_2)
rect((82, 131, 86, 135), metal_0)
rect((83, 132, 85, 134), metal_2)
rect((79, 148, 119, 157), coat_0)
rect((81, 150, 117, 155), coat_2)
line([(81, 150), (115, 150)], coat_4, 2)
rect((94, 149, 105, 157), metal_0)
rect((96, 151, 103, 155), gold_1)
rect((98, 152, 101, 154), coat_0)
rect((117, 140, 129, 156), coat_0)
rect((119, 142, 127, 153), coat_2)
line([(119, 143), (126, 143)], coat_4, 1)
rect((122, 146, 124, 149), gold_1)

# Diamond community badge, arm vial and buckles. Each is only a few clustered
# pixels but color and placement are stable identity signals at small size.
poly([(117, 118), (125, 125), (118, 133), (111, 126)], metal_0, coat_0, 1)
poly([(117, 120), (123, 125), (117, 130), (113, 125)], teal_2)
poly([(117, 122), (120, 125), (117, 128), (115, 125)], teal_4)
rect((116, 124, 118, 126), cloth_4)
rect((139, 122, 145, 135), metal_0)
rect((140, 125, 144, 132), teal_1)
rect((141, 125, 143, 127), teal_4)
rect((139, 122, 145, 124), metal_2)
rect((139, 133, 145, 135), gold_0)
rect((131, 137, 136, 139), metal_1)
rect((61, 129, 66, 132), gold_1)

# Neck and south-facing scarf coils (drawn over lapels).
poly([(88, 87), (108, 87), (109, 103), (85, 103)], skin_0, coat_0, 1)
poly([(90, 88), (106, 88), (106, 99), (90, 100)], skin_2)
rect((92, 90, 104, 96), skin_3)
poly([(83, 95), (94, 100), (107, 98), (116, 93), (118, 104),
      (110, 116), (95, 122), (82, 112), (78, 104)], teal_0, coat_0, 2)
poly([(82, 98), (93, 103), (108, 101), (116, 97), (114, 105),
      (107, 111), (93, 115), (83, 108)], teal_2)
poly([(85, 99), (93, 103), (107, 102), (114, 99), (110, 105),
      (94, 109), (84, 105)], teal_3)
line([(82, 108), (93, 115), (105, 112)], teal_1, 3)
line([(88, 102), (96, 106), (109, 104)], teal_4, 1)
poly([(94, 115), (108, 111), (103, 124), (97, 130), (91, 120)], teal_1, teal_0, 1)
line([(99, 117), (98, 124)], teal_3, 2)

# Face, ears, eyebrows, eyes, cheek, nose and smile. Highlights are chunky
# enough to remain after downsampling to a 52px logical silhouette.
poly([(82, 66), (92, 62), (105, 64), (115, 72), (114, 87),
      (106, 96), (91, 97), (80, 89), (77, 75)], skin_0, coat_0, 2)
poly([(82, 71), (91, 66), (105, 67), (112, 73), (110, 88),
      (104, 94), (92, 94), (83, 88), (80, 77)], skin_2)
poly([(84, 73), (91, 69), (99, 68), (97, 84), (89, 91), (83, 85)], skin_3)
poly([(100, 68), (109, 72), (110, 84), (104, 91), (99, 91)], skin_1)
rect((78, 78, 81, 85), skin_1)
rect((113, 77, 116, 84), skin_1)
rect((79, 79, 81, 83), skin_3)
rect((113, 79, 115, 82), skin_3)
line([(83, 79), (89, 77), (94, 78)], hair_1, 2)
line([(101, 78), (107, 76), (111, 78)], hair_1, 2)
rect((85, 80, 92, 83), cloth_4)
rect((102, 80, 109, 83), cloth_4)
rect((87, 79, 91, 83), ink)
rect((104, 79, 108, 83), ink)
rect((89, 80, 90, 81), teal_3)
rect((106, 80, 107, 81), teal_3)
rect((85, 83, 93, 84), skin_1)
rect((101, 83, 109, 84), skin_1)
line([(97, 80), (95, 86), (99, 88)], skin_0, 1)
rect((94, 87, 97, 88), skin_4)
line([(91, 91), (97, 92), (104, 90)], skin_0, 1)
rect((94, 92, 101, 92), skin_3)
rect((83, 86, 87, 87), skin_4)

# Layered low, windswept short hair. Several separated tufts preserve the
# male silhouette; the female's ponytail shape is intentionally absent.
poly([(70, 72), (73, 64), (82, 62), (83, 58), (92, 61), (98, 56),
      (108, 61), (116, 58), (122, 66), (126, 70), (121, 78),
      (115, 80), (111, 74), (102, 75), (98, 80), (91, 74),
      (80, 81), (77, 75), (71, 79)], hair_0, ink, 1)
poly([(73, 68), (82, 64), (87, 61), (94, 65), (100, 59),
      (109, 64), (116, 61), (121, 67), (118, 72), (110, 70),
      (103, 72), (97, 76), (89, 71), (81, 76), (76, 74)], hair_1)
poly([(73, 69), (82, 65), (86, 62), (91, 65), (82, 72),
      (76, 75), (69, 74)], hair_2)
poly([(87, 65), (97, 58), (103, 61), (98, 70), (92, 75), (87, 73)], hair_2)
poly([(105, 63), (113, 62), (120, 68), (118, 72), (112, 69),
      (103, 73)], hair_2)
poly([(80, 68), (87, 63), (90, 65), (83, 71), (77, 73)], hair_3)
poly([(94, 63), (98, 59), (101, 62), (96, 70), (92, 72)], hair_3)
poly([(108, 64), (112, 63), (117, 67), (113, 68), (104, 69)], hair_3)
line([(77, 68), (83, 65), (87, 64)], hair_4, 1)
line([(94, 65), (99, 60)], hair_4, 1)
line([(107, 65), (113, 64)], hair_4, 1)
# Angular bangs and two outward tips break the hair into readable clumps.
poly([(78, 72), (86, 66), (89, 72), (86, 80), (81, 83)], hair_1, hair_0, 1)
poly([(91, 69), (99, 65), (102, 69), (99, 81), (94, 76)], hair_1, hair_0, 1)
poly([(104, 67), (112, 68), (114, 75), (108, 79), (104, 74)], hair_1, hair_0, 1)
poly([(73, 72), (69, 75), (65, 73), (69, 69), (75, 68)], hair_1, hair_0, 1)
poly([(118, 68), (125, 70), (128, 76), (122, 74), (117, 76)], hair_1, hair_0, 1)
line([(82, 71), (86, 68), (87, 72)], hair_4, 1)
line([(96, 70), (99, 68), (98, 74)], hair_3, 1)
line([(110, 70), (112, 73)], hair_4, 1)

# A few select finishing pixels, placed deliberately for material separation.
rect((72, 118, 74, 120), coat_5)
rect((124, 114, 126, 116), coat_5)
rect((67, 129, 69, 130), coat_5)
rect((130, 129, 132, 131), coat_5)
rect((78, 156, 79, 158), gold_1)
rect((124, 150, 125, 151), gold_2)
line([(78, 199), (83, 198)], coat_4, 1)
line([(112, 199), (117, 200)], coat_4, 1)

assert im.size == (192, 224)
bbox = im.getbbox()
assert bbox is not None and bbox[1] == 56 and bbox[3] == 209, bbox
assert im.getpixel((0, 0))[3] == 0
OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT)
print(f"WROTE {OUT} bbox={bbox} foot=(96,208) visible_height=152")
