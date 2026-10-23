"""Trace the active ordinary-default exploration sets used by the M8 city (read-only)."""
import hashlib
import json
import os
import re
import sys

GAME = "/home/kel/projects/worlds-between/repo/game"
REGS = {
    "protagonist-male": "data/mexplore23/rpg-2-star-ocean-the-second_protagonist-male_explore-sprite-set-registry_unapproved-mexplore23-v01_20261021-162551-15fcefc2.json",
    "protagonist-female": "data/hsea-front17/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-222654-e8633039.json",
    "liang-xu": "data/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-sprite-set-registry_unapproved-lexplore28-v01_20261021-194350-4041cca1.json",
}


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def local(base_dir, ref):
    if ref.startswith("res://"):
        return os.path.join(GAME, ref[len("res://"):])
    return os.path.normpath(os.path.join(base_dir, ref))


for actor, rel in REGS.items():
    reg = os.path.join(GAME, rel)
    data = json.load(open(reg, encoding="utf-8"))
    print(actor, "registry", rel, "sha256", sha(reg))
    set_path = local(os.path.dirname(reg), data["actors"][actor])
    sdata = json.load(open(set_path, encoding="utf-8"))
    print("  set", os.path.relpath(set_path, GAME), "sha256", sha(set_path))
    print("  set_id", sdata.get("set_id"), "density", sdata["density"], "frame_size", sdata["frame_size"], "pivot", sdata["pivot"])
    for action in ("idle", "walk"):
        counts = {f: len(sdata["actions"][action][f]) for f in ("south", "west", "north", "east")}
        first = local(os.path.dirname(set_path), sdata["actions"][action]["south"][0]["file"])
        print("   ", action, counts, "south[0]", os.path.relpath(first, GAME), "sha256", sha(first)[:16])
