"""Relocate the already-tested native adapter dependency graph into one runtime."""
import hashlib,json,re
from pathlib import Path
from .library import ROOT,write,sha
RUNTIME=ROOT/'runtime/module_runtime'
QUOTED=re.compile(r'([\"\'])([^\"\'\n]+\.(?:gd|tres|tscn|gdshader|json))\1')
class Vendor:
 def __init__(self):self.nodes={};self.sources={};self.visiting=set();self.host=set()
 def add(self,path):
  path=Path(path).resolve()
  if path in self.nodes:return self.nodes[path]
  if path in self.visiting:raise ValueError('cyclic_runtime_dependency:'+str(path))
  self.visiting.add(path);raw=path.read_text();children={}
  for _,ref in QUOTED.findall(raw):
   if ref.startswith('res://'):
    self.host.add(ref[6:]);continue
   p=(path.parent/ref).resolve()
   if p.is_file():children[ref]=self.add(p)
   elif ref.startswith(('../','./')):raise ValueError('missing_runtime_dependency:'+str(path)+':'+ref)
  graph=hashlib.sha256((raw+json.dumps(children,sort_keys=True)).encode()).hexdigest();name=path.stem+'-'+graph[:12]+path.suffix
  rewritten=raw
  for ref,target in sorted(children.items(),key=lambda p:-len(p[0])):
   for quote in ['"',"'"]:rewritten=rewritten.replace(quote+ref+quote,quote+target+quote)
  RUNTIME.mkdir(parents=True,exist_ok=True);target=RUNTIME/name
  if target.exists()and target.read_text()!=rewritten:raise ValueError('runtime_name_collision:'+name)
  target.write_text(rewritten);self.nodes[path]=name;self.visiting.remove(path);self.sources.setdefault(name,dict(sourceSha256=sha(path),sourcePath=path.relative_to(ROOT).as_posix(),sha256=sha(target),children=sorted(children.values())));return name
 def save(self):write(RUNTIME/'index.json',dict(schema='map-edit/shared-runtime/v1',files=self.sources,hostResourceReferences=sorted(self.host),note='One automatically resolved adapter graph. No case, replay, generator or player scene is included.'))
