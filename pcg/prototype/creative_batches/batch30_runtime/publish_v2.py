"""Compose the frozen publisher with repaired-scene and review-only metadata."""
import argparse
import collections
import json
from pathlib import Path
from . import publish_v3 as base


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',required=True)
    p.add_argument('--manifest',type=Path,default=base.OUT/'manifest.json')
    a=p.parse_args();target=a.manifest.resolve()
    if target.exists():raise ValueError('immutable delivery manifest exists')
    original_scene=base.scene_for
    def scene_for(case):
        if case['family']=='park-for-return-repaired':return Path(__file__).with_name('d04r2_overview_v1.tscn')
        return original_scene(case)
    base.scene_for=scene_for
    temporary=target.with_name(target.name+'.building')
    base.publish(a.runs,temporary)
    value=json.loads(temporary.read_text())
    value['publisher_adapters']=[base.binding(Path(__file__))]
    held=json.loads((base.REPO/'pcg/creative-production/batch30/design-holds-v1.json').read_text())
    held_versions=set(held['contentVersions'])
    if any(m['contentVersion']in held_versions for m in value['modules']):
        raise ValueError('design-held versions cannot count toward new30 delivery')
    for module in value['modules']:
        world=json.loads((base.REPO/module['document']['path']).read_text())['id'].removeprefix('generated-')
        module['continuous_fixture_videos']=[]
        for manifest in sorted((base.OUT/'videos').glob('*/manifest.json')):
            cases_path=manifest.parent/'review_cases.json'
            if not cases_path.exists():continue
            cases=json.loads(cases_path.read_text())['cases']
            for clip in json.loads(manifest.read_text())['clips']:
                case=next((c for c in cases if c.get('module_sha256')==clip['case_sha256']),None)
                if not case or case.get('layout_uid')!=world:continue
                if any(v['case_sha256']==clip['case_sha256']for v in module['videos']):continue
                movie=manifest.parent/clip['file'];assert base.file_sha(movie)==clip['sha256']
                module['continuous_fixture_videos'].append(dict(**base.binding(movie),manifest=base.binding(manifest),case_sha256=clip['case_sha256'],frames_exact=clip['frames_exact'],duration=clip['duration'],strict_comparison='passed',scope='Exact same-world continuous validation fixture only; no upgrade of generic return/seam/entry contract.'))
        for manifest in sorted((base.OUT/'videos').glob('*/review-only-manifest.json')):
            for clip in json.loads(manifest.read_text())['clips']:
                if clip.get('contentVersion')!=module['contentVersion']:continue
                movie=manifest.parent/clip['file']
                assert base.file_sha(movie)==clip['sha256']
                module['videos'].append(dict(**base.binding(movie),manifest=base.binding(manifest),
                    case_sha256=clip['case_sha256'],frames_exact=False,frames_compared=clip['frames_compared'],
                    strict_comparison='failed',review_only=True,duration=clip['duration'],
                    limitations='Original strict comparison failed; all actual differences remain in manifest, not relaxed.'))
    value['video_count']=sum(len(m['videos'])for m in value['modules'])
    value['strict_video_count']=sum(v['strict_comparison']=='passed'for m in value['modules']for v in m['videos'])
    value['review_only_video_count']=sum(v.get('review_only',False)for m in value['modules']for v in m['videos'])
    # The repaired D04 rule is the same design relationship, not another family.
    value['registered_rule_relationships']=len({m['family'].removesuffix('-repaired')for m in value['modules']})
    value['port_counts']=dict(collections.Counter(str(m['port_count'])for m in value['modules']))
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.rename(target)
    print(json.dumps(dict(manifest=str(target.relative_to(base.REPO)),modules=value['new_modules'],videos=value['video_count'])))


if __name__=='__main__':main()
