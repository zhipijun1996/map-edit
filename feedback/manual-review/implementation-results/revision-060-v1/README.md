# 审批实现与真实 Godot 证据（revision060）

授权修复HQ01/HQ02/S12，并实现新批HQ03/HQ07/HQ08/HQ09。HQ02中台宽64→112、旧S12原生载台改可穿已按授权实施；其余设计几何与轨道不改。

本轮7项均有可玩包，固定方向31条，完整v2通过3项。原游戏870份保护文件未变；设计网页未修改。所有通过、失败、零帧拒绝、引擎中断和源码快照均保留。

| 规格 | 状态 | 原生方向 | 正式案例数 | 下载与证据 |
| --- | --- | --- | --- | --- |
| s12 | 完整v2通过 | 12 | 962 | [证据](s12.json) · [试玩ZIP](downloads/s12-native.zip) · [短片](videos/native-s12-B-to-T-v1/native.mp4) |
| hq01 | 可玩，完整验证未过 | 6 | 456 | [证据](hq01.json) · [试玩ZIP](downloads/hq01-native.zip) · [短片](videos/native-hq01-L-to-R-v1/native.mp4) |
| hq02 | 完整v2通过 | 2 | 166 | [证据](hq02.json) · [试玩ZIP](downloads/hq02-native.zip) · [短片](videos/native-hq02-B-to-T-v1/native.mp4) |
| hq03 | 可玩，完整验证未过 | 6 | 416 | [证据](hq03.json) · [试玩ZIP](downloads/hq03-native.zip) · [短片](videos/native-hq03-L-to-R-v1/native.mp4) |
| hq07 | 可玩，完整验证未过 | 2 | 136 | [证据](hq07.json) · [试玩ZIP](downloads/hq07-native.zip) · [短片](videos/native-hq07-L-to-R-v2/native.mp4) |
| hq08 | 完整v2通过 | 2 | 170 | [证据](hq08.json) · [试玩ZIP](downloads/hq08-native.zip) · [短片](videos/native-hq08-L-to-T-v1/native.mp4) |
| hq09 | 初态冲突／仅单向样品 | 1 | 0 | [证据](hq09.json) · [试玩ZIP](downloads/hq09-native.zip) · [短片](videos/native-hq09-L-to-T-v2/native.mp4) |

完整通过是当前精确版本及已测路线的技术候选资格，不是人工试玩或生产批准。固定样品成功不代表全部扰动通过；未过项按JSON逐方向说明，不归咎为已证明的几何无解。

## 试玩

下载ZIP后在本仓库根目录解压，按[WORKSPACE](../../../../pcg/WORKSPACE.md)恢复原项目资源。用官方Godot4.7.2打开JSON的nativePlayable.scene：

```bash
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/<scene路径>" -- --case 0
```

省略`--replay`为手动操作，加上则回放真实记录输入；`--case N`切换已包含的方向。ZIP不重复打包官方引擎或原游戏资源。影片为实际编译场景、60FPS、1倍速，结尾全世界冻结1秒。strict=false的影片明确为REVIEW_ONLY，全部严格差异保留；不放宽比较器。

## 证据与限制

[授权与预算](authorization/request.json) · [几何/源码/预算核验](verification/geometry-source-budget.json) · [原始归档核验](verification/raw-archive.json) · [原始完整报告重算](verification/full-report-rederivation.json) · [AI抽帧观察](verification/ai-video-observation.json)

HQ02已有真实敌弹先发射、再被P原生圆形扫掠消解的回执，余寿0.4667秒；没有改敌弹速度或寿命。HQ08只在原生实际落地支撑后启动，不以进入触发图框替代。HQ09用原PlayerProjectile的terrain_impacted与spent证明挡弹，真实玩家有10帧穿过挡板；L来向发出真实机关子弹、收回两侧刺，顶口平台保留。HQ09顶刺方向的第二版仅改_draw，原表现和影片保留。

HQ01正式运行遇到原引擎signal11：完成批次逐字节复用，只续跑相同输入，未换候选/池/种子。完整结果仍False。HQ07反例驱动读取不存在direction的问题已独立补测12例，原校准失败不因此变True。

```bash
python3 pcg/tools/restore_archive.py approved-revision060-implementation-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py approved-revision060-implementation-v1 --extract
python3 -m pcg.manual_review.audit_revision060_061_v1
```

镜像、封口组合、任意进入态与完整Map仍UNKNOWN。没有部署设计网页、合并main或授予生产批准。
