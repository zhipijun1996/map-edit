"""Finite Module-fit feedback: stretch contact coordinates, never add terrain."""
import copy,json
from pathlib import Path
from .director import requests
from pcg.map_directed.director import REPO
from pcg.prototype.plains.room_modules import generate,routes

def run(name):
 out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_shape_feedback_run')
 out.mkdir(parents=True);source=REPO/'pcg/results/direct-contact-layout-v2/layout.json';layout=json.loads(source.read_text());layout['column_widths']=[448]*40;history=[]
 for attempt in range(4):
  folder=out/('attempt-'+str(attempt));folder.mkdir();path=folder/'layout.json';path.write_text(json.dumps(layout,indent=2))
  try:
   _,specs,_=requests(path)
   modules=[routes(generate(s))for s in specs]
  except ValueError as error:
   reason=str(error);nodes=reason.split('/')[1].split(',');history.append({'attempt':attempt,'status':'unsatisfied','reason':reason,'affected_nodes':nodes})
   for node in nodes:
    room=layout['rooms'].get(node)
    if room:
     degree=sum(node in [e['from'],e['to']]for e in layout['source_graph']['edges'])
     minimum=768 if degree>=5 else 512
     current=sum(layout['column_widths'][x]for x in range(room['x'],room['x']+room['w']))
     growth=max(64,minimum-current)
     for x in range(room['x'],room['x']+room['w']):layout['column_widths'][x]+=(growth+room['w']-1)//room['w']
   (out/'history.json').write_text(json.dumps(history,indent=2));continue
  history.append({'attempt':attempt,'status':'module_shapes_satisfied','modules':len(modules)})
  (out/'history.json').write_text(json.dumps(history,indent=2));(out/'layout.json').write_text(json.dumps(layout,indent=2));print(history,flush=True);return
 raise ValueError('bounded_shape_revision_exhausted')
if __name__=='__main__':run('direct-contact-shapes-v3')
