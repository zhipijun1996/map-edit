"""Real LLM proposal provider via the configured Codex CLI, with raw receipts.

No template fallback: a failed model call is a failure. The model only proposes;
code registration, actual physics, novelty review and admission are separate.
"""
import argparse,json,subprocess,time
from pathlib import Path
from .engine import ROOT
from .experiments import write
from ..factory.core.engine import file_sha

FIELDS=['id','title','observation_decision','causal_relationship','geometry_necessity','reward','failure_recovery','direction_difference','cheap_falsifiers','difference_from_inventory','implementation_plan']
SCHEMA=dict(type='object',additionalProperties=False,required=['proposals'],properties=dict(proposals=dict(type='array',minItems=8,maxItems=12,items=dict(type='object',additionalProperties=False,required=FIELDS+['cells','capabilities'],properties={**{k:dict(type='string')for k in FIELDS},'cells':dict(type='array',items=dict(type='string')),'capabilities':dict(type='array',items=dict(type='string'))}))))

def run(name,context_path):
    out=ROOT/'results'/name
    if out.exists():raise ValueError('immutable_llm_call_exists')
    out.mkdir(parents=True);context=Path(context_path).read_text()
    prompt='''你是《失序之钟》内容工坊的创意生产者。实际用户要求：循环制作至少20个不重复玩法的Module，创意必须由大模型产生。
只负责创意，禁止调用工具或编辑文件。根据上下文提出8至12个新的、彼此不同的可实现动作挑战。先消化失败反馈，不要重提被否决的廉价解法。尺寸、Seed、装饰、动作词、单纯增加难度不算新玩法。不要把机关任意堆叠；每个设计必须有明确的玩家观察与决策、因果关系及能推翻它的便宜反例。允许现有墙跳/二段跳/钩索能力，但必须显式声明，不能假设基础角色拥有它们。只能复用当前真实机制，不得宣称未经实现的新Cell已有能力。缺口写implementation_plan，不可把空想当成已实现。
优先能在独立Module中快速验证的局部挑战，不设计Map拓扑，不要求堆积长链。输出严格JSON。字段中保持具体地貌关系，不只形容词。你的输出是待实现提案，不能写技术通过、人工认可或生产批准。
上下文：\n'''+context
    write(out/'schema.json',SCHEMA);(out/'prompt.txt').write_text(prompt)
    scratch=Path('/workspace/scratch/creative-producer-empty');scratch.mkdir(parents=True,exist_ok=True)
    cmd=['codex','exec','--ephemeral','--sandbox','read-only','--skip-git-repo-check','--cd',str(scratch),'--json','--output-schema',str(out/'schema.json'),'--output-last-message',str(out/'response.json'),'-']
    write(out/'command.json',cmd);started=time.perf_counter()
    with(out/'events.jsonl').open('w')as stdout,(out/'stderr.log').open('w')as stderr:
        p=subprocess.run(cmd,input=prompt,text=True,stdout=stdout,stderr=stderr,timeout=300)
    receipt=dict(schema='pcg/llm-creative-call/v1',provider='configured_codex_cli',cli_version=subprocess.check_output(['codex','--version'],text=True).strip(),exit_code=p.returncode,wall_seconds=time.perf_counter()-started,prompt_sha256=file_sha(out/'prompt.txt'),events_sha256=file_sha(out/'events.jsonl'),actual_model_call_attempted=True,template_fallback=False)
    if p.returncode==0 and(out/'response.json').exists():
        value=json.loads((out/'response.json').read_text());assert 8<=len(value['proposals'])<=12
        assert len({r['id']for r in value['proposals']})==len(value['proposals'])
        receipt.update(status='proposal_only',proposals=len(value['proposals']),response_sha256=file_sha(out/'response.json'))
    else:receipt['status']='model_call_failed'
    write(out/'receipt.json',receipt);print(json.dumps(receipt),flush=True)
    if p.returncode:raise RuntimeError('creative_model_call_failed; no templates substituted')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--context',required=True);a=p.parse_args();run(a.name,a.context)
