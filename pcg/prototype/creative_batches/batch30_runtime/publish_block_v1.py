"""Publish upstream-compatible Block candidates from the existing disk store."""
import argparse
import json
from pathlib import Path
from . import publish_v3 as base


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',required=True)
    p.add_argument('--manifest',type=Path,default=base.REPO/'generation/workshop/plains30-block-v1/manifest.json')
    args=p.parse_args();target=args.manifest.resolve()
    if target.exists():raise ValueError('immutable Block delivery exists')
    base.OUT=target.parent
    def scene_for(case):
        if not case.get('block_grid'):raise ValueError('non-Block candidate cannot enter current delivery')
        if case.get('native_block_scene'):
            return base.REPO/case['native_block_scene']
        if any(l.get('carrier_mount')for l in case.get('latches',[])):
            raise ValueError('mounted Block candidate requires its explicit native consumer')
        return Path(__file__).with_name('main_block_v1.tscn')
    base.scene_for=scene_for
    temporary=target.with_name(target.name+'.building');base.publish(args.runs,temporary)
    value=json.loads(temporary.read_text())
    value.update(schema='pcg/block-module-delivery/v1',id='plains30-block-v1',
                 block_contract_upstream='a685faebdb7596b0808538ab9ef299d6455d2320',
                 block_policy=base.binding(base.REPO/'pcg/map_directed/block_grid/plains-policy.json'),
                 publisher_adapters=[base.binding(Path(__file__))],
                 confirmed_new_action_families=0,
                 family_notice='These are newly validated Block/interface adapters of existing gameplay, not new mechanics.',
                 map_assembly='UNKNOWN; source direction, boundary fixture, state entailment and full Map remain separate')
    for item in value['modules']:
        doc=json.loads((base.REPO/item['document']['path']).read_text());c=doc['generationContract']
        grid=c['space'].get('blockGrid');assert grid and grid['size']==128
        assert c['space']['bounds']['w']%128==0 and c['space']['bounds']['h']%128==0
        item['block_contract']=grid;item['reserved_bounds']=c['space']['bounds']
        item['block_dimensions']=[c['space']['bounds'][k]//128 for k in ['w','h']]
        case=json.loads((base.REPO/item['case_file']['path']).read_text())['cases'][0]
        item['map_request']=case.get('source_map_request','UNKNOWN')
        item['map_request_response']=case.get('map_request_response','UNKNOWN')
        item['qualification']='original regular local staging-direction candidate; arbitrary entry, reverse, recovery and Map assembly UNKNOWN'
        item['presentation_dependencies']=[base.binding(Path(__file__).with_name(n))for n in ['main_block_v1.gd','main_block_v1.tscn','block_draw_v1.gd']]
        for manifest in sorted((base.OUT/'videos').glob('*/review-only-manifest.json')):
            for clip in json.loads(manifest.read_text())['clips']:
                if clip.get('contentVersion')!=item['contentVersion']:continue
                movie=manifest.parent/clip['file']
                assert base.file_sha(movie)==clip['sha256']
                item['videos'].append(dict(**base.binding(movie),manifest=base.binding(manifest),
                    case_sha256=clip['case_sha256'],frames_exact=False,frames_compared=clip['frames_compared'],
                    strict_comparison='failed',review_only=True,duration=clip['duration'],
                    limitations='Original strict comparison failed; full differences are retained in the bound manifest.'))
    value['video_count']=sum(len(m['videos'])for m in value['modules'])
    value['strict_video_count']=sum(v['strict_comparison']=='passed'for m in value['modules']for v in m['videos'])
    value['review_only_video_count']=sum(v.get('review_only',False)for m in value['modules']for v in m['videos'])
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.rename(target)
    print(json.dumps(dict(manifest=str(target.relative_to(base.REPO)),new_block_candidates=value['new_modules'],videos=value['video_count'])))


if __name__=='__main__':main()
