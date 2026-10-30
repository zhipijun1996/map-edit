import inspect,sys
from pcg.migration import core
from . import record_revision058_native_v2 as previous
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for as formal_folder
def folder_for(r):
 p=OUT/'delivery-selection.json';mapping=core.read(p)['overrides'] if p.exists()else{}
 return core.REPO/mapping[label(r)] if label(r)in mapping else formal_folder(r)
s=inspect.getsource(previous.run).replace("'-v2'if n=='42'else'-v1'","'-v1'").replace('revision058_native_movie_v1','revision060_native_movie_v2')
s=s.replace("{'42':'C-to-exit','s02':'B-to-T','s07':'L-to-T','s09':'B-to-L','s11':'B-to-R','s12':'B-to-T','s15':'L-to-R'}","{'hq09':'L-to-T','hq07':'R-to-L','s04':'B-to-T','s06':'B-to-T','s09':'B-to-L','lift':'A-to-B'}")
ns={**previous.__dict__,'rows':rows,'label':label,'OUT':OUT,'folder_for':folder_for};exec(compile(s,__file__,'exec'),ns)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:ns['run'](r)
