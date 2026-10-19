"""Independent archive/pixel/semantic-source inspection of existing v2 editability."""
import argparse, copy, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, uuid, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
TAG='20261019-220550-2b708970'
ROLES=['legs','mechanisms','body','claw','eye','impact']
ROLE_PART={'far_rear_leg':'legs','far_front_leg':'legs','near_rear_leg':'legs','near_front_leg':'claw','belly':'mechanisms','dome':'mechanisms','shell':'body','far_fin':'body','cheek_plate':'body','eye_housing':'eye','eye':'eye'}
REPS={'idle':0,'move':4,'windup':12,'strike':14,'hit':16,'defeat':20}
checks=[]
def ck(key,value):checks.append({'key':key,'pass':bool(value)})
def ext(p):
    p=str(Path(p).resolve())
    return p if os.name!='nt' or p.startswith('\\\\?\\') else '\\\\?\\'+p
def read(p):return Path(ext(p)).read_bytes()
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def image(raw):return Image.open(io.BytesIO(raw)).convert('RGBA')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ext(path));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def normalized_manifest(value):
    value=copy.deepcopy(value)
    value.pop('createdAtUtc',None)
    value['builder'].pop('path',None);value['helper'].pop('path',None);value['package'].pop('directory',None)
    return value
def run(package):
    manifest_path=next(package.glob('*manifest*.json'));m=json.loads(read(manifest_path))
    source_manifest_path=ROOT/m['source']['manifest']['path'];s=json.loads(read(source_manifest_path))
    ck('ten-package-files',len(list(package.iterdir()))==10 and len(m['package']['files'])==10)
    ck('all-filenames-rule',all(re.fullmatch(r'rpg-2-star-ocean-the-second_sentry_editable-native(?:-[a-z-]+)?_v01_\d{8}-\d{6}-[a-f0-9]{8}\.(?:py|pxo|ora|png|json)',p.name) for p in package.iterdir()))
    ck('package-flags-unapproved-offdefault',m['artAccepted'] is False and m['runtimeIntegrated'] is False and m['artAcceptanceCount']==0 and m['provenance']['guiReliabilityClaimed'] is False)
    source_manifest_git=subprocess.check_output(['git','show','HEAD:'+m['source']['manifest']['path']],cwd=ROOT)
    source_manifest_working=read(source_manifest_path)
    ck('source-manifest-canonical-git-raw-sha',hashlib.sha256(source_manifest_git).hexdigest()==m['source']['manifest']['sha256'])
    ck('source-manifest-working-crlf-only-bridge',source_manifest_working.replace(b'\r\n',b'\n')==source_manifest_git)
    ck('source-existing-v2',s['revision']=='m8-anim-v02' and 'ffefdc6f' in source_manifest_path.name and s['frameCount']==21 and s['cellSize']==[112,62])
    strip=image(read(ROOT/s['file']))
    ck('source-strip-sha',sha(ROOT/s['file'])==s['sha256']==m['source']['strip']['sha256'])
    ck('copied-strip-exact-original-bytes',read(next(package.glob('*strip*.png')))==read(ROOT/s['file']))
    for name,digest in m['artifacts'].items():ck('artifact-raw-sha-'+name,sha(package/name)==digest)
    author_path=ROOT/s['authorScript'];author_raw=read(author_path)
    ck('v2-author-text-lf-source-hash',hashlib.sha256(author_raw.replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest()==s['authorScriptSha256'])
    ck('v2-author-raw-hash',sha(author_path)==m['source']['authorScript']['sha256Bytes'])
    author=load_module('root_existing_sentry_v2_author',author_path)
    for input_name in [s['authorScript'],s['staticAuthorScript'],s['file'],*[entry['file'] for entry in s['frameFiles']]]:
        ck('no-animation-v1-v3-input-'+Path(input_name).name,not re.search(r'anim-v0[13]',input_name))
    expected_seconds={}
    for state,spec in s['states'].items():
        times=[ms/1000 for st,idx,ms,_dx in s['previews']['loopGif3x']['sequence'] if st==state and not(state=='defeat' and idx==20 and ms==900)]
        expected_seconds[state]=spec['frameTime'] if spec['frameTime'] is not None else times[0]
        ck(state+'-source-preview-timing-consistent',all(abs(v-expected_seconds[state])<1e-12 for v in times))
        ck(state+'-manifest-source-indices-and-mode',m['states'][state]['frames']==spec['frames'] and m['states'][state]['mode']==spec['mode'])
    layers_by_frame=[]
    with zipfile.ZipFile(io.BytesIO(read(next(package.glob('*.pxo'))))) as z:
        data=json.loads(z.read('data.json'));native=m['native'];meta=json.loads(data['user_data'])
        ck('pxo-crc-clean',z.testzip() is None)
        ck('pxo-v7-header',data['pxo_version']==7 and data['pixelorama_version']=='v1.2.3-stable' and data['color_mode']==5)
        ck('pxo-size21frames',data['size_x']==112 and data['size_y']==62 and len(data['frames'])==21 and data['fps']==12)
        ck('pxo-six-editable-semantic-layers',[r['name'] for r in data['layers']]==ROLES and all(r['type']==0 and r['visible'] and not r['locked'] and r['opacity']==1 and r['blend_mode']==0 and not r['clipping_mask'] and r['parent']==-1 for r in data['layers']))
        ck('pxo-pivot-source',meta['pivot']==s['runtimeAnchor']==[46,60] and meta['anchorRow']==60 and meta['bodyCenterX']==s['bodyCenterX']==64)
        ck('pxo-source-bindings',meta['sourceManifestSha256']==hashlib.sha256(source_manifest_git).hexdigest() and meta['sourceStripSha256']==s['sha256'])
        ck('pxo-tag-ranges',[(t['name'],t['from'],t['to']) for t in data['tags']]==[(state,min(spec['frames'])+1,max(spec['frames'])+1) for state,spec in s['states'].items()])
        ck('pxo-no-extra-cels',len([name for name in z.namelist() if re.fullmatch(r'image_data/frames/\d+/layer_\d+',name)])==21*6)
        ck('pxo-preview-frame0',image(z.read('preview.png')).tobytes()==strip.crop((0,0,112,62)).tobytes())
        for i,frame in enumerate(data['frames']):
            source_entry=s['frameFiles'][i];source_raw=read(ROOT/source_entry['file']);source=image(source_raw);pixels=np.asarray(source)
            ck(f'f{i}-source-original-sha',hashlib.sha256(source_raw).hexdigest()==source_entry['sha256'])
            ck(f'f{i}-source-strip-cell-equal',source.tobytes()==strip.crop((i*112,0,(i+1)*112,62)).tobytes())
            state=next(state for state,spec in s['states'].items() if i in spec['frames'])
            ck(f'f{i}-duration-fps-seconds',abs(frame['duration']/data['fps']-expected_seconds[state])<1e-12)
            ck(f'f{i}-timeline-index-pivot',m['timeline'][i]['sourceIndex']==i and m['timeline'][i]['state']==state and m['timeline'][i]['pivot']==[46,60])
            ck(f'f{i}-six-cel-editable',len(frame['cels'])==6 and all(c['opacity']==1 and c['z_index']==0 for c in frame['cels']))
            owner=np.full((62,112),-1,dtype=np.int8)
            _state,pose=author.FRAMES[i]
            for part in author.build_parts(pose):
                p=np.asarray(part.layer);mask=p[:,:,3]>0 if p.ndim==3 else p!=0
                # Independent vectorized reconstruction of each painted Part's
                # interior + orthogonal one-pixel outline, retaining topmost ownership.
                footprint=mask.copy();footprint[1:]|=mask[:-1];footprint[:-1]|=mask[1:];footprint[:,1:]|=mask[:,:-1];footprint[:,:-1]|=mask[:,1:]
                owner[footprint]=ROLES.index(ROLE_PART[part.name])
            for x,y,_ in pose['fx']:owner[y,x+author.MARGIN]=ROLES.index('impact')
            ck(f'f{i}-every-opaque-pixel-semantic-owner',np.all(owner[pixels[:,:,3]>0]>=0))
            roles={};coverage=np.zeros((62,112),dtype=np.uint8);composite=Image.new('RGBA',(112,62))
            for li,role in enumerate(ROLES,1):
                raw=z.read(f'image_data/frames/{i+1}/layer_{li}');ck(f'f{i}-{role}-cel-size',len(raw)==112*62*4)
                layer=Image.frombytes('RGBA',(112,62),raw);arr=np.asarray(layer);mask=arr[:,:,3]>0;coverage+=mask
                expected=np.zeros_like(pixels);selection=(owner==li-1)&(pixels[:,:,3]>0);expected[selection]=pixels[selection]
                ck(f'f{i}-{role}-semantic-source-pixels',arr.tobytes()==expected.tobytes())
                ck(f'f{i}-{role}-binary-alpha',set(np.unique(arr[:,:,3]).tolist())<={0,255})
                ck(f'f{i}-{role}-declared-cel-sha',hashlib.sha256(raw).hexdigest()==m['frameCels'][i]['cels'][role]['rgbaSha256'])
                ck(f'f{i}-{role}-not-flattened-copy',raw!=source.tobytes())
                composite.alpha_composite(layer);roles[role]=layer
            ck(f'f{i}-disjoint-exact-opaque-coverage',np.array_equal(coverage,(pixels[:,:,3]>0).astype(np.uint8)))
            ck(f'f{i}-all-composite-pixels-exact-v2',composite.tobytes()==source.tobytes())
            ck(f'f{i}-ground-contact-row60',source.getbbox()[3]==61)
            layers_by_frame.append(roles)
    for state,index in REPS.items():
        path=next(package.glob('*'+state+'-representative*.ora'))
        with zipfile.ZipFile(io.BytesIO(read(path))) as z:
            ck(state+'-ora-crc-clean',z.testzip() is None)
            stack=list(ET.fromstring(z.read('stack.xml')).find('stack'))
            ck(state+'-ora-six-role-stack',[r.attrib['name'] for r in reversed(stack)]==ROLES)
            composite=Image.new('RGBA',(112,62))
            for layer in reversed(stack):
                role=layer.attrib['name'];im=image(z.read(layer.attrib['src']))
                ck(state+'-ora-role-'+role,im.tobytes()==layers_by_frame[index][role].tobytes())
                ck(state+'-ora-visible-origin-'+role,layer.attrib['opacity']=='1.0' and layer.attrib['visibility']=='visible' and layer.attrib['x']=='0' and layer.attrib['y']=='0' and layer.attrib['composite-op']=='svg:src-over')
                composite.alpha_composite(im)
            target=strip.crop((index*112,0,(index+1)*112,62))
            ck(state+'-ora-composite-original-v2',composite.tobytes()==target.tobytes())
            ck(state+'-ora-merged-original-v2',image(z.read('mergedimage.png')).tobytes()==target.tobytes())
    # Rebuild in a fresh ignored peer with explicit authoritative source/helper paths.
    # Full manifest includes wall-clock and package location, so compare those
    # disclosed administrative fields separately; all nine artifact bytes are exact.
    peer=ROOT/'work'/('sentry3-'+uuid.uuid4().hex[:8]);peer.mkdir(parents=True,exist_ok=True)
    builder=next(package.glob('*.py'));target=peer/builder.name
    Path(ext(target)).write_bytes(read(builder))
    helper=ROOT/'game/assets/inputs'/m['helper']['file']
    source_snapshot=ROOT/'work'/('sentrysrc-'+uuid.uuid4().hex[:8])
    inputs=[m['source']['manifest']['path'],s['authorScript'],s['staticAuthorScript'],s['file'],s['staticPilot']['file'],*[entry['file'] for entry in s['frameFiles']]]
    for relative in inputs:
        destination=source_snapshot/relative
        Path(ext(destination.parent)).mkdir(parents=True,exist_ok=True)
        Path(ext(destination)).write_bytes(source_manifest_git if relative==m['source']['manifest']['path'] else read(ROOT/relative))
    # Source bytes use extended reads. The short subprocess script argv stays
    # ordinary Windows form so its provenance relpath sees the same drive type.
    result=subprocess.run([sys.executable,str(target),'--source-root',str(source_snapshot),'--helper',str(helper)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    ck('rebuild-process-exit',result.returncode==0)
    for name in m['artifacts']:ck('rebuild-artifact-exact-'+name,(peer/name).is_file() and read(peer/name)==read(package/name))
    rebuilt=json.loads(read(peer/manifest_path.name)) if (peer/manifest_path.name).is_file() else None
    ck('rebuild-manifest-semantic-equality-excluding-disclosed-admin-fields',rebuilt is not None and normalized_manifest(rebuilt)==normalized_manifest(m))
    report={'recordedAtUtc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'tag':TAG,'sourceRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'packageManifestRawSha256':sha(manifest_path),'sourceManifestWorkingRawSha256':sha(source_manifest_path),'sourceManifestCanonicalGitRawSha256':hashlib.sha256(source_manifest_git).hexdigest(),'sourceManifestLineEndingBridge':'Canonical working legacy manifest is CRLF, canonical Git blob is LF; normalizing only CRLF reproduces exact declared source bytes. Ignored rebuild snapshot uses exact canonical Git blob; existing working legacy file unchanged.','artifactRawSha256':{p.name:sha(p) for p in package.iterdir()},'checks':checks,'count':len(checks),'failed':[c['key'] for c in checks if not c['pass']],'rebuildStdout':result.stdout,'rebuildStderr':result.stderr,'rebuildManifestByteEquality':read(peer/manifest_path.name)==read(manifest_path),'manifestAdministrativeFieldsExcluded':['createdAtUtc','builder.path','helper.path','package.directory'],'limitations':['No Pixelorama application launch, native export, playback or GUI save/reopen inspected.','Move/windup native timing linearizes source preview; actual runtime remains distance/progress driven; no runtime retiming or motion approval.','Six layers contain only visible source raster pixels; hidden overwritten geometry is unrecoverable and no new shadow is invented.','Existing static-v01 palette/compositor dependency of v2 author is preserved; no animation-v1 or animation-v3 inputs were used.','Manifest clock/location metadata is not byte-deterministic; all nine binary/source artifacts rebuild byte-identically.'],'artApproved':False,'runtimeChanged':False,'unscoredEditabilityGap':True}
    out=ROOT/'outputs/sentry-editable-v01';out.mkdir(parents=True,exist_ok=True)
    (out/f'rpg-2-star-ocean-the-second_sentry_native-independent-report_v01_{TAG}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SENTRY_NATIVE_INDEPENDENT',len(checks)-len(report['failed']),'/',len(checks),'PASS' if not report['failed'] else 'FAIL',report['failed'])
    if not report['failed']:
        destination=ROOT/'game/assets/enemies/sentry-editable-v01';destination.mkdir(parents=True,exist_ok=True)
        for p in package.iterdir():Path(ext(destination/p.name)).write_bytes(read(p))
        print('Copied ONLY ten verified package files into canonical checkout.')
    return bool(report['failed'])
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);args=parser.parse_args();sys.exit(run(args.package))
