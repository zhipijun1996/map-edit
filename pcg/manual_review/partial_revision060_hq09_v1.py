import copy,inspect
from pcg.migration import core,physics
from .continue_revision060_v1 import rows,label,OUT,AUTH,FINAL
from .revision060_content_v1 import decode
from .finalize_revision060_v1 import folder_for,deliver
from . import finalize_first40_v1 as shared

def main():
 row=next(r for r in rows()if label(r)=='hq09');source=core.REPO/row['outputDirectory'];scoped=OUT/'fixtures/hq09-outbound-only';assert not scoped.exists();cs=core.read(source/'cases.json')['cases'];left=[c for c in cs if c['route_spec']['from_port']=='L'];assert len(left)==1
 for name in ['module.mapnote.json','migration.json','parameters.json']:core.write(scoped/name,core.read(source/name))
 core.write(scoped/'cases.json',dict(cases=left));r=copy.deepcopy(row);r['outputDirectory']=core.relative(scoped);s=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r060-partial-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/revision060_content_v1.py');ns={**shared.__dict__,'AUTH':AUTH,'ROOT':FINAL,'folder_for':folder_for,'decode':decode};exec(compile(s,__file__,'exec'),ns);ns['freeze'](r)
 f=folder_for(r);core.write(f/'qualification.json',dict(passed=False,scope='L-to-T playable candidate only; no formal qualification',freshT='FAIL: native thorns harm before first input',conflict=physics.artifact(OUT/'verification/hq09-fresh-top-conflict.json'),geometryChanged=False,productionAdmitted=False));deliver(r)
if __name__=='__main__':main()
