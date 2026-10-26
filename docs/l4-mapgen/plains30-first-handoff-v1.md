# 平原30增量：首份可集成候选 D05

用户改案的风铃追接台已产生两个新技术候选，见[标准目录](../../generation/workshop/plains30-v1/manifest-core-D05-v1.json)。两版只使用移动、普通单跳和原射击反冲，不需要钩索、墙跳或二跳。

核心动作是站到停着的平台，向右跳起、向左下射击台上风铃；同一枪反冲并启动台向右追接。新几何的首次射后落地真实发生在 `catch-deck`，接触后按原机制恢复弹药，再跳向右岸。旧原型固定小台先接人的问题保留在失败记录，未作为新版本的证明。

| 版本 | 空间需求 | 候选 contentVersion |
| --- | --- | --- |
| D05-1 | 较远右岸 | `sha256:3b5ea33ef146c44fdf201ff3ebff5c4001fd398a0f532c1dbad068a7b17859b6` |
| D05-2 | 左移并抬高接收岸 | `sha256:5ab81cab175d4b27d82c72ce6a0cfdcb51476584bfa9238b5cfcde14b80c6b43` |

两版均只有 A→B 的局部路径声明，A 左向外接、B 右向外接。反向、任意台相位/入口速度、变换、接缝、整图传递保持 UNKNOWN。不在接缝自动补平台或恢复资源。B 可先消费标准文档进行局部集成；实际连续接入另验。

原 regular 校准与独立留出，每版 clean/mild/moderate 各12次，均12/12。每版42条精确几何反例未达到相同出口与奖励；有限搜索不证明不存在其他方法。总242次真实 Harness 案例。故意打偏后返回A重试的连续恢复仍在独立验证，尚未签通用恢复/回程合同。人工观感、实际试玩和生产批准均 UNKNOWN。

首版正常速度[短视频](../../generation/workshop/plains30-v1/videos/D05-1-v1/bell-carrier-catch.mp4)有239帧全部字段、机关、承载和奖励状态的严格原生回放核对。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_mounted_v1 \
  --name workshop-d05-reproduce-new-name \
  --rules pcg.prototype.creative_batches.batch30_d05.api_v3 --index 2
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-v1/manifest-core-D05-v1.json --play D05-1
```

运行前按 WORKSPACE 恢复 Godot 和归档。完整轨迹绑定 `pcg/results/workshop-batch30-d05-full-v1/bell-carrier-catch`。原98份候选不覆盖，当前30目标只完成2份可计数候选；D04另2份虽局部技术通过，因奖励路线被更省的无台路线支配而设计暂扣，不计目标。
