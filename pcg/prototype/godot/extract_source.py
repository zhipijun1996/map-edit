from pathlib import Path
import subprocess,re,json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=Path('/workspace/gunman-rush-latest'));args=parser.parse_args()
SRC=args.source; DST=Path(__file__).parent
SHA='12f6cb006d7119598e3235f4ca4f7323e4c9d092'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',SHA],cwd=SRC,text=True).splitlines()
cache={}; classes={}
def read(p):
 if p not in cache:
  cache[p]=subprocess.check_output(['git','show',SHA+':'+p],cwd=SRC)
 return cache[p]
for p in paths:
 if p.endswith('.gd') and (p.startswith('scripts/') or p.startswith('assets/')):
  s=read(p).decode(); m=re.search(r'^class_name\s+(\w+)',s,re.M)
  if m:classes[m[1]]=p
license_index=DST/'asset_licenses_provenance.json'
license_paths=list(json.loads(license_index.read_text())['files']) if license_index.exists() else []
pending=license_paths+['scenes/player/player.tscn','scripts/world/grapple_anchor.gd','config/player_tuning.json','config/input_profile.json','scripts/ui/demo_ui_01/game_typography.gd'];done=set(); missing=set()
while pending:
 p=pending.pop()
 if p in done:continue
 if p not in paths:missing.add(p);continue
 data=read(p);done.add(p)
 if p.endswith(('.gd','.tres','.tscn','.json','.gdshader')):
  s=data.decode()
  for q in re.findall(r'res://([\w/ .-]+\.(?:gdshader|gd|tscn|tres|json|png|svg|wav|ogg|otf|ttf))',s):
   if q not in done:pending.append(q)
  if p.endswith('.gd'):
   for token in set(re.findall(r'\b[A-Z]\w*\b',s)):
    if token in classes and classes[token] not in done:pending.append(classes[token])
for p in done:
 q=DST/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(read(p))
record={'repository':'https://github.com/zhipijun1996/gunman-rush','commit':SHA,'files':{p:hashlib.sha256(read(p)).hexdigest() for p in sorted(done)},'missing_static_refs':sorted(missing)}
(DST/'source_provenance.json').write_text(json.dumps(record,indent=2))
print('copied',len(done),'files',sum(len(read(p)) for p in done),'bytes; missing',missing)
