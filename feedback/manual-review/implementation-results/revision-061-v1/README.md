# 审批实现与真实 Godot 证据（revision061）

实现已批准的第二轮S02/S07/S08/S10/S11/S12/S13，均与旧同号规格分开。S04/S06/S09后来在main获准，按最新请求进入下一轮。

本轮7项均有可玩包，固定方向27条，完整v2通过5项。原游戏870份保护文件未变；设计网页未修改。所有通过、失败、零帧拒绝、引擎中断和源码快照均保留。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
| s02 | 完整v2通过 | 2 | 169 | [证据](s02.json) · [试玩ZIP](downloads/s02-native.zip) · [短片](videos/native-s02-B-to-T-v1/native.mp4) |
| s07 | 完整v2通过 | 2 | 128 | [证据](s07.json) · [试玩ZIP](downloads/s07-native.zip) · [短片](videos/native-s07-L-to-T-v1/native.mp4) |
| s08 | 完整v2通过 | 2 | 125 | [证据](s08.json) · [试玩ZIP](downloads/s08-native.zip) · [短片](videos/native-s08-R-to-T-v1/native.mp4) |
| s10 | 可玩，完整验证未过 | 2 | 133 | [证据](s10.json) · [试玩ZIP](downloads/s10-native.zip) · [短片](videos/native-s10-R-to-B-v1/native.mp4) |
| s11 | 完整v2通过 | 6 | 486 | [证据](s11.json) · [试玩ZIP](downloads/s11-native.zip) · [短片](videos/native-s11-B-to-R-v1/native.mp4) |
| s12 | 可玩，完整验证未过 | 12 | 862 | [证据](s12.json) · [试玩ZIP](downloads/s12-native.zip) · [短片](videos/native-s12-B-to-T-v1/native.mp4) |
| s13 | 完整v2通过 | 1 | 85 | [证据](s13.json) · [试玩ZIP](downloads/s13-native.zip) · [短片](videos/native-s13-L-to-L-v1/native.mp4) |

完整通过是当前精确版本及已测路线的技术候选资格，不是人工试玩或生产批准。固定样品成功不代表全部扰动通过；未过项按JSON逐方向说明，不归咎为已证明的几何无解。

## 试玩

下载ZIP后在本仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原项目资源。用官方Godot4.7.2打开JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`为手动操作，加上则回放真实记录输入；`--case N`切换已包含的方向。ZIP不重复打包官方引擎或原游戏资源。影片为实际编译场景、60FPS、1倍速，结尾全世界冻结1秒。strict=false的影片明确为REVIEW_ONLY，全部严格差异保留；不放宽比较器。

## 证据与限制

[授权与预算](authorization/request.json) · [几何/源码/预算核验](verification/geometry-source-budget.json) · [原始归档核验](verification/raw-archive.json) · [原始完整报告重算](verification/full-report-rederivation.json) · [AI抽帧观察](verification/ai-video-observation.json)

S11新增精确顺时针椭圆运动定义，复用原ModuleMovingPlatform与角色物理，非直线或折线近似；真实承载、周期与9类非法定义拒绝均有证据。S13为同一L口的实际取奖自返回；额外外部L→取奖→外部L实测中，第13帧完整进入、第65帧真实取得4币、第152帧完整退出。通用单次出界观察器不接受先入后出的顺序，保留原False并按自返回合同只读复核，未重跑物理。

```bash
python3 pcg/tools/restore_archive.py approved-revision061-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision061-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision060_061_v1
```

镜像、封口组合、任意进入态与完整Map仍UNKNOWN。没有部署设计网页、合并main或授予生产批准。
