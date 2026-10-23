"""Native export equality and bounded test-only source-fit captures; no adoption/approval."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys
from PIL import Image
R=Path(__file__).resolve().parents[1];P=R.parents[1];TAG='20261022-222500-3d61c74e'
O=R/'outputs/lin58d/root';O.mkdir(parents=True,exist_ok=True)
def fs(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
def sha(p):return hashlib.sha256(fs(p).read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
sp=importlib.util.spec_from_file_location('checked',R/'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py');runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner)
proof={'base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'native':[],'fits':[],'scope':'editable static sources and deterministic test-only overlays; no motion, ordinary integration, GUI SaveAs/reopen or art approval'}
fit_only='--fit-only' in sys.argv
if fit_only:
 old=json.loads((O/f'rpg-2-star-ocean-the-second_lin-que_native-and-fit-proof_v01_{TAG}.json').read_text(encoding='utf8'))
 proof['native']=old['native'];proof['priorFits']=old['fits']
 proof['priorFitLimitation']='World-coordinate WDC overlay was partly behind HUD; rerendered in viewport CanvasLayer. Original captures retained, not final visual evidence.'
def write():(O/f'rpg-2-star-ocean-the-second_lin-que_native-and-fit-proof_v01_{TAG}.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
for d in ('south','west','north','east'):
 folder=R/'game/assets/characters/lin-que-native-v01'/d;ms=list(fs(folder).glob('*manifest*.json'));assert len(ms)==1,(d,'missing manifest')
 m=json.loads(ms[0].read_text(encoding='utf8'));source=folder/m['files']['png']['file'];im=Image.open(fs(source)).convert('RGBA')
 for fmt in (() if fit_only else ('pxo','ora')):
  src=folder/m['files'][fmt]['file'];before=sha(src);out=O/(d+'-'+fmt);out.mkdir(exist_ok=True);assert not list(out.glob('*.png'))
  target=out/f'rpg-2-star-ocean-the-second_lin-que_{d}-{fmt}-native-flat_unapproved-v01_{TAG}.png'
  cmd=[str(P/'work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe'),'--headless','--quit','--','--export','-o',str(target),str(src)]
  log=out/f'rpg-2-star-ocean-the-second_lin-que_{d}-{fmt}-native-log_v01_{TAG}.log'
  r=subprocess.run(cmd,cwd=R,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=65,creationflags=subprocess.CREATE_NO_WINDOW)
  text=r.stdout+r.stderr;log.write_text(text,encoding='utf8');flats=list(out.glob('*.png'));exact=len(flats)==1 and Image.open(flats[0]).convert('RGBA').size==im.size and Image.open(flats[0]).convert('RGBA').tobytes()==im.tobytes()
  if len(flats)==1 and flats[0]!=target:flats[0].rename(target)
  diagnostics=[x for x in text.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:'))]
  e={'direction':d,'format':fmt,'command':cmd,'exitCode':r.returncode,'flatExact':exact,'inputUnchanged':sha(src)==before,'diagnostics':diagnostics,'cleanApplication':not diagnostics and r.returncode==0,'guiSaveReopenVerified':False,'sourceSha256':before,'log':rel(log),'export':rel(target)}
  proof['native'].append(e);write();assert r.returncode==0 and exact and e['inputUnchanged'],e
 fit=O/(d+'-fit-r2' if fit_only else d+'-fit');fit.mkdir(exist_ok=True);script=R/'tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd'
 cmd=[str(P/'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),'--path',str(R/'game'),'--resolution','640x360','--script',str(script),'--',str(source),str(fit),TAG,'lin-que']
 log=fit/f'rpg-2-star-ocean-the-second_lin-que_{d}-source-fit-log_v01_{TAG}.log';r=runner.run_checked(cmd,80,['JIANG37_SOURCE_FIT_PASS captures=4'],log);r.pop('log',None)
 proof['fits'].append({'direction':d,'command':cmd,'result':r,'log':rel(log),'captures':[rel(x) for x in fit.glob('*.png')],'scriptSha256':sha(script),'sourceSha256':sha(source)});write();assert r['passed'],r
print('LIN58D_NATIVE_EXACT',sum(x['flatExact'] for x in proof['native']),'/',len(proof['native']))
print('LIN58D_FIT_PASS',sum(x['result']['passed'] for x in proof['fits']),'/',len(proof['fits']))
