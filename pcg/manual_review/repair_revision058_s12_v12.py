"""Final prospective control correction: selected direct TOP dock guard matches172."""
from pcg.migration import core,godot_package,physics
from .continue_revision058_v1 import rows,label,AUTH

def apply():
 r=next(r for r in rows()if label(r)=='s12');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-s12-v12.json',dict(cases=cs))
 core.write(AUTH/'s12-final-control-stop.json',dict(selection='v12 is the final prospective controller in this round. First all-gates pass may consume one formal. Otherwise freeze an explicitly unqualified native demonstration, preserve all failures, report solid-carrier/jump interference without changing approved motion or collision.',reason='Two solid platforms can block a jump or displace the rider at different initial phases. No geometry/timing change without user review.',formalVersionsUsed=0,newHoldoutUsed=False,source=physics.artifact(__file__)))
 for c in cs:
  for v in c['control_plan']:
   if v.get('route_mode')=='direct'and v.get('trigger',{}).get('migration_goal'):v['trigger']['migration_goal']=[168,11,8,6]
  c['id']+='-v12'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':apply()
