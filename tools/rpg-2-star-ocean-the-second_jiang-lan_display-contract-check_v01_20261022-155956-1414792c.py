#!/usr/bin/env python3
"""Independent Jiang Lan display40 exact-crop/manifest check.

Usage: python <this> --root R --manifest M --out O
Exit 0 pass, 1 failure, 2 producer artifact pending. One JSON report under O.
Read-only for source/producer files; no motion/default/art-approval claims.
"""
import argparse, copy, hashlib, io, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

P="rpg-2-star-ocean-the-second"; T="20261022-155956-1414792c"; A="jiang-lan"
SS="bbddf46f3c1370742c86d1934e36adf7969e5f43a4e6d67ddbf9ba8d44902e4a"
SD=(1915,821); R=(0,0,480,630); CS=(480,630)
DEF=f"outputs/{P}_jiang-lan_character-sheet_hairstyle-v02_20261013-161317-c21bd255.png"
REP=f"{P}_{A}_display-contract-report_v01_{T}.json"
SCOPE=("independent exact-crop/manifest contract only; no motion, default-use, "
       "runtime, or art-approval claims; source and producer files are read-only")


def sh(b): return hashlib.sha256(b).hexdigest()
def g(c,n,o,d=""): c.append({"id":n,"ok":bool(o),"detail":d})
def ins(r,p):
    try: p.resolve().relative_to(r.resolve()); return True
    except ValueError: return False


def pick(r,b,v,pr=False):
    """Resolve one explicit metadata path; no recursive/glob lookup."""
    if not v: return None
    q=Path(str(v).replace("\\","/"))
    for f in ([r,b] if pr else [b,r]):
        x=(q if q.is_absolute() else f/q).resolve()
        if ins(r,x) and x.is_file(): return x
    return None


def blocks(m,keys):
    o=[]
    for k in keys:
        v=m.get(k)
        if isinstance(v,dict): o.append((k,v))
        elif isinstance(v,str): o.append((k,{"path":v}))
    return o


def acts(m):
    o=[]
    for k in ("actor_id","subject"):
        if isinstance(m.get(k),str): o.append((k,m[k]))
    for k in ("actor","identity"):
        v=m.get(k)
        if isinstance(v,str): o.append((k,v))
        elif isinstance(v,dict):
            for s in ("actor_id","id","subject"):
                if isinstance(v.get(s),str): o.append((f"{k}.{s}",v[s]))
    return o


def sb(m): return blocks(m,("source","source_ref","source_sheet","source_pin"))
def ib(m):
    o=blocks(m,("image","crop_png","output"))
    for i,v in enumerate(m.get("outputs") or []):
        if isinstance(v,dict) and str(v.get("path","")).lower().endswith(".png"): o.append((f"outputs[{i}]",v))
    d=m.get("display")
    if isinstance(d,dict) and d.get("image_path"): o.append(("display",{"path":d["image_path"],"sha256":d.get("image_sha256")}))
    return o


def rect(v):
    if isinstance(v,str):
        n=[int(x) for x in re.findall(r"-?\d+",v)]
        return tuple(n[:4]) if len(n)>=4 else None
    if isinstance(v,(list,tuple)) and len(v)>=4:
        try: return tuple(int(x) for x in v[:4])
        except (TypeError,ValueError): return None
    if isinstance(v,dict):
        for k in ("rect","source_rect","source_crop","bounds"):
            if k in v and rect(v[k]): return rect(v[k])
        if all(k in v for k in ("left","top","right","bottom")): return tuple(int(v[k]) for k in ("left","top","right","bottom"))
        if all(k in v for k in ("x","y","width","height")):
            x,y,w,h=(int(v[k]) for k in ("x","y","width","height")); return (x,y,x+w,y+h)
        if all(k in v for k in ("left","top","width","height")):
            x,y,w,h=(int(v[k]) for k in ("left","top","width","height")); return (x,y,x+w,y+h)
    return None


def cb(m): return [(k,m[k]) for k in ("source_crop","crop_rect","crop","source_rect","sourceRectangle") if m.get(k) is not None]


def val(m,ibyt,sbyt):
    c=[]
    try: s=Image.open(io.BytesIO(sbyt)).convert("RGBA")
    except Exception as e: return {"ok":False,"checks":[{"id":"source.decode","ok":False,"detail":repr(e)}]}
    a=acts(m); g(c,"actor.present",bool(a)); g(c,"actor.jiang-lan",bool(a) and all(v==A for _,v in a),str(a))
    for l,b in sb(m):
        h=b.get("sha256") or b.get("rawsha256") or b.get("file_sha256")
        if h: g(c,f"{l}.source-sha",h==SS,str(h))
        if "width" in b or "height" in b: g(c,f"{l}.source-size",(b.get("width"),b.get("height"))==SD,str((b.get("width"),b.get("height"))))
    g(c,"source.actual-sha",sh(sbyt)==SS,sh(sbyt)); g(c,"source.actual-size",s.size==SD,str(s.size))
    pr=[(l,rect(b)) for l,b in cb(m)]; pr=[(l,r) for l,r in pr if r]
    g(c,"crop.declared",bool(pr)); g(c,"crop.consistent",bool(pr) and all(r==pr[0][1] for _,r in pr),str(pr))
    r=pr[0][1] if pr else None; g(c,"crop.rect",r==R,f"{r} != {R}")
    if r:
        g(c,"crop.size",(r[2]-r[0],r[3]-r[1])==CS,str((r[2]-r[0],r[3]-r[1])))
        g(c,"crop.bounds",0<=r[0]<r[2]<=s.width and 0<=r[1]<r[3]<=s.height,f"{r} in {s.size}")
    for l,b in cb(m):
        if not isinstance(b,dict): continue
        for k in ("resampled","resample"):
            if k in b: g(c,f"{l}.{k}",b[k] is False,str(b[k]))
        if isinstance(b.get("method"),str): g(c,f"{l}.method",not any(x in b["method"].lower() for x in ("resample","resize","scale")),b["method"])
    try: i=Image.open(io.BytesIO(ibyt)).convert("RGBA")
    except Exception as e: g(c,"image.decode",False,repr(e)); i=None
    if i: g(c,"image.size",i.size==CS,str(i.size))
    nh=0
    for l,b in ib(m):
        h=b.get("sha256") or b.get("rawsha256") or b.get("file_sha256")
        if h: nh+=1; g(c,f"{l}.image-sha",h==sh(ibyt),str(h))
        if "width" in b or "height" in b: g(c,f"{l}.image-size",(b.get("width"),b.get("height"))==CS,str((b.get("width"),b.get("height"))))
    g(c,"image.manifest-sha-present",nh>0)
    if i and r and 0<=r[0]<r[2]<=s.width and 0<=r[1]<r[3]<=s.height:
        e=s.crop(r); g(c,"pixels.exact-crop",i.size==e.size and i.tobytes()==e.tobytes(),f"{e.size[0]*e.size[1]} pixels")
    else: g(c,"pixels.exact-crop",False,"no in-bounds rect")
    return {"ok":all(x["ok"] for x in c),"checks":c}


def pa(m):
    h=0
    for k in ("actor_id","subject"):
        if isinstance(m.get(k),str): m[k]="wrong-actor"; h=1
    for k in ("actor","identity"):
        v=m.get(k)
        if isinstance(v,str): m[k]="wrong-actor"; h=1
        elif isinstance(v,dict):
            for s in ("actor_id","id","subject"):
                if isinstance(v.get(s),str): v[s]="wrong-actor"; h=1
    if not h: m["actor_id"]="wrong-actor"


def ph(m,p):
    h=0
    for k in ("image","crop_png","output"):
        v=m.get(k)
        if isinstance(v,dict):
            for n in ("sha256","rawsha256","file_sha256"):
                if n in v: v[n]="0"*64; h=1
    for v in m.get("outputs") or []:
        if isinstance(v,dict) and str(v.get("path","")).lower().endswith(".png"):
            for n in ("sha256","rawsha256","file_sha256"):
                if n in v: v[n]="0"*64; h=1
    d=m.get("display")
    if isinstance(d,dict) and "image_sha256" in d: d["image_sha256"]="0"*64; h=1
    if not h:
        m.setdefault("image",{})
        if isinstance(m["image"],dict): m["image"]["sha256"]="0"*64
        else: m["image"]={"path":p,"sha256":"0"*64}


def pc(m):
    s=[0,0,SD[0]+1,R[3]]; h=0
    for k in ("source_crop","crop_rect","crop","source_rect","sourceRectangle"):
        if k in m: m[k]=list(s); h=1
    if not h: m["source_crop"]=list(s)


def fx(n,m,ibyt,sbyt,fn):
    x=copy.deepcopy(m); fn(x)
    try:
        q=val(x,ibyt,sbyt); return {"id":n,"refused":not q["ok"],"failedChecks":[z["id"] for z in q["checks"] if not z["ok"]][:6]}
    except Exception as e: return {"id":n,"refused":True,"failedChecks":[f"exception:{e!r}"]}


def wr(o,r):
    o.mkdir(parents=True,exist_ok=True); p=o/REP
    with open(p,"w",encoding="utf-8",newline="\n") as f: f.write(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    return p


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",default="."); ap.add_argument("--manifest",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(argv); root=Path(a.root).resolve(); mp=Path(a.manifest)
    if not mp.is_absolute(): mp=root/mp
    mp=mp.resolve(); out=Path(a.out).resolve()
    rep={"schema":"jiang-display-contract-check/v1","project":P,"subject":A,
         "purpose":"display-contract-check","variant":"v01",
         "run":{"timestamp_utc":datetime.now(timezone.utc).isoformat(),"unique_id":T},
         "expected":{"actor_id":A,"source_sha256":SS,"source_dimensions":list(SD),
                     "source_rect":list(R),"output_dimensions":list(CS),"resample":False},
         "scope":SCOPE,"manifest_path":str(mp)}
    if not mp.is_file():
        rep.update(status="PENDING",exit_code=2,checks=[],negativeFixtures={},
                   reason="producer manifest/artifact absent; not inspected")
        p=wr(out,rep); print(json.dumps({"status":"PENDING","exit":2,"report":str(p)})); return 2
    rep["manifest_sha256"]=sh(mp.read_bytes())
    try: m=json.loads(mp.read_bytes())
    except Exception as e:
        rep.update(status="FAIL",exit_code=1,negativeFixtures={},reason=f"manifest parse: {e!r}",
                   checks=[{"id":"manifest.parse","ok":False,"detail":repr(e)}])
        p=wr(out,rep); print(json.dumps({"status":"FAIL","exit":1,"report":str(p)})); return 1

    ds=next((b.get("path") for _,b in sb(m) if b.get("path")),None)
    sp=pick(root,mp.parent,ds,True) or (root/DEF).resolve()
    ip=next((pick(root,mp.parent,b.get("path")) for _,b in ib(m) if b.get("path")),None)
    bad=[]
    if not sp.is_file() or not ins(root,sp): bad.append({"id":"source.file","ok":False,"detail":f"unresolved {ds!r}"})
    if ip is None or not ip.is_file(): bad.append({"id":"image.file","ok":False,"detail":"unresolved image"})
    if bad:
        rep.update(status="FAIL",exit_code=1,checks=bad,negativeFixtures={},reason="artifact path failure")
        p=wr(out,rep); print(json.dumps({"status":"FAIL","exit":1,"report":str(p),"failures":[x["id"] for x in bad]})); return 1

    sbyt=sp.read_bytes(); ibyt=ip.read_bytes(); before=sh(sbyt)
    q=val(m,ibyt,sbyt); c=q["checks"]
    if ds: g(c,"source.path",sp==pick(root,mp.parent,ds,True),ds)
    else: g(c,"source.path",sp.name==Path(DEF).name,"fixed documented fallback")
    g(c,"source.unchanged",before==sh(sp.read_bytes())==SS,f"before={before}")
    fs={"wrong-hash":fx("wrong-hash",m,ibyt,sbyt,lambda x:ph(x,ip)),
        "wrong-actor":fx("wrong-actor",m,ibyt,sbyt,pa),
        "out-of-bounds-crop":fx("out-of-bounds-crop",m,ibyt,sbyt,pc)}
    after=sh(sp.read_bytes()); g(c,"fixtures.source-unchanged",after==before==SS,f"after={after}")
    ok=all(x["ok"] for x in c) and all(x["refused"] for x in fs.values())
    rep.update(status="PASS" if ok else "FAIL",exit_code=0 if ok else 1,checks=c,negativeFixtures=fs,
               source={"path":str(sp.relative_to(root)),"sha256":after,"dimensions":list(SD)},
               image={"path":str(ip.relative_to(root)),"sha256":sh(ibyt),"dimensions":list(CS)},
               reason="contract verified" if ok else "contract check failed")
    p=wr(out,rep)
    print(json.dumps({"status":rep["status"],"exit":rep["exit_code"],"report":str(p),
                      "failures":[x["id"] for x in c if not x["ok"]]+[f"fixture:{k}" for k,v in fs.items() if not v["refused"]]}))
    return rep["exit_code"]


if __name__=="__main__": raise SystemExit(main())
