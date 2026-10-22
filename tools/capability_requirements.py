"""Import explicit source declarations; absent or incomplete declarations stay uncertain."""
import copy


def resource_evidence(raw, module_id):
    result=[]
    for location,data in [('module',raw),('entry_port',raw.get('entry_port',{})),('exit_port',raw.get('exit_port',{}))]:
        limits={k:v for k,v in data.items() if (k.startswith(('min_','minimum_','maximum_')) or k=='requires_burst') and isinstance(v,(int,float,bool)) and v>0}
        if limits: result.append({'moduleId':module_id,'location':location,'values':limits})
    return result


def from_source(source, resources):
    raw=source['original'];kind=source['kind'];abilities=[];limits=[]
    if kind=='forest':
        abilities=list(dict.fromkeys(raw.get('requires',[])))
        note='只导入工厂显式 requires；机关、动作路线和验证配置不自动成为硬性锁。未声明不代表无锁。'
    else:
        nodes=[{'module_id':source['moduleId']}] if kind=='resource' else raw['nodes']
        for node in nodes:
            part=raw if kind=='resource' else resources[node['module_id']]['data']
            evidence=resource_evidence(part,node['module_id']);limits.extend(evidence)
            for row in evidence:
                v=row['values']
                if v.get('min_jumps',0)>0: abilities.append('jump')
                if v.get('min_jumps',0)>=2: abilities.append('double_jump')
                if v.get('min_air_shots',0)>0: abilities.append('shot_recoil')
                if v.get('min_air_shots',0)>2: abilities.append('multi_air_shot')
                if v.get('requires_burst'): abilities.append('recoil_burst')
        note='从模块及实际出入口的显式参数导入；原始次数、距离等数值保留在下方。能力标签不替代完整参数筛选或物理验证。'
        if kind=='foundry':note+=' 工坊 capability_profile='+str(raw.get('capability_profile'))+' 是回放验证配置，不当作最低能力锁；当前只合并组成模块的显式要求。'
    requirements={'version':1,'status':'partial' if abilities or limits else 'unspecified','allOf':list(dict.fromkeys(abilities)),'anyOfGroups':[],'note':''}
    return copy.deepcopy(requirements),{'note':note,'tuningConstraints':limits}
