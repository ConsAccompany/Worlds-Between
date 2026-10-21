"""Compare selected working files with exact staged Git blobs in two Git calls; never stage or mutate sources.
Usage: python -I <this> --paths-file <newline relative paths> --report <unique project JSON>
"""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def raw(path):
    return Path("\\\\?\\"+str(path.resolve())).read_bytes() if os.name=="nt" else path.read_bytes()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--paths-file",required=True);ap.add_argument("--report",required=True);a=ap.parse_args()
    paths=sorted(set(Path(a.paths_file).read_text(encoding="utf8").splitlines()));start=time.monotonic()
    if not paths:raise ValueError("selected paths empty")
    for p in paths:
        q=(ROOT/p).resolve()
        if Path(p).is_absolute() or not q.is_relative_to(ROOT):raise ValueError("selected path escapes checkout")
    index={}
    for record in subprocess.run(["git","ls-files","--stage","-z"],cwd=ROOT,capture_output=True,check=True).stdout.split(b"\0"):
        if not record:continue
        meta,p=record.split(b"\t",1);mode,oid,stage=meta.split()
        if stage!=b"0":raise ValueError("unmerged index")
        index[p.decode("utf8")]=oid.decode()
    missing=[p for p in paths if p not in index]
    if missing:raise ValueError("paths are not staged: "+str(missing[:5]))
    objects=subprocess.run(["git","cat-file","--batch"],cwd=ROOT,input=("\n".join(index[p] for p in paths)+"\n").encode(),capture_output=True,check=True).stdout
    pos=0;rows=[]
    for p in paths:
        end=objects.index(b"\n",pos);oid,kind,size=objects[pos:end].split();size=int(size);pos=end+1
        staged=objects[pos:pos+size];pos+=size+1
        if kind!=b"blob" or oid.decode()!=index[p]:raise ValueError("unexpected staged object")
        working=raw(ROOT/p);rows.append({"file":p,"gitBlob":index[p],"sha256":hashlib.sha256(staged).hexdigest(),"bytes":len(staged),"rawEqual":staged==working})
    result={"result":"PASS" if all(x["rawEqual"] for x in rows) else "FAIL","generatedAt":datetime.now(timezone.utc).isoformat(),"gitCalls":2,"elapsedSeconds":round(time.monotonic()-start,3),"hashMode":"raw working bytes vs exact staged blob bytes, no text normalization","files":rows}
    target=Path(a.report).resolve()
    if not target.is_relative_to(ROOT):raise ValueError("report outside checkout")
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(result["result"],len(rows),"files",result["elapsedSeconds"],"seconds",[x["file"] for x in rows if not x["rawEqual"]][:10]);return 0 if result["result"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
