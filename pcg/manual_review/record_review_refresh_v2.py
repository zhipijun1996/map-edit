"""Append the repaired 154 movie; preserve the earlier review-only candidate."""
import inspect
from . import record_review_refresh_v1 as shared
source=inspect.getsource(shared.run).replace("version='v2'if n=='140'else'v1'", "version='v2'").replace("videos/'+n+'-v1'", "videos/'+n+'-v2'")
exec(compile(source,__file__,'exec'),globals()|shared.__dict__)
# Explicit scope: this second recording is only the final 154 candidate.
if __name__=='__main__':
 scope=shared.__dict__.copy();exec(compile(source,__file__,'exec'),scope)
 scope['run'](next(r for r in shared.core.read(shared.AUTH)['rows']if r['reviewId']=='154'))
