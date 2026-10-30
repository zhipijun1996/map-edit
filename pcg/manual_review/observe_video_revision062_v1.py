if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from .continue_revision062_v1 import rows,label,OUT
NOTES={'hq01':'T→L回放中角色实际站于Q，P/Q与分组风铃可见；左右端口标签完整。','hq03':'R→L回放中原生怪与玩家位于下层安全落脚面，上下岩面刺和顶口可见。','hq07':'互补桥A开B关、右侧原怪和回程铃可见；相机余量使右口标签完整。','rs10':'B→R回放中角色位于中层平台上方，反冲子弹、锯与各层落脚面可见。','rs12':'B→T回放中角色站于Q，P/Q独立轨道与风铃、顶口可见。','s04':'高竖井中P/Q分离，角色位于下台附近，上段原空怪、独立风铃及上下口可见。','s06':'斜向载台承载角色，载台下方真实风铃可见；严格原生回放相同，64px刚性偏移另由原始逐帧坐标审计。','s09':'角色已过锯窗进入右侧区域，中线锯、上下原生尖刺与下段原空怪可见。'}
def main():
 viewed=[];scopes=[]
 for r in rows():
  n=label(r);frame=OUT/'verification/video-frames'/(n+'-1.jpg');viewed.append(dict(name=n,frame=physics.artifact(frame),observation=NOTES[n]));manifest=next((OUT/'videos').glob('native-'+n+'-*/manifest.json'));scopes.append(dict(name=n,baseModuleId=r['moduleId'],exactDesignVersion=r['designVersion'],manifest=physics.artifact(manifest),placement='standalone identity transform',connectedPortSubset=[],closureProfile='none',unusedPortSealing='UNKNOWN',scope='representative internal-dock route; separately evaluated boundary raw is required for qualification',humanPlaytest='UNKNOWN'))
 core.write(OUT/'verification/ai-video-observation.json',dict(observer='Codex primary agent',method='Actual view_image inspection of all8 listed midframes. Technical audit independently compared body/input/HP/support and retained every strict field difference.',viewed=viewed,humanPlaytest='UNKNOWN',noQualificationFromImagesAlone=True))
 core.write(OUT/'verification/video-scope-addendum.json',dict(schema='pcg/video-scope-addendum/v1',rows=scopes,oldManifestsUnchanged=True))
if __name__=='__main__':main()
