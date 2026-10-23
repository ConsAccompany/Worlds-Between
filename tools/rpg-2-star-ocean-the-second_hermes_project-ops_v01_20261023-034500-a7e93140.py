"""Portable takeover helpers. No account credentials, inference, or destructive restore."""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, zipfile
ROOT=Path(__file__).resolve().parents[1]
HOME=ROOT.parent
INDEX='assets/handoff/rpg-2-star-ocean-the-second_project-assets_complete-index_v01_20261021-180244-718e0ceb.json'
LEDGER='outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json'
def sha_file(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def safe_target(root,rel):
    root=Path(root).resolve();relative=Path(rel)
    if relative.is_absolute() or '..' in relative.parts:raise ValueError('unsafe relative path')
    p=root/relative
    if not p.resolve().is_relative_to(root):raise ValueError('path escapes destination')
    q=p
    while q!=root:
        if q.is_symlink():raise ValueError('symlink destination refused')
        q=q.parent
    return p
def verify_archive():
    d=json.loads((ROOT/INDEX).read_text(encoding='utf8'));count=0
    for b in d['bundles']:
        p=ROOT/b['repositoryPath'];assert p.stat().st_size==b['bytes'];assert sha_file(p)==b['sha256']
    zips={}
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for a in d['assets']:
            st=a['storage']
            if st['type']=='git':
                proc.stdin.write((a['gitBlob']+'\n').encode());proc.stdin.flush()
                header=proc.stdout.readline().split();assert len(header)==3 and header[1]==b'blob',a['id']
                n=int(header[2]);h=hashlib.sha256();left=n
                while left:
                    data=proc.stdout.read(min(left,1024*1024));assert data;h.update(data);left-=len(data)
                assert proc.stdout.read(1)==b'\n';digest=h.hexdigest();size=n
            else:
                bundle=st.get('package') or st.get('bundle')
                member=st.get('member')
                if bundle not in zips:
                    match=next(b for b in d['bundles'] if b['name']==bundle or b['repositoryPath']==bundle)
                    zips[bundle]=zipfile.ZipFile(ROOT/match['repositoryPath'])
                with zips[bundle].open(member) as f:
                    h=hashlib.sha256();size=0
                    for data in iter(lambda:f.read(1024*1024),b''):h.update(data);size+=len(data)
                digest=h.hexdigest()
            assert digest==a['sha256'] and size==a['bytes'],a['id'];count+=1
    finally:
        proc.stdin.close();proc.wait(timeout=10)
        for z in zips.values():z.close()
    print(json.dumps({'historicalAssetsVerified':count,'archivePackagesVerified':len(d['bundles']),'method':'Frozen gitBlob objects and exact ZIP members, not mutable current working paths.'}))
def vault_index():return json.loads((HOME/'vault/index.json').read_text(encoding='utf8'))
def verify_vault():
    d=vault_index();count=0;total=0
    for o in d['objects']:
        p=safe_target(HOME,o['storage']);assert p.is_file(),o['sha256'];assert p.stat().st_size==o['bytes'];assert sha_file(p)==o['sha256'];count+=1;total+=o['bytes']
    print(json.dumps({'vaultUniqueFilesVerified':count,'bytes':total,'originalOccurrences':d['summary']['eligibleOccurrences'],'scanErrors':len(d['errors'])}))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['doctor','archive-verify','vault-verify','asset-find','asset-restore']);p.add_argument('--match');p.add_argument('--alias');p.add_argument('--destination');a=p.parse_args()
    if a.command=='archive-verify':return verify_archive()
    if a.command=='vault-verify':return verify_vault()
    if a.command in ['asset-find','asset-restore']:
        d=vault_index();found=[o for o in d['objects'] if any((a.match or a.alias or '').lower() in s.lower() for s in o['aliases'])]
        if a.command=='asset-find':
            for o in found:print(json.dumps({k:o[k] for k in ['sha256','bytes','aliases','storage']}))
            return
        if not a.alias or not a.destination:raise ValueError('--alias and --destination required')
        found=[o for o in found if a.alias in o['aliases']]
        if len(found)!=1:raise ValueError('exact alias is missing or ambiguous')
        o=found[0];source=safe_target(HOME,o['storage']);assert sha_file(source)==o['sha256'];dest=Path(a.destination).resolve()
        if dest==ROOT or ROOT in dest.parents:raise ValueError('restore to a separate workspace, never the active repository')
        dest.mkdir(parents=True,exist_ok=True);target=safe_target(dest,a.alias);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert sha_file(target)==o['sha256'],'refusing overwrite of different bytes'
        else:
            with target.open('xb') as f,source.open('rb') as src:shutil.copyfileobj(src,f)
        print(target);return
    result={'root':str(ROOT),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'tools':{x:shutil.which(x) for x in ['git','node','ffmpeg','xvfb-run','gh']},'ledger':json.loads((ROOT/LEDGER).read_text(encoding='utf8'))['computed']}
    for name,path in [('godot',HOME/'tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64'),('pixelorama',HOME/'tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64')]:result['tools'][name]=str(path) if path.is_file() else None
    result['vaultPresent']=(HOME/'vault/index.json').exists();print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
