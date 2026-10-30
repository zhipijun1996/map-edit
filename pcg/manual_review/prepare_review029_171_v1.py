if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core
from pcg.manual_review import prepare_review029_v1 as shared
from pcg.manual_review.review029_content_v1 import decode
from pcg.manual_review.prepare_review_refresh_v1 import kill
from pcg.prototype.workshop.rules import cmd

def wave_decode(doc):
 t=next(o for o in doc['objects']if o.get('mechanics',{}).get('kind')=='player_enter_spawn_wave');t['mechanics']['speed']=18;t['type']='switch'
 for e in [o for o in doc['objects']if o['type']=='enemy']:
  e['movementIntent']['speed']=18
 return decode(doc)
def plan_for(n,target,source,design):
 right=target['from']=='entry';start=465 if right else 559;end=616 if right else 408
 first='design-ambush-right'if right else'design-ambush-left';second='design-ambush-left'if right else'design-ambush-right'
 p=shared.at(start,420)+shared.at(512,420)+[cmd('wait',3)]
 p+=kill(first,512,420,8)+kill(second,512,420,8)
 return p+shared.end(end,420),source[0]
def main():
 row=next(r for r in core.read(shared.AUTH/'handoff.json')['rows']if r['reviewId']=='171')
 text=inspect.getsource(shared.prepare).replace("'pcg/manual_review/review029_author_v1.py'","'pcg/manual_review/review029_author_v2.py'")
 scope={**shared.__dict__,'decode':wave_decode,'plan_for':plan_for};exec(compile(text,__file__,'exec'),scope);scope['prepare'](row)
if __name__=='__main__':main()
