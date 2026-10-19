"""Rebind optimized authored runtime derivatives; never regenerate models using historical copy-only builder.
Original package builder and source entries are preserved under original_builder/source hashes.
Text hashes normalize CRLF to LF only; binary/raw package pins use exact bytes.
"""
from pathlib import Path
import json,hashlib,sys,re
R=Path(sys.argv[1]).resolve()
P=R/'game/data/fexp/rpg-2-star-ocean-the-second_female-complete-explore_package_v01_20261019-184500-f2c0a7e1.json'
G=R/'game/scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd'
j=json.loads(P.read_bytes())
if "original_builder" not in j:
 j["original_builder"]={"path":j["builder"],"sha256_text_lf_v1":j["builder_sha256_text_lf_v1"],"scope":"historical copy/extract provenance; does not reproduce optimized derivatives"}
j["builder"]='tools/rpg-2-star-ocean-the-second_female-complete-explore_optimized-manifest-rebinder_v01_20261019-232829-d1c028ee.py'
j["builder_sha256_text_lf_v1"]=hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n",b"\n")).hexdigest()
j["authored_runtime_derivatives"]={"revision":"fcx-v03 exact render optimization","west":"unchanged","east_north_south":"amended authored runtime copies; historical unchanged-copy assertions do not apply","art_geometry_timing_approval":"unchanged; unapproved optional pilot"}
for e in j["entries"]:
 if "copy_sha256_text_lf_v1" in e:
  e.setdefault("original_copy_sha256_text_lf_v1",e["copy_sha256_text_lf_v1"])
  e["copy_sha256_text_lf_v1"]=hashlib.sha256((R/e["copy"]).read_bytes().replace(b"\r\n",b"\n")).hexdigest()
P.write_text(json.dumps(j,ensure_ascii=False,indent=1)+"\n",encoding="utf-8",newline="\n")
s=G.read_text(encoding="utf-8")
s=re.sub(r'const PINNED_PACKAGE_RAW_SHA256 := "[0-9a-f]+"','const PINNED_PACKAGE_RAW_SHA256 := "'+hashlib.sha256(P.read_bytes()).hexdigest()+'"',s)
G.write_text(s,encoding="utf-8",newline="\n")
print("FEXP_REBIND_OK",hashlib.sha256(P.read_bytes()).hexdigest())
