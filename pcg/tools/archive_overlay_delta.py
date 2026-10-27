"""Lossless overlay deltas against a byte-verified archived parent PCK."""
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
from pcg.tools.restore_archive import open_parts
from pcg.module_library.paths import REPO
from pcg.module_library.paths import write
PARENT='results/shape-search-web-transport-v2/overlay.3b09aef68f37.pck'
def parent_files(tools):
 sys.path.insert(0,str(tools));from check_web_bundle import Pack
 with open_parts('shape-search-results-v1')as z:
  index=json.loads(z.read('PCG-ARCHIVE-INDEX.json'));i=index[PARENT];b=z.read(i.get('archive_entry',PARENT));assert hashlib.sha256(b).hexdigest()==i['sha256']
 with tempfile.NamedTemporaryFile(suffix='.pck')as t:
  t.write(b);t.flush();p=Pack(Path(t.name));return {k:p.read(k)for k in p.entries},i['sha256']
def run(folder,tools,restore=False):
 folder=Path(folder);base,parent_sha=parent_files(tools)
 from check_web_bundle import Pack
 from pcg.prototype.packaging_v3.overlay_pack import write_pack
 manifest=json.loads((folder/'overlay-manifest.json').read_text());pack=folder/manifest['overlay']['pack'];delta=folder/'pack-delta.json'
 if restore:
  d=json.loads(delta.read_text());assert d['parent_sha256']==parent_sha
  for k in d['removed']:base.pop(k)
  for k,v in d['changed'].items():
   b=(folder/v['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==v['sha256'];base[k]=b
  if pack.exists():assert hashlib.sha256(pack.read_bytes()).hexdigest()==d['pack_sha256'];return
  m=write_pack(pack,base);assert m['sha256']==d['pack_sha256'];return
 if delta.exists():raise ValueError('immutable_delta_exists')
 p=Pack(pack);files={k:p.read(k)for k in p.entries};changed={}
 for k,b in files.items():
  if base.get(k)==b:continue
  h=hashlib.sha256(b).hexdigest();rel='pack-objects/'+h;q=folder/rel;q.parent.mkdir(exist_ok=True);q.write_bytes(b);changed[k]=dict(file=rel,sha256=h)
 removed=sorted(set(base)-set(files));expected=hashlib.sha256(pack.read_bytes()).hexdigest()
 # Rebuild in a temporary file before deleting any original pack.
 test={k:b for k,b in base.items()if k not in removed};test.update({k:files[k]for k in changed})
 with tempfile.TemporaryDirectory()as tmp:m=write_pack(Path(tmp)/'test.pck',test)
 assert m['sha256']==expected==manifest['overlay']['sha256']
 write(delta,dict(parent_archive='shape-search-results-v1',parent_path=PARENT,parent_sha256=parent_sha,pack_sha256=expected,removed=removed,changed=changed,exact_reconstruction_verified=True))
 size=pack.stat().st_size;pack.unlink();print(json.dumps(dict(folder=str(folder),reclaimed=size,delta_bytes=sum((folder/v['file']).stat().st_size for v in changed.values()))))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--game-tools',required=True);p.add_argument('--restore',action='store_true');a=p.parse_args();run(a.folder,a.game_tools,a.restore)
