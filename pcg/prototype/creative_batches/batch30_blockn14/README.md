# N14：越过铃，再回身选路

玩家从低西口 A 真正跳上中央 M 台回枪。选择左高 B 或右高 C 后，先跳到所选铃的外侧，回身向下射铃：同一枪打开对应原短时门，并把人物反冲推向出口。两个独立门初闭，所有路线共用同一实体、机关状态、资源规则和入口；没有虚加恢复 Port。

```text
B 西高口 ← 岸──门L      门R──岸 → C 东高口   floor352
                 ↖     ↗
                铃L M 铃R                    M floor608
A 西低口 ────────↗                           floor736
                  内部保留底岸                floor928
```

Port anchor / body dock：A W[0,704]/[24,718]、B W[0,320]/[24,334]、C E[1024,320]/[1000,334]。真实边中心与内部身体站位分开；拥有格是1024×1024的8×8格，外邻(-1,5)、(-1,2)、(8,2)不拥有，无外框。A→B/A→C之外四有序对均 UNKNOWN；D第二输入、泛化回程/恢复、边界穿越、接缝和全图也 UNKNOWN。底岸存在不等于已验恢复。

原卡 B31-N14 来自当前 Codex 子代理，见 `pcg/creative-production/batch30/block-next-ideas-v3.json`。是 G09 观察射位关系的分叉组合，家族新增数暂不增加。无新 Cell：仅原 rocks / move / jump / recoil / ground renewal / 两个独立 timed ShotLatch，原弹丸、身体、防夹及计时不改。需求显式无奖；B/C是两处真实后续口，不能借奖励数量证明选择。

两个规则、54/80真实探针：

- 首规则修正概念门下沿768切断入口的问题，门下沿640使入口在门下通行；8案例中四名义都真落M、正确击铃，但到原高岸竖面太晚，未到出口。失败全部保留。
- 第二规则只将高岸各向内延64，保全部原门/铃/高差/底岸。4名义中c0两路通过、c1两路失败；4错误侧/省枪对照未到同目标。
- 在 noise 前按事前全24px身体首落裕度固定 B0/C0，余量39.836/38.088px。噪声22/24：B mild6/6、moderate4/6；C各6/6。B两次真实射偏未开门，4/6略高原.65小样标准，完整cal/held可能拒绝，绝不调第三规则。
- 14精确反例未推翻关系。两个 `over-top-without-opening-20` 只是搜索意图名称，实际原弹丸仍击中正确铃，先越铃再反身后1枪2跳到岸，是合法瞄准替代；不能把它们称作绕门或用命名当证据。

所有名义完整24×36身体及相邻帧保守扫掠都在冻结拥有格。失败有落底/失误后跑出拥有格的真实记录，不签恢复。首三个Python预检空格语法错误均在Engine前修正，零实际物理调用；原Godot main --check-only通过。不是物理通过数量。

原件路径 `pcg/results/workshop-batch30-blockn14-{core-v1,core-v2,noise-v1,counters-v1,preflight-v1}/`。标准原Python Block/route消费者、20×2精确反例绑定、原标准导出/Block JS预检通过，均不等于完整技术准入。根任务串行运行：

```sh
python -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --rules pcg.prototype.creative_batches.batch30_blockn14.api_v1 \
  --name workshop-batch30-blockn14-full-v1 --index 25 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v6.json
```

可玩场景 `main_v1.tscn` 复用原Workshop与Block绘图，标准合同和原持久库由原生产入口输出。交接时完整cal/held/入库/视频未完成，人工观感、试玩、生产准入均 UNKNOWN。未重写模拟、验证框架、候选库或 Map Generator。


## 原完整验证已完成

`workshop-batch30-blockn14-full-v1/pass-receiver-turn-fork`：154真实案例，新增原库版本`88c75d0f8e7a27b73c0149be04a4eb9e8734da2c0bb4b3c398b2cc3197f9d6c9`。校准两路clean/mild/moderate全通过；独立留出B moderate10/12、C11/12，其余全通过。全部保留未开中正确门而超时的失败，不将有限通过率换成人类难度/100%可靠性。

探针谱系54+完整154=208 Harness尝试。仍只A→B/A→C，共同M、两原独立限时门、真实越铃反身射击；另四方向、通用恢复、第四口、边界接缝、任意进入状态、Map/人工认可UNKNOWN。使用原接口、原regular，没有新Cell或物理。
