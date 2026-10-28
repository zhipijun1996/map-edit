"""Explicit compatibility views for retired grid ownership and runner bindings.

The old authored causal assertions still execute over real frames. A transient
legacy-grid view covers the new complete rectangle, followed by an exact body
rectangle check; this does not resurrect the retired Map or sparse ownership.
"""
from __future__ import annotations
import copy
import importlib
from pathlib import Path
from . import core
from pcg.map_directed.block_grid.contracts import raster

_ORIGINAL_PATHS=(
 'pcg/prototype/creative_batches/batch30_blockd05/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blocka1/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blockpilot/api_v2.py',
 'pcg/prototype/creative_batches/batch30_blockbridge/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blockn12/api_v2.py',
 'pcg/prototype/creative_batches/batch30_blocka2/api_v3.py',
 'pcg/prototype/creative_batches/batch30_blocka3/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blockn11/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blockc05/api_v1.py',
 'pcg/prototype/creative_batches/batch30_blockc07/api_v1.py',
 'pcg/prototype/creative_batches/resource_routes/ordered-target-v2.py',
 'pcg/prototype/creative_batches/plains50_resources/production_v1.py',
 'pcg/prototype/creative_batches/plains50_new_relations/production_sequence_v1.py',
)
_AUTHORS={path:importlib.import_module(path.removesuffix('.py').replace('/','.'))for path in _ORIGINAL_PATHS}
# Expose imports to existing WorkshopEngine author_sources recursion. Helpers,
# original checkers and actual GDScript dependencies are frozen unchanged.
for _index,_module in enumerate(_AUTHORS.values()):globals()['ORIGINAL_'+str(_index)]=_module
SOURCE_DEPENDENCIES=sorted({Path(module.__file__)for module in _AUTHORS.values()}|
    {Path(p)for module in _AUTHORS.values()for p in getattr(module,'SOURCE_DEPENDENCIES',[])})


def original_view(case):
    binding=case.get('migration_compat',{})
    if binding.get('schema')!='pcg/migration-purpose-compatibility/v1':raise ValueError('missing_migration_compatibility_binding')
    path=binding.get('originalAuthorSource');author=_AUTHORS.get(path)
    if author is None:raise ValueError('unregistered_original_compatibility_author:'+str(path))
    view=copy.deepcopy(case)
    rectangle=binding.get('foundationRectangle')
    if binding.get('legacyOwnership')=='superseded_by_exact_foundation_rectangle':
        if rectangle!=case.get('migration_adaptation',{}).get('rectangle'):raise ValueError('ownership_compatibility_rectangle_drift')
        rect=[rectangle[k]for k in ('x','y','w','h')]
        view['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[0,0],cells=sorted(map(list,raster(rect))),
            interpretation='transient original checker view only; exact new Foundation rectangle checked separately')
    return author,view


def purpose(case,raw):
    author,view=original_view(case);result=author.purpose(view,raw)
    binding=case['migration_compat']
    if binding.get('legacyOwnership')=='superseded_by_exact_foundation_rectangle':
        r=binding['foundationRectangle'];outside=[]
        for frame in raw.get('frames',[]):
            if frame['x']-12<r['x']-.05 or frame['x']+12>r['x']+r['w']+.05 or frame['y']-18<r['y']-.05 or frame['y']+18>r['y']+r['h']+.05:
                outside.append(frame['frame'])
        result.setdefault('causal',{})['foundation_exact_body_ownership']=dict(body=[24,36],rectangle=r,outsideFrames=outside)
        if outside:result['reasons'].append('actual_body_outside_foundation_rectangle')
    result['ok']=not result['reasons'];return result


def fixture_task_outcome(case,raw):
    author,view=original_view(case)
    callback=getattr(author,'fixture_task_outcome',None)
    if callback:return callback(view,raw)
    return dict(ok=purpose(case,raw)['ok'])


def bind(document,input_cases,original_cases):
    """Return versionable data bindings; never mutate existing prepared inputs."""
    from .physics import author_for,runner_for
    from pcg.prototype.factory.core.quality import digest
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    records=[]
    for case,original in zip(cases,original_cases):
        author=author_for(original);path=core.relative(author.__file__)
        grid='block_grid'in original
        sequence=any(l.get('sequence_offset')for l in case.get('latches',[]))
        if not grid and not sequence:continue
        if path not in _AUTHORS:raise ValueError('compatibility_author_requires_explicit_registration:'+path)
        runner=runner_for(original,author)
        if sequence:
            if case.get('family')=='prepared-air-sequence':runner=core.REPO/'pcg/prototype/creative_batches/plains50_new_relations/sequence_runner_v1.gd'
            else:runner=core.REPO/'pcg/prototype/creative_batches/resource_routes/runner-v2.gd'
        relative_runner=core.relative(runner);token=digest(relative_runner)[:12]
        wrapper=Path(__file__).parent/'compat_runners'/('runner_'+token+'.py')
        source=('from pathlib import Path\nfrom pcg.migration.purpose_compat import purpose, fixture_task_outcome, SOURCE_DEPENDENCIES\n'
            +'RUNNER_SCRIPT=Path(__file__).resolve().parents[3]/'+repr(relative_runner)+'\n')
        if wrapper.exists()and wrapper.read_text()!=source:raise ValueError('immutable_compatibility_runner_changed')
        if not wrapper.exists():wrapper.parent.mkdir(parents=True,exist_ok=True);wrapper.write_text(source)
        case['migration_compat']=dict(schema='pcg/migration-purpose-compatibility/v1',originalAuthorSource=path,
            runnerSource=relative_runner,legacyOwnership='superseded_by_exact_foundation_rectangle'if grid else'not_applicable',
            foundationRectangle=copy.deepcopy(doc['generationContract']['space']['bounds']),
            originalBlockGridSha256=digest(original['block_grid'])if grid else None,
            interpretation='Original causal assertions retained; only retired ownership data and actual original runner binding adapted.')
        case['generation_rule']['registration_source']=core.relative(wrapper)
        records.append(dict(caseId=case['id'],**case['migration_compat']))
    if records:doc['generationContract']['generation']['migration']['compatibilityBindings']=records
    return doc,cases,records
