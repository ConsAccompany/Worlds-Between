"""Verify delivered source/evidence bindings; ORA diagnostic-clean failures deliberately remain failures."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib,json,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/'tools/rpg-2-star-ocean-the-second_female-idle-four-direction_native-build_unapproved-v01_20261018-175418-34294d7d.py'
spec=spec_from_file_location('idle_evidence_author',AUTHOR);a=module_from_spec(spec);spec.loader.exec_module(a)
PROOF=a.OUT/f'{a.SLUG}_female-idle-four_evidence-manifest_v01_{a.STAMP}-{a.ID}.json'
def main():
 p=json.loads(a.read(PROOF))
 assert not p['artApproved'] and not p['motionApproved'] and not p['runtimeIntegrated']
 for path,h in p['sources'].items():assert a.sha(a.read(ROOT/path),True)==h,path
 for path,h in p['protectedGameSource'].items():
  assert a.sha(a.read(ROOT/path),True)==h,path
  assert a.sha(subprocess.check_output(['git','show',p['baseCommit']+':'+path],cwd=ROOT),True)==h,path
 assert a.sha(a.read(ROOT/p['manifest']))==p['manifestSha256']
 m=json.loads(a.read(ROOT/p['manifest']))
 assert m['sourceSha256TextLf']==a.sha(a.read(AUTHOR),True)
 for path,h in m['helpers'].items():assert a.sha(a.read(ROOT/path),True)==h
 assert len(m['phases'])==12 and abs(sum(f['seconds'] for f in m['phases'])-4.8)<1e-9
 for direction,row in m['directions'].items():
  assert a.sha(a.read(ROOT/row['file']))==row['sha256']
  assert row['uniqueRgbaPoses']==len({f['files']['png']['sha256'] for f in row['frames']})==8
  for f in [row['pxo'],*[v for phase in row['frames'] for v in phase['files'].values()]]:assert a.sha(a.read(ROOT/f['file']))==f['sha256']
  source=a.rgba(a.read(ROOT/row['file']))
  for i,parts in enumerate(a.poses(source,direction)):
   assert a.png(a.flat(parts))==a.read(ROOT/row['frames'][i]['files']['png']['file'])
 assert a.sha(a.read(ROOT/p['nativeReport']))==p['nativeReportSha256']
 n=json.loads(a.read(ROOT/p['nativeReport']));assert n['manifestSha256']==p['manifestSha256']
 failed=[key for key,value in n['gates'].items() if not value]
 assert n['passed']==34 and n['total']==46 and len(failed)==12 and all('_ora_' in key for key in failed)
 assert len(n['native'])==16 and all(d['exit']==0 and d['allCellsExact'] for d in n['native'])
 assert all(not d['unexpectedDiagnostics'] for d in n['native'] if d['format']=='pxo')
 assert all(d['unexpectedDiagnostics'] for d in n['native'] if d['format']=='ora')
 assert a.sha(a.read(ROOT/p['initialStrictFailure']))==p['initialStrictFailureSha256']
 initial=json.loads(a.read(ROOT/p['initialStrictFailure']));assert (initial['passed'],initial['total'])==(30,42)
 for path,h in p['boundFiles'].items():assert a.sha(a.read(ROOT/path))==h,path
 control=json.loads(a.read(ROOT/p['oraControl']));assert control['exit']==0 and 'get_child' in control['stderr'] and 'ensure_control_visible' in control['stderr']
 for path in p['captureReports']:
  report=json.loads(a.read(ROOT/path));fps=report['fps'];assert report['manifestSha256']==p['manifestSha256'] and len(report['frames'])==round(20.8*fps)
  assert report['checks']==(1924 if fps==30 else 3796) and report['canvas']==[640,360]
  assert all(abs(f['delta']-1/fps)<1e-6 for f in report['frames'])
  assert all(b['processFrame']==q['processFrame']+1 for q,b in zip(report['frames'],report['frames'][1:]))
  assert {f['direction'] for f in report['frames']}=={'south','north','west','east'}
 for movie in p['movies']:
  probe=movie['probe'];assert probe['width']==640 and probe['height']==360 and abs(float(probe['duration'])-20.8)<.001
  report=json.loads(a.read(ROOT/movie['captureReport']))
  assert hashlib.sha256(''.join(f['sha256'] for f in report['frames']).encode()).hexdigest()==movie['inputFramesSha256Digest']
 assert len(p['critical'])==12 and {c['direction'] for c in p['critical']}=={'south','north','west','east'} and {c['phase'] for c in p['critical']}=={0,4,7}
 for c in p['critical']:assert Image.open(a.long(ROOT/c['file'])).size==(640,360)
 print('IDLE FOUR SOURCE PACKAGE PASS: source30/30, animated PXO4/4, exact supplemental ORA exports12/12; strict ORA diagnostic-clean0/12 remains FAILED. Two actual1x movies, twelve criticalPNGs, defaults unchanged; art/fluidity unapproved.')
if __name__=='__main__':main()
