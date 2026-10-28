# 保留组合挑战核心的 Macro 迁移实证

正式样品为 `modules/workshop-macro-gate-brake-return-0/` 与 `modules/workshop-macro-gate-brake-return-1/`。两者属于同一玩法家族的两个既有空间版本，不计新玩法家族。

## 修正方法

原先把出口岸高量化到新网格，改变了门、下落刹车及返回阶梯共享的时序。修订保留全部9块原平台的矩形和材料、机关、奖励、出生/目标与核心输入，另增加三个独立外缘落脚台：

| Port | 外边锚点 | 真实站位 | 方向与表面 |
|---|---|---|---|
| A | `[-256,406]` | `[-232,420]` | LEFT / ROCK / INOUT |
| C | `[1024,406]` | `[1000,420]` | RIGHT / ROCK / INOUT |
| B | `[1024,662]` | `[1000,676]` | RIGHT / ROCK / INOUT |

完整占用矩形为 `[-256,-42,1280,1024]`，即10×8 Block；实例场景原点偏移 `[256,42]`。没有外边框，也没有把左右岸铺成长安全底板。右侧落脚台位于 `x=928…1024`，原刹车动作最远只到 `x=835/875`，核心路径与新增台子分离。外缘空隙使用真实跳跃与反冲通过，实际落稳后才跨边，旧B的未认证LEFT提议据自然可行出流改为RIGHT。

保留的四条有向路线：A→C取得门后奖励，A→B完成两个挑战，C→B执行下落刹车，B→A从下层阶梯返回。其余有向对和自环保持UNKNOWN。两个真实子定义分别重新绑定；它们是Macro内部定义，没有冒充另两个独立认证Module。

## 实测与证据

- 两个版本各249个真实Godot输入案例通过原regular门槛，包含校准、独立留出、18条双向局部身体接缝、8条连续进出及反例检查。
- 返回路线的moderate为11/12；版本1取箱路线的留出moderate为11/12。失败原件保留，没有降低门槛。
- 正式包实际重放8条冻结策略共1366帧，HP5、稳定出口，两个版本的奖励均为22/12/22/10。
- 另各一条同世界核心完整往返实际通过：492/499帧，一个actor epoch、同一钱包、无返回重置，最终22币。这是两条clean补充见证，C/B表示内部原落点；不冒充新外边自环资格或新的独立留出。
- `macro-core-migration-report-v1.json`记录610个输入案例的修订历史；同世界往返另2例。失败、运行源和原始trace均保留。

原检查器按“第一枪”选事件时，会误伤先空打一枪、后来仍执行完整空中射铃的输入。新候选专用观测绑定使用真实弹丸、当时空中姿态、对应门窗口及完整身体通过归因；原刹车、奖励、返回和安全断言全部保留。旧作者、旧观测器和冻结原件不覆盖，没有通用“多一个按键就算付费”的例外。

完整来源及报告位于 `pcg/migration/foundation-v1/macro-core-migration-report-v1.json`、`macro-same-world-loop-witness-v1.json`。正式目录内含标准doc、两个组件定义、物理输入、可玩 `module.tscn / demo.tscn`、原生执行回执和原件归档映射。通用Map、任意进入状态、封口组合、镜像和人工趣味认可仍未认证。

## 持久化复用与复现

以下请求已经从正式库新进程检索到两个版本的四条路线，没有调用生成器或新增物理：

```bash
python3 -m pcg.migration.query pcg/migration/foundation-v1/macro-integration-request-v1.json --allow-scoped
python3 -m pcg.migration validate modules/workshop-macro-gate-brake-return-0 --certified
python3 -m pcg.migration validate modules/workshop-macro-gate-brake-return-1 --certified
```

回收站的原始来源仍可重新准备，不依赖内存候选缓存：

```bash
python3 -m pcg.migration.macro_repair --source-prefix 167dcb6ec336 --out .cache/migration/macro-reproduction-0
python3 -m pcg.migration.macro_repair --source-prefix 04a93aeaf9d4 --out .cache/migration/macro-reproduction-1
```

已实测两份准备稿的doc与cases字节SHA，均与原执行`input-binding.json`完全一致。每个full实验目录保留`frozen-inputs/`和`input-restoration.json`，可在清理临时缓存后恢复。原始报告的只读重验和原生重放不等于新留出；后续正式qualifier须先检查已有条件锁。
