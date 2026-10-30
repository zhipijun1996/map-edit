import inspect,sys
from . import record_revision058_native_v2 as previous
from .continue_revision062_v1 import rows,label,OUT
from .finalize_revision062_v1 import folder_for
s=inspect.getsource(previous.run).replace("'-v2'if n=='42'else'-v1'","'-v1'").replace('revision058_native_movie_v1','revision060_native_movie_v2')
s=s.replace("{'42':'C-to-exit','s02':'B-to-T','s07':'L-to-T','s09':'B-to-L','s11':'B-to-R','s12':'B-to-T','s15':'L-to-R'}","{'hq01':'T-to-L','hq03':'R-to-L','hq07':'L-to-R','rs10':'B-to-R','rs12':'B-to-T','s04':'B-to-T','s06':'B-to-T','s09':'L-to-B'}")
ns={**previous.__dict__,'rows':rows,'label':label,'OUT':OUT,'folder_for':folder_for};exec(compile(s,__file__,'exec'),ns)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:ns['run'](r)
