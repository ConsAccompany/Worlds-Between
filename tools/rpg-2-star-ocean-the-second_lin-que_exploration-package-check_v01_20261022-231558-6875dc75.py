#!/usr/bin/env python3
"""Independent Lin Que exploration package check; UNAPPROVED source only.
Usage: --root R --out O --manifest source.json. Exit 0 pass, 1 fail, 2 pending."""
import argparse, copy, hashlib, json, os, struct, sys
from pathlib import Path
P="rpg-2-star-ocean-the-second"; A="lin-que"; TAG="20261022-231558-6875dc75"; DIRS=("south","west","north","east"); PH=tuple(f"phase{i}" for i in range(12)); REP=f"{P}_{A}_exploration-package-check_v01_{TAG}.json"
def ext(p): q=Path(p).absolute(); return Path("\\\\?\\"+str(q)) if os.name=="nt" and not str(q).startswith("\\\\?\\") else q
def sha(p):
 with p.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()
def dim(p):
 b=p.read_bytes()[:24]; return struct.unpack(">II",b[16:24]) if b[:8]==b"\x89PNG\r\n\x1a\n" and b[12:16]==b"IHDR" else None
def rp(f): q=Path(str(f).replace("\\","/")); return ext(q if q.is_absolute() else R/q)
def fr(q): return isinstance(q,dict) and isinstance(q.get("file"),str) and isinstance(q.get("sha256") or q.get("rawsha256"),str)
def cf(d,base,e,label,png=False,need=True):
 f=d.get("file") if isinstance(d,dict) else None
 if not isinstance(f,str): e.append(label+": file missing"); return None
 p=base/Path(str(f).replace("\\","/")) if not Path(str(f).replace("\\","/")).is_absolute() else rp(f)
 if not p.is_file(): e.append(label+": missing "+str(p)); return None
 h=d.get("sha256") or d.get("rawsha256"); e.append(label+": sha256 mismatch") if need and (not isinstance(h,str) or sha(p)!=h.lower()) else None
 if png and dim(p)!=(80,112): e.append(label+": not 80x112")
 return p
def refs(o,e):
 if isinstance(o,dict):
  if isinstance(o.get("file"),str) and o["file"].lower().endswith((".png",".pxo",".ora")): e.append("source ref lacks sha256") if not (o.get("sha256") or o.get("rawsha256")) else cf(o,R,e,"ref",o["file"].lower().endswith(".png"),True)
  for v in o.values(): refs(v,e)
 elif isinstance(o,list):
  for v in o: refs(v,e)
def source(m):
 e=[]; c=m.get("contract") if isinstance(m.get("contract"),dict) else {}; ds=m.get("directions") if isinstance(m.get("directions"),dict) else {}
 if m.get("visual_id")!=A: e.append("visual_id != lin-que")
 for k,v in (("cell",[80,112]),("pivot",[40,104]),("density",2),("logical_height",48)): e.append(f"contract.{k} != {v}") if c.get(k)!=v else None
 if set(ds)!=set(DIRS): e.append("directions are not exactly south/west/north/east")
 for d in DIRS:
  x=ds.get(d) if isinstance(ds.get(d),dict) else {}; idle=x.get("idle") if isinstance(x.get("idle"),list) else []; walk=x.get("walk") if isinstance(x.get("walk"),list) else []; st=x.get("stop_bridges") if isinstance(x.get("stop_bridges"),dict) else {}
  if not fr(x.get("static")): e.append(d+": static ref")
  if len(idle)!=4 or not all(fr(q) for q in idle): e.append(d+": idle count/ref")
  if len(walk)!=12 or not all(fr(q) for q in walk): e.append(d+": walk count/ref")
  if set(st)!=set(PH): e.append(d+": stop_bridges keys")
  for i,b in enumerate([st.get(k) for k in PH]):
   if not isinstance(b,list) or len(b)!=4 or not all(isinstance(q,dict) for q in b): e.append(f"{d}/phase{i}: bridge shape"); continue
   if b[0].get("ref")!="walk" or b[0].get("index")!=i or b[0].get("k")!=0: e.append(f"{d}/phase{i}: start endpoint")
   if b[-1].get("ref")!="idle" or b[-1].get("index")!=0 or b[-1].get("k")!=1: e.append(f"{d}/phase{i}: end endpoint")
   if not all(fr(q) and q["file"].lower().endswith(".png") for q in b[1:3]): e.append(f"{d}/phase{i}: middle PNGs")
   try: ks=[float(q["k"]) for q in b[1:3]]
   except (KeyError,TypeError,ValueError): ks=[]
   if len(ks)!=2 or abs(ks[0]-1/3)>1e-6 or abs(ks[1]-2/3)>1e-6: e.append(f"{d}/phase{i}: middle k")
  if fr(x.get("static")) and idle and fr(idle[0]):
   sp,ip=rp(x["static"]["file"]),rp(idle[0]["file"])
   if not (sp.is_file() and ip.is_file() and sp.read_bytes()==ip.read_bytes()): e.append(d+": static != idle0")
 refs(m,e); return e
def runtime(rs,rs_path,src):
 e=[]; base=rs_path.parent; acts=rs.get("actions") if isinstance(rs.get("actions"),dict) else {}
 if rs.get("schema")!="worlds-between.exploration-sprite-set.v1": e.append("runtime schema")
 if rs.get("actor_id")!=A: e.append("runtime actor_id != lin-que")
 if rs.get("density")!=2 or rs.get("frame_size")!=[80,112] or rs.get("pivot")!=[40,104]: e.append("runtime native contract")
 if set(acts)!={"idle","walk"}: e.append("runtime actions shape")
 for act,n in (("idle",4),("walk",12)):
  ar=acts.get(act) if isinstance(acts.get(act),dict) else {}
  if set(ar)!=set(DIRS): e.append(act+": dirs")
  for d in DIRS:
   arr=ar.get(d) if isinstance(ar.get(d),list) else []
   if len(arr)!=n: e.append(f"{act}/{d}: count")
   for i,f in enumerate(arr):
    q=cf(f,base,e,f"{act}/{d}/{i}",png=True,need=False); dur=f.get("duration_ms") if isinstance(f,dict) else None
    if type(dur) is not int or not 40<=dur<=2000: e.append(f"{act}/{d}/{i}: duration")
    x=src.get("directions",{}).get(d,{}).get(act,[]) if isinstance(src.get("directions"),dict) else []
    sp=rp(x[i]["file"]) if i<len(x) and fr(x[i]) else None
    if q and sp and sp.is_file() and q.read_bytes()!=sp.read_bytes(): e.append(f"{act}/{d}/{i}: runtime copy")
 return e
def registry(reg,rs_name):
 e=[]; actors=reg.get("actors") if isinstance(reg.get("actors"),dict) else {}
 if reg.get("schema")!="worlds-between.exploration-sprite-set-registry.v1": e.append("registry schema")
 if set(actors)!={A} or Path(str(actors.get(A,""))).name!=rs_name: e.append("registry is not Lin-only")
 return e
ap=argparse.ArgumentParser(); ap.add_argument("--root",default="."); ap.add_argument("--out",required=True); ap.add_argument("--manifest",required=True); a=ap.parse_args(); R=ext(a.root); O=ext(a.out); M=Path(a.manifest); M=ext(M if M.is_absolute() else R/M); O.mkdir(parents=True,exist_ok=True)
def finish(rep,code): (O/REP).write_text(json.dumps(rep,indent=2)+"\n",encoding="utf8"); print(rep["status"],rep.get("error","")); raise SystemExit(code)
if not M.is_file(): finish({"tag":TAG,"status":"PENDING","passed":False,"error":"source manifest missing; no placeholder/pass","manifest":str(M)},2)
try: m=json.loads(M.read_text(encoding="utf8"))
except Exception as ex: finish({"tag":TAG,"status":"FAIL","passed":False,"error":"malformed source manifest: "+repr(ex),"manifest":str(M)},1)
pkg=m.get("package") if isinstance(m.get("package"),dict) else {}; errs={"source":source(m)}; rs_path=rp(pkg.get("sprite_set","")); rs={}
try:
 if not rs_path.is_file() or pkg.get("sprite_set_sha256")!=sha(rs_path): raise ValueError("runtime sprite set missing/hash")
 rs=json.loads(rs_path.read_text(encoding="utf8")); errs["runtime"]=runtime(rs,rs_path,m)
except Exception as ex: errs["runtime"]=["runtime unavailable: "+repr(ex)]
reg_path=rp(pkg.get("registry","")); rgerr=[]
try:
 if not reg_path.is_file(): raise FileNotFoundError("registry missing")
 rgerr=registry(json.loads(reg_path.read_text(encoding="utf8")),rs_path.name)
except Exception as ex: rgerr=["registry unavailable: "+repr(ex)]
errs["registry"]=rgerr; controls={}
bm=copy.deepcopy(m)
try: bm["directions"]["south"]["static"]["sha256"]="0"*64
except (KeyError,TypeError): pass
controls["bad_hash_refused"]=bool(source(bm)); br=copy.deepcopy(rs)
try: br["actions"]["idle"]["south"][0]["duration_ms"]=39
except (KeyError,IndexError,TypeError): pass
controls["bad_duration_refused"]=bool(rs and runtime(br,rs_path,m)); bg={"actors":{A:"other-sprite-set.json"}} if reg_path.is_file() else {}; controls["bad_actor_refused"]=bool(bg and registry(bg,rs_path.name))
checks=[{"id":k,"ok":not v,"errors":v[:12]} for k,v in errs.items()]+[{"id":"control."+k,"ok":v} for k,v in controls.items()]; ok=all(c["ok"] for c in checks)
rep={"tag":TAG,"status":"PASS" if ok else "FAIL","passed":ok,"manifest":str(M),"checks":checks,"control_mode":"in-memory only; no source mutation","scope":"UNAPPROVED technical package parity only; no art/motion/contact/default approval"}
(O/REP).write_text(json.dumps(rep,indent=2)+"\n",encoding="utf8"); print("LINQUE_EXPLORE_PACKAGE",sum(c["ok"] for c in checks),"/",len(checks)); print("FAILURES",[c["id"] for c in checks if not c["ok"]]); raise SystemExit(0 if ok else 1)
