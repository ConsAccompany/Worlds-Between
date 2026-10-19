"""One finite Pixelorama CLI export; independent raster equality, raw diagnostics retained."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, io, json, os, re, subprocess, uuid, sys
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PRIMARY=ROOT.parents[1]
TAG='20261019-181125-65fc9cd8'
SLUG='rpg-2-star-ocean-the-second'
OUT=ROOT/'outputs/sentry-native-app-v01'
STOP=PRIMARY/'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
EXE=PRIMARY/'work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'
PACKAGE=ROOT/'game/assets/enemies/sentry-editable-v01'

def extended(p):
    return '\\\\?\\'+str(p.resolve())

def read(p):
    with open(extended(p),'rb') as f:return f.read()

def write(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    with open(extended(p),'wb') as f:f.write(b)

def sha(b):return hashlib.sha256(b).hexdigest()
def rgba(b):return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))

def run(source,label):
    if STOP.exists():raise SystemExit('GLOBAL STOP: no export started')
    temp=ROOT/'work'/('sentry-app-'+uuid.uuid4().hex[:8]);temp.mkdir()
    for d in ['app','local','export']:(temp/d).mkdir()
    input_=temp/f'{SLUG}_sentry_native-cli-input-{label}_v01_{TAG}.pxo'
    original=read(source);write(input_,original)
    target=temp/'export'/f'{SLUG}_sentry_native-cli-{label}_v01_{TAG}.png'
    env=dict(os.environ);env['APPDATA']=str(temp/'app');env['LOCALAPPDATA']=str(temp/'local')
    args=[str(EXE),'--headless','--quit','--','--export','-o',str(target),str(input_)]
    started=datetime.now(timezone.utc).isoformat()
    try:
        p=subprocess.run(args,env=env,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        stdout,stderr,exit_=p.stdout,p.stderr,p.returncode;timed_out=False
    except subprocess.TimeoutExpired as e:
        stdout,stderr,exit_=e.stdout or b'',e.stderr or b'',None;timed_out=True
    ended=datetime.now(timezone.utc).isoformat()
    for kind,data in [('stdout',stdout),('stderr',stderr)]:
        write(OUT/f'{SLUG}_sentry_native-cli-{label}-{kind}_v01_{TAG}.log',data)
    files=sorted((temp/'export').glob('*.png'));rows=[]
    for i,f in enumerate(files):
        data=read(f);a=rgba(data)
        dest=OUT/f'{SLUG}_sentry_native-cli-{label}-export-{i+1:02d}_v01_{TAG}.png';write(dest,data)
        rows.append({'file':dest.relative_to(ROOT).as_posix(),'nativeFileName':f.name,'sha256':sha(data),'size':[a.shape[1],a.shape[0]]})
    combined=(stdout+b'\n'+stderr).decode('utf-8','replace')
    markers=[s for s in combined.splitlines() if re.search(r'ERROR|WARNING|SCRIPT ERROR|Shader compilation failed',s,re.I)]
    return {'source':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(original),'sourceUnchanged':read(source)==original,
            'inputCopyUnchanged':read(input_)==original,'command':args,'startUtc':started,'endUtc':ended,'exit':exit_,
            'timeout':timed_out,'diagnosticMarkers':markers,'cleanAppSuccess':exit_==0 and not markers,
            'exports':rows,'temp':str(temp)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if '--control-only' in sys.argv:
        path=OUT/f'{SLUG}_sentry_native-cli-report_v01_{TAG}.json'
        report=json.loads(read(path))
        control=ROOT/'outputs/battle-static-v15/rpg-2-star-ocean-the-second_female-battle-idle-right_editable-layers_unapproved-v15_20261018-210446-e9ee7d3b.pxo'
        assert sha(read(control))=='72b03201d33dfa7ea9f815122908f8f8dacf03b939c2838192bb8540e7b7f947'
        result=run(control,'unchanged-control')
        expected=ROOT/'outputs/battle-static-v15/rpg-2-star-ocean-the-second_female-battle-idle-right_static-native0p65_unapproved-v15_20261018-210446-abde2095.png'
        result['nativeRasterPass']=result['exit']==0 and len(result['exports'])==1 and np.array_equal(rgba(read(ROOT/result['exports'][0]['file'])),rgba(read(expected)))
        result['sameDiagnosticMarkersAsCandidate']=result['diagnosticMarkers']==report['candidate']['diagnosticMarkers']
        report['control']=result;report['toolSha256']=sha(read(Path(__file__)))
        write(path,(json.dumps(report,indent=2)+'\n').encode())
        print(json.dumps({'controlRasterPass':result['nativeRasterPass'],'sameDiagnostics':result['sameDiagnosticMarkersAsCandidate'],'cleanAppSuccess':result['cleanAppSuccess']},indent=2))
        return
    source=next(PACKAGE.glob('*.pxo'));strip=next(PACKAGE.glob('*strip*.png'))
    result=run(source,'candidate');expected=rgba(read(strip));exported=[rgba(read(ROOT/r['file'])) for r in result['exports']]
    one_strip=len(exported)==1 and exported[0].shape==expected.shape and np.array_equal(exported[0],expected)
    # Default CLI may export independent numbered timeline frames rather than a spritesheet.
    individual=len(exported)==21 and all(a.shape==(62,112,4) and np.array_equal(a,expected[:,i*112:(i+1)*112]) for i,a in enumerate(exported))
    result.update({'expectedStrip':strip.relative_to(ROOT).as_posix(),'expectedStripSha256':sha(read(strip)),
                   'oneStripExact':one_strip,'all21IndependentFramesExact':individual,
                   'nativeRasterPass':result['exit']==0 and (one_strip or individual) and result['sourceUnchanged'] and result['inputCopyUnchanged']})
    report={'task':'Sentry existing v2 editable PXO native CLI open/export','candidate':result,'control':None,
            'nativeGuiSaveAsTested':False,'artApprovalGranted':False,'runtimeChanged':False,
            'toolSha256':sha(read(Path(__file__)))}
    path=OUT/f'{SLUG}_sentry_native-cli-report_v01_{TAG}.json'
    write(path,(json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({'report':str(path),'nativeRasterPass':result['nativeRasterPass'],'cleanAppSuccess':result['cleanAppSuccess'],'exports':len(exported),'diagnostics':result['diagnosticMarkers']},indent=2))
    if not result['nativeRasterPass']:raise SystemExit(1)

if __name__=='__main__':main()
