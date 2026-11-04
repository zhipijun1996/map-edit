"""Record actual AI inspection of generated evidence frames, without human claims."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import importlib
from pcg.migration import core,physics
NOTES={'060':{'s12':'原生双载台、左右岸与轨道可见。','hq01':'P/Q载台、风铃与分组连线可见。','hq02':'中台扩宽后的落脚面与原生载台可见。','hq03':'岩面刺、风铃与原怪可见。','hq07':'桥门A开B关，右侧入口与返回风铃标签完整；v1右标签裁切已用纯相机v2修正。','hq08':'实际角色、锯与载台可见。','hq09':'上下刺方向与挡板可见；该样片不能证明新鲜T入口安全。'},'061':{'s02':'高竖井错位平台与原生锯可见。','s07':'角色位于上层B机关附近，互补门和返回风铃可见。','s08':'中间岩面上下刺、平台与上口可见；中帧角色位于上口上方，边界资格以独立原始探针为准。','s10':'三层落脚面、锯与右口可见。','s11':'角色实际站在椭圆载台上，中心岩面与三口可见。','s12':'P/Q独立轨道与多端风铃可见，角色站于Q。','s13':'原生宝箱打开、HUD4币，角色正在返回L，锯与上下岩面刺可见。'}}
def main():
 for version in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+version+'_v1');viewed=[];scopes=[]
  for r in scope.rows():
   n=scope.label(r);root=scope.OUT/'verification'/('video-frames-v2'if version=='060'and n=='hq07'else'video-frames');frame=root/(n+'-1.jpg');viewed.append(dict(name=n,frame=physics.artifact(frame),observation=NOTES[version][n]));manifest=sorted((scope.OUT/'videos').glob('native-'+n+'-*/manifest.json'))[-1];scopes.append(dict(name=n,baseModuleId=r['moduleId'],exactDesignVersion=r['designVersion'],filmManifest=physics.artifact(manifest),placement='standalone identity transform',connectedPortSubset=[],closureProfile='none',unusedPortSealing='UNKNOWN',representativeFilm='native internal-dock route replay; boundary proof is separate original raw probes',humanPlaytest='UNKNOWN'))
  core.write(scope.OUT/'verification/ai-video-observation.json',dict(observer='Codex primary agent',method='Actual view_image inspection of listed midframes; technical audit independently compared frame bodies/input/HP/support and preserved strict differences.',humanPlaytest='UNKNOWN',viewed=viewed))
  core.write(scope.OUT/'verification/video-scope-addendum.json',dict(schema='pcg/video-scope-addendum/v1',rows=scopes,oldManifestsUnchanged=True))
if __name__=='__main__':main()
