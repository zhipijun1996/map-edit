# 给B的两个精确碰撞接缝试件

[输入与源码/原Module版本绑定](manifest.json) · [可执行fixture cases](fixtures.input.json) · [完整实验汇总](../../../../pcg/results/workshop-plains50-exact-seams-v1/summary.json)

两个试件已执行104次真实Godot案例：4个小探针后固定各首个通过控制，校准49/50、独立留出48/50。静态clean各1次，mild/moderate各12次；每试件均按原regular门槛通过，全部失败保留，见[失败索引](failure-index-v1.json)。试件不入Module库，不增加本批50个的计数，不给原Module自动补“seam verified”。

|试件|原候选版本|原碰撞体如何拆分|同一世界内的实际动作|
|---|---|---|---|
|四口investment-fork|`106e4362c838…`|原C支撑`[520,570,440,100]`按原Port C的x730拆为`[520,570,210,100]`与`[730,570,230,100]`|从原A进入→原B取得12币→真实落到C所在支撑→整身体双向跨缝→原D无伤落稳|
|三口thorn-branch|`ab5d60871a32…`|原B支撑`[475,430,220,160]`按原Port B的x580拆为`[475,430,105,160]`与`[580,430,115,160]`|从原A过尖刺通道→原B取得8币→整身体双向跨缝→下降到原下层C无伤落稳|

两段矩形的内部不重叠，外侧边、y与高度与原矩形完全相同，接触边精确重合：原碰撞union不变，新增/移除solid面积都为0。没有补平台、传送、资源授予或腿间场景重建。每条案例从入口到另一出口始终使用同一角色、机关状态、真实落地资源恢复和奖励账本；领取原奖励一次。

为适配原Definition“入口/出口的完整角色身体必须被一块碰撞体支撑”预检，raw fixture移除了multiport描述，将Definition退出marker放到分割线右40单位的位置。**实际goal仍是另一原端口**，marker不是新增端口、通行合同或原Module端口替换。原文档/原cases的字节SHA和contentVersion保存在清单；修改后的几何/策略使用独立fixtureVersion，不复用原Module证据授权。

四口试件校准25/25、留出25/25；三口试件校准24/25、留出23/25，失败发生于moderate扰动的原尖刺进入段，包含实际受伤/恢复，不伪称全部通过。这里的finite witnesses不证明任意进入状态、两任意Module接缝、镜像/缩放或全Map可用；原合同所有UNKNOWN保持UNKNOWN。

从仓库根复现（原Godot环境与上述两候选源记录已恢复，输出名必须全新）：

```sh
python3 -m pcg.prototype.creative_batches.plains50_seams.fixtures_v1 --name fresh-plains50-exact-seams
```

命令复用原WorkshopEngine、instantiate、evaluate和真实Controller/身体碰撞，不建立第二套模拟或Map Generator。预算上限120，本轮实际104。输入、压缩输出、执行命令/日志、全部失败、冻结源码与留出前选择在`pcg/results/workshop-plains50-exact-seams-v1/`，由根任务统一归档。
