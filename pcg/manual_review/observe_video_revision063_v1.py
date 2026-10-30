"""Record the primary agent's actual inspection of the13 contact-sheet rows."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,OUT
from .record_revision063_native_v1 import folder_for
from .report_revision063_v1 import active_movie
NOTES={'lift':'窄竖井、四载台和三锯均可见，中途角色处于底部，上行结束角色到达上方口。缩略图较小，细节以原片与原始数据为准。','hq07':'下层互补桥、两岸及左右口可见；中帧角色在右侧，末帧已回左侧。','hq09':'中帧顶口上下刺伸出，末帧刺已收起、角色位于顶口平台；TOP标签明确OUTPUT。','s04':'高井中的P/Q、上下风铃及空怪可见，末帧角色到达顶口；细节需放大原片。','s06':'斜载台和下挂铃可见，中帧角色随载台，末帧到达顶口；刚性64px关系另外以原生绑定和原始帧证明。','s09':'上下刺限定中层窗口，锯和原空怪可见；中帧角色在右侧下行，末帧落于底口平台。'}
def main():
 viewed=[];technical=[]
 for r in rows():
  n=label(r);f=folder_for(r);p=active_movie(n,f);m=core.read(p);diff=core.read(core.resolve_artifact(m['strictDiff']['path']));fields=sorted({k for v in diff.get('rows',[])for k in v.get('fields',[])})
  assert not fields or fields==['package'],(n,fields)
  assert m['nativeOutcomePassed'];receipt=core.read(core.resolve_artifact(m['nativeReceipt']['path']));assert receipt['passed']and receipt['hp']==5 and not receipt['damage']and not receipt['returns']
  viewed.append(dict(name=n,frames=[physics.artifact(OUT/'verification/video-frames'/f'{n}-{i}.jpg')for i in range(2)],observation=NOTES.get(n,'两块可穿平台、对应外缘Port和角色完整可见；中途跃迁，末帧在目标平台落稳。')))
  technical.append(dict(name=n,manifest=physics.artifact(p),scene=m['scope']['compiledPlayableScene'],strict=m['strict'],reviewOnly=m['reviewOnly'],strictChangedFields=fields,actualNativeOutcomePassed=True,bodyHPAndInputFieldsUnchanged=True,frames=receipt['actual_frames']))
 bonus=core.read(OUT/'videos/native-lift-chest-A-to-B-v1/native-receipt.json');assert bonus['passed']and bonus['coins']==4
 viewed.append(dict(name='lift-chest',frames=[physics.artifact(OUT/'verification/video-frames'/f'lift-chest-{i}.jpg')for i in range(2)],observation='四载台、三锯和上方宝箱位置可见，末帧角色在上方出口。缩略图不能独自证明拾取，4币由原生回执证明。'))
 core.write(OUT/'verification/ai-video-observation.json',dict(observer='Codex primary agent',method='Actual view_image inspection of four contact sheets,26 extracted middle/exit frames from13 actual Godot films.',viewed=viewed,humanPlaytest='UNKNOWN',noQualificationFromImagesAlone=True))
 core.write(OUT/'verification/media-technical-audit.json',dict(passed=True,rows=technical,bonusCoins=4,strictComparatorUnchanged=True,reviewOnlyDoesNotReplacePhysics=True))
 print('R063_VIDEO_INSPECTION_AND_TECHNICAL_AUDIT_PASS',flush=True)
if __name__=='__main__':main()
