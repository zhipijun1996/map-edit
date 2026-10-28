# Graph + Block + Module：增量空间契约 v1

本扩展复用 Map Notes `gunman-rush-level-sketch/v1` 与 `generationContract`，不另建内容格式。仅新生成物声明 `generationContract.space.blockGrid`；旧文档不被自动转换或重新批准。实现入口是 `module-block-grid.js`、`pcg/map_directed/block_grid/contracts.py`，最终仍执行原 `module-contract.js`。

## Block 与形状

- `schema = map-notes/block-grid/v1`；`size` 是至少32的偶数整数，当前真实物理配方只校准128；其他尺寸必须返回 `needs_design`，不能缩放角色或冒用128证据。
- `origin` 为两个 Block 整数倍像素坐标。`cells` 是互异整数二元组，必须四邻接连通。不是必须填满的 M×N 矩形，不生成矩形外墙。
- `cells` 是保守的空间所有权：包含真实碰撞体、机关全部运动包络、交互体以及已声明的动作净空。不同实例的预留 Block 不重叠。它会比仅碰撞体搜索保守，可能拒绝本来能塞入的组合，这是第一版明确的取舍。
- 实体仍由 `objects` 表达，`collisionSolids`、`actionClearance`、`dynamicEnvelopes` 仍属于原契约。Block 掩码不替代这些真实几何。有限轨迹覆盖标为 partial，不能称覆盖所有玩家输入。

示意片段（完整文档还必须满足原契约）：

```json
{
  "space": {
    "blockGrid": {
      "schema": "map-notes/block-grid/v1",
      "size": 128,
      "origin": [0, 0],
      "cells": [[0,0], [1,0], [1,1]],
      "port_bindings": [
        {"port_id":"entry", "cell":[0,0], "edge":"W", "profile":"ground64/v1"}
      ]
    }
  }
}
```

## Port 锚点、进入状态与方向关系

`edge` 只允许 W/E/N/S，法线分别为(-1,0)/(1,0)/(0,-1)/(0,1)。该 cell 属于模块，法线方向邻格不属于模块。几何锚点严格等于：

`origin + (cell + 0.5 + normal × 0.5) × size`

Port 可以在凹形轮廓的真实边界上，不要求处于包围矩形外沿。此规则不保证旁边一定放得下另一个模块，仍需整个预留轮廓及动作/动态检查。

原 `ports[].position` 是锚点；新增 `ports[].grid` 保留 cell/edge/profile，`stagingPosition` 是模块内部的实际检查点。二者不同：水平开口中心、脚下地面和角色身体中心并不重合。实例中的 `ground64/v1` 约定地面在开口中心下32px，24×36角色站立中心在锚点下14px；不得当作坐标误差悄悄补路。

相连端口必须锚点重合、法线相反、profile兼容、身体能穿过开口。第一版要求相同 profile 与 crossing offset；不支持任意形状间的适配连接件。垂直 `vertical-recoil-128/v1` 独立于水平接口，上行与下行使用原角色的真实跳跃反冲/走落，不能旋转水平模块假定成立。镜像也是新版本，须独立验证；不支持重力方向旋转。

每个有序 Port 对继续使用原 `relations`。不存在的连接不默认互通；必须逆行的折返支路需要逆向证据。不要求所有模块可逆，也不能为了矩阵全绿而批准非设计通路。单模块 staging 见证保存为 `stagingDirectionEvidence`，不升级边界接口。新整图的边界穿越、资源及机关状态另存 `boundary-state-verification.json`，按内容版本和实际实例绑定。

当前搜索仅支持已有 `grounded_dock` 运动合同，并在实际 pilot 的模块入口检查落地、射击资源和冷却。通用的空中高速进入、钩索挂接或任意状态区间组合还没有获得准入。`state_entails` 仅为失败关闭的合同区间辅助函数，不能把它的纯测试称为全图状态求解。

## 直接拼接与拒绝行为

Map 不生成平台、桥梁、外墙或隐形恢复点。Module Generator 可以在新版本中有限调整其终端岸体（当前每侧最多扩32px）、移动越界铃铛；必须保留调整日志，并重跑新版本物理，不能继承父版本通过结论。内部挑战没有按Block缩放。

同一个 `shape_search.search(..., require_blocks=True)` 先筛选有效 Block 合同，再使用既有有限回溯、环闭合位移剪枝、实体/动作/动态窄相检测。候选不足、端口容量不足、闭环无法闭合、能力或运动条件不满足时返回不可满足原因；不删除关键边，不补平台，不把单模块结果当整图结果。

Map 需求保留职责、所有边、能力、资源、奖励类别、难度意图及生成预算。完整区域未确定的方向和输入状态标UNKNOWN，由联合求解和物理见证落实，而不是编造固定答案。需求补缺仅能调用已有注册配方；未实现的 Boss、道具或高端口模块必须 `needs_design`，不能由名称匹配伪装生成成功。

## 候选与复用

继续使用 `CandidateLibrary`，通过标准文档往返后整图验证，覆盖所有声明有向边才进入隔离 `map-instances` 与 `payloads`。按硬需求检索已验证 payload；每次新组装都重新验整图。通用关系UNKNOWN、人工评审待定、生产准入关闭；技术验证与趣味认可分开。

`plains-policy.json` 保存本轮40～65节点、2～3主路线、三种支路回程及五类奖励的目标。旧96～128实例实验协议保持历史原件，其数量目标由本轮新策略取代。金币不冒充主要道具；奖励数量和总价值各自受控。未标定的价值预算为null并阻止完整验收，绝不表示免费或无限额。人类7～10分钟/10～20分钟必须真人校准，程序秒数不能替代。
