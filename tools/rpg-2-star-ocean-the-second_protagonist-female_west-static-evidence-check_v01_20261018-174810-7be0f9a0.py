"""Verify west static artifact/current source/native report and actual gameplay captures."""
from pathlib import Path
import hashlib,json,os,re,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/female-west-static-v01'
PROOF=OUT/'rpg-2-star-ocean-the-second_protagonist-female_west-static-evidence-manifest_v01_20261018-174753-9b21bd7f.json'
def long(p):
 s=str(Path(p).resolve());pre=chr(92)*2+'?'+chr(92)
 return pre+s if os.name=='nt' and not s.startswith(pre) else s
def read(p):return Path(long(p)).read_bytes()
def sha(b,text=False):return hashlib.sha256(b.replace(bytes([13,10]),bytes([10])) if text else b).hexdigest()
def main():
 p=json.loads(read(PROOF))
 for source,value in p['sources'].items():assert sha(read(ROOT/source),True)==value,source
 for source,value in p['protectedGameSource'].items():
  assert sha(read(ROOT/source),True)==value,source
  assert sha(subprocess.check_output(['git','show',p['baseCommit']+':'+source],cwd=ROOT),True)==value,source
 for path,value in p['capturesAndLog'].items():assert sha(read(ROOT/path))==value,path
 artifact=json.loads(read(next(OUT.glob('*west-static-manifest*.json'))))
 for value in artifact['files'].values():assert sha(read(ROOT/value['file']))==value['sha256'],value['file']
 assert sha(read(ROOT/artifact['source']),True)==artifact['sourceSha256TextLf']
 assert sha(read(ROOT/artifact['containerWriter']),True)==artifact['containerWriterSha256TextLf']
 assert artifact['bounds']==[24,8,58,103] and artifact['opaquePixels']==2273 and artifact['logicalBodyHeight']==48
 assert sha(read(ROOT/artifact['paletteSource']))==p['approvedV8Sha256']==artifact['paletteSourceSha256']
 assert sha(read(ROOT/p['nativeReport']))==p['nativeReportSha256']
 native=json.loads(read(ROOT/p['nativeReport']));assert native['passed']==native['total']==13 and not native['artApproved']
 assert native['sourceSha256TextLf']==artifact['sourceSha256TextLf']
 report=json.loads(read(next((OUT/'captures').glob('*capture-report*.json'))));assert report['checks']==14 and len(report['captures'])==12 and not report['artApproved'] and not report['motionApproved']
 assert report['sourceSha256']==artifact['files']['png']['sha256']
 assert {c['scene'] for c in report['captures']}=={'city-bright','annex-room2-dark'} and {c['language'] for c in report['captures']}=={'en','zh'}
 for c in report['captures']:
  file=OUT/'captures'/c['file'];assert sha(read(file))==c['sha256'];assert list(Image.open(long(file)).size)==c['window']
  if c['variant']=='west1280':assert c['bodyHeight']==96 and c['exactTexels']==c['opaqueTexels']==2273
  else:assert c['bodyHeight']==48
 for log in OUT.glob('*gameplay-log*.txt'):
  text=read(log).decode('utf-8-sig');assert not re.search(r'(?m)^(SCRIPT ERROR|ERROR|.*FAIL)',text);assert 'FEMALE_WEST_CAPTURE PASS checks=14 captures=12' in text
 print('FEMALE WEST EVIDENCE PASS: source/artifact hashes, approved palette, native13, actualGodot14/12captures,48logicalpx/2273texelfidelity, defaults unchanged; unapproved static-only')
if __name__=='__main__':main()
