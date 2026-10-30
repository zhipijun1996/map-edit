"""The existing full verifier, with bounded raw storage instead of all-run RAM.
Every byte/hash, source, input, seed, gate, boundary and counter check is retained.
"""
import functools,gzip,inspect,json
from . import core,physics
class RawCache:
 @functools.lru_cache(maxsize=1)
 def load(self,packed):
  packed=__import__('pathlib').Path(packed);cases=core.read(packed.with_name(packed.name.replace('.output.json.gz','.input.json')))['cases']
  with gzip.open(packed,'rt')as stream:results=json.load(stream)['results']
  return cases,results
class LazyLookup:
 def __init__(self,cache):self.cache=cache;self.keys={}
 def register(self,key,packed,index):self.keys[key]=(str(packed),index)
 def __getitem__(self,key):
  packed,index=self.keys[key];cases,results=self.cache.load(packed);return cases[index],results[index]
def verify_report(folder,proof):
 source=inspect.getsource(physics._verify_report_uncached)
 before='lookup = {}; by_id = {}; count = 0';assert before in source
 source=source.replace(before,'cache = RawCache(); lookup = LazyLookup(cache); by_id = LazyLookup(cache); count = 0')
 before="lookup[(batch['batch'], index)] = (case, raw)";assert before in source;source=source.replace(before,"lookup.register((batch['batch'], index), compressed, index)")
 before="by_id[case['id']] = (case, raw)";assert before in source;source=source.replace(before,"by_id.register(case['id'], compressed, index)")
 ns={**physics.__dict__,'RawCache':RawCache,'LazyLookup':LazyLookup};exec(compile(source,__file__,'exec'),ns);return ns['verify_report'](folder,proof)
