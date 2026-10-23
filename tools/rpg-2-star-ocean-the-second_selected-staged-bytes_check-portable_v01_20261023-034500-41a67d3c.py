"""Compare the exact selected Git index blobs in one batch, including binary assets."""
from pathlib import Path
import json,subprocess,sys,hashlib,os
R=Path(__file__).resolve().parents[1]
paths=json.loads((R/sys.argv[1]).read_bytes())
assert len(paths)==len(set(paths))
index=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=R).decode().split('\0')[:-1]
assert set(index)==set(paths),'Index contains missing or unrelated paths'
stream=subprocess.check_output(['git','cat-file','--batch'],input=''.join(':'+p+'\n' for p in paths).encode(),cwd=R)
offset=0
for p in paths:
 end=stream.index(b'\n',offset);header=stream[offset:end].split();assert len(header)==3 and header[1]==b'blob',(p,header)
 size=int(header[2]);start=end+1;data=stream[start:start+size];assert stream[start+size:start+size+1]==b'\n';offset=start+size+1
 local_path=(R/p).resolve()
 local=(Path('\\\\?\\'+str(local_path)) if os.name=='nt' else local_path).read_bytes()
 assert hashlib.sha256(data).digest()==hashlib.sha256(local).digest(),p
assert offset==len(stream)
print('ALL_SELECTED_STAGED_RAW_BYTES_PASS',len(paths))
