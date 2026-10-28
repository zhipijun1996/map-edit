"""Check shipped videos, immutable archive parts and current evidence status."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(web_only=False):
 videos=0;parts=0
 for folder in(ROOT/'generation/videos').iterdir():
  m=json.loads((folder/'manifest.json').read_text());assert m['playback_speed']==1 and m['physics_hz']==60 and m['approved_offline']==0
  for entry in m['clips']+[m['combined']]:
   p=folder/entry['file'];assert p.stat().st_size==entry['bytes']and sha(p)==entry['sha256'];assert p.read_bytes()[4:8]==b'ftyp';videos+=1
  for c in m['clips']:
   r=c['engine_result'];assert r['module_sha256']==c['module_sha256']and r['safe']and r['hp']==5 and r['stable_frames']>=6
  for c in m['clips']:
   if 'native_trace'in c:
    t=c['native_trace'];p=folder/t['file'];assert p.stat().st_size==t['bytes']and sha(p)==t['sha256'];trace=json.loads(p.read_text());assert trace['module_sha256']==c['module_sha256']and len(trace['frames'])==t['frames']and t['max_position_error']==0 and t['cell_events_match_at_every_frame']
   if 'map_notes'not in c:continue
   link=c['map_notes'];doc_path=(folder/link['file']).resolve();diagram=(folder/link['diagram']).resolve();assert doc_path.is_relative_to(ROOT/'generation')and diagram.is_relative_to(ROOT/'generation');assert sha(doc_path)==link['contentSha256']and sha(diagram)==link['diagramSha256'];doc=json.loads(doc_path.read_text());contract=doc['generationContract'];assert doc['id']==link['id']and contract['contentVersion']==link['contentVersion'];source=contract['generation']['source'];assert source['moduleSha256']==c['module_sha256']or any(r['routeId']==link.get('routeId')and r['moduleSha256']==c['module_sha256']for r in source.get('routeCases',[]))
 for manifest in ([] if web_only else (ROOT/'pcg/archives').glob('*/manifest.json')):
  m=json.loads(manifest.read_text());total=0;whole=hashlib.sha256()
  for entry in m['parts']:
   p=manifest.parent/entry['file'];assert p.parent==manifest.parent and p.stat().st_size==entry['bytes']and sha(p)==entry['sha256'];whole.update(p.read_bytes());total+=p.stat().st_size;parts+=1
  assert total==m['archive_bytes']and whole.hexdigest()==m['archive_sha256']
 summary=json.loads((ROOT/'pcg/results/guided-landing-v2/summary.json').read_text());assert all(a['parents']==6 for a in summary['arms'].values());assert summary['approved_offline']==0 and summary['human_video_feedback']==0
 result=dict(videos_verified=videos,archive_parts_verified=parts,
  archive_validation='NOT_RUN_WEB_ONLY' if web_only else ('VERIFIED' if parts else 'NO_ARCHIVES_PRESENT'),
  scope='Published video, contract and trace bytes only; archived experiments not checked; no human review approval' if web_only else 'Shipped bytes and recorded finite evidence; no human review approval')
 print(json.dumps(result));return result
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--web-only',action='store_true',help='Validate published video/contract/trace bytes; explicitly omit offline PCG archives')
 run(parser.parse_args().web_only)
