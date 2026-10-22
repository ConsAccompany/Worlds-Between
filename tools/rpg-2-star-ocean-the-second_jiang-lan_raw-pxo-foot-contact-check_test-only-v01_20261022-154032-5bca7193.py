from pathlib import Path
import json,zipfile,numpy as np,hashlib
R=Path(__file__).resolve().parents[1];s=json.loads(next((R/'outputs/jexplore39').glob('*source-manifest*.json')).read_bytes());allrec={}
for d,bank in s['directions'].items():
 z=zipfile.ZipFile(R/bank['pxo']['file']);dj=json.loads(z.read('data.json'));names=[x['name'] for x in dj['layers']];side=d in ['west','east'];rec=[]
 def foot(fi,k):
  lay='boots' if k=='A' or not side or fi==1 else 'far-limbs';i=names.index(lay)+1;a=np.frombuffer(z.read(f'image_data/frames/{fi+1}/layer_{i}'),np.uint8).reshape(112,80,4)[:,:,3].copy();a[:69]=0
  if not side:
   if k=='A':a[:,40:]=0
   else:a[:,:40]=0
  elif fi==1:
   f=(np.arange(80)-40)*(-1 if d=='west' else 1);a[:,f>5 if k=='A' else f<=5]=0
  ys,xs=np.nonzero(a)
  if len(ys)==0:return {'grounded':False,'row':-1}
  row=int(ys.max());span=xs[ys==row];return {'grounded':row==103,'row':row,'minx':int(span.min()),'maxx':int(span.max())}
 for p in range(12):rec.append({k:foot(5+p,k) for k in ['A','B']})
 pairs=[]
 for p in range(11):
  for k in ['A','B']:
   a,b=rec[p][k],rec[p+1][k]
   if a['grounded'] and b['grounded']:
    sign=-1 if d=='west' else 1;slip=max(abs(sign*(b[q]-a[q])+11.2) for q in ['minx','maxx']) if side else 11.2;pairs.append({'phase':p,'foot':k,'sourceWorldSlip':round(slip,5)})
 stops=[]
 for p in range(12):
  frames=[5+p,17+2*p,18+2*p,1]
  for k in ['A','B']:
   for x,y in zip(frames,frames[1:]):
    a,b=foot(x,k),foot(y,k)
    if a['grounded'] and b['grounded']:
     diff=(max(abs(b[q]-a[q]) for q in ['minx','maxx']) if k=='A' else abs(b['minx' if d=='west' else 'maxx']-a['minx' if d=='west' else 'maxx'])) if side else abs(b['row']-a['row']);stops.append(diff)
 worst=max(x['sourceWorldSlip'] for x in pairs);claimed=s['contact_check'][d]['walk_max_world_slip_src_at_40ms_boundaries'];assert abs(worst-claimed)<.0001,(d,worst,claimed);assert max(stops)==0,(d,max(stops));allrec[d]={'actualRawPxoFootSamples':rec,'worldSlipAt40msBoundariesSourceMax':worst,'worldSlipLogicalMax':worst/2,'authorReportExactlyMatchesIndependentPixels':True,'stopGroundedFootMovementSourceMax':max(stops),'stopTransitionsChecked':len(stops),'notFootlockPass':True,'stopAnchorScope':'near toe and heel; far toe only, neutral far heel is occluded; full far-foot outline changes up to9sourcepx at neutral handoff and is not a fixed-anchor claim'};print('INDEPENDENT_CONTACT',d,'WORST_SRC',worst,'STOP',max(stops))
allrec['_checkerSha256Raw']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();o=R/'outputs/jexplore39/root';(o/'rpg-2-star-ocean-the-second_jiang-lan_raw-pxo-independent-foot-contact-proof_v01_20261022-154032-5bca7193.json').write_bytes((json.dumps(allrec,indent=2)+'\n').encode())
