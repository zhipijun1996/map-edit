# C01 换脚桥的 Block128 接口适配

这是既有 C01 同枪撤掉脚下桥A、生成远处落脚桥B、实际落B恢复后再起跳的空间适配，不增加玩法家族。冻结入口 `pcg.prototype.creative_batches.batch30_blockbridge.api_v1`，只允许移动、普通跳跃、射击反冲。

| 需求 | A 边界锚点 / 内侧身体点 | B 边界锚点 / 内侧身体点 | 保留轮廓包围尺寸 |
| --- | --- | --- | --- |
| 横向断拱 | `[0,320]` / `[24,334]` | `[1536,192]` / `[1512,206]` | 1792×1024，76格 |
| 紧凑升层 | `[0,320]` / `[24,334]` | `[1152,64]` / `[1128,78]` | 1408×1024，61格 |

真实边界端口使用最新 Map `a685faebdb7596b0808538ab9ef299d6455d2320` 的 Block128、连通不规则所有权与 `ground64/v1`。锚点位于拥有格子边界中心，外侧相邻格不归该 Module；身体点在面内侧24px、锚点下14px，岸顶在锚点下32px。Harness 继续使用真实身体点；标准文档才把 Port 映射为边界锚点。没有把人物直接搬到核心起点，人物从A实走到原动作起点。

全部内部地貌整体向上平移86px，尺寸与动作关系不缩放。A终岸裁去原左侧100px空岸；横向B岸裁去外侧64px并上移20px，紧凑B岸向外延伸2px并下移2px。原恢复底岸、楼梯、两门、风铃与12币宝箱全部保留。裁岸改变了原恢复策略：旧回枪位置会把完整身体反冲到A禁止拥有的外邻格，不能继承旧恢复通过。v2把回枪位置限定在170/180px，选择首个通过控制后再测试扰动；拥有格子在新运行前冻结，完整24×36角色每帧都检查。

当前两份需求是 Task A 根据最新 Map 合同派生的内容需求 `block-demand/C01/0,1`，**不是** B 的无奖励 `block-demand/exp1_0`。本版本保留12币奖励，API对外来需求、无奖励替换、反向或未知能力不给通过，返回具体 `needs_design`。Map 的联合端口分配、任意进入状态、真正跨边界、B→A、区域回程和整图仍 UNKNOWN。

## 已实际执行

- 总80/80个预注册小样，含v1 clean4与v2 clean4、mild12、moderate12；名义路线全部通过。
- 新精确几何24个有界反例，0个设计反例成立；保留两个合法替代控制，不强制唯一按键序列。有限反例不证明没有其他解法。
- 失败落到原底岸后，在同一世界不重置资源、实走楼梯、重新切回原机关状态、回到新A身体点、重新完成换脚桥：8 clean、8 mild、8 moderate全部通过。完整身体从未越出预冻结所有权。
- 原 Python Block合同和原标准JS预检通过；以上小样不替代原regular完整校准与独立留出。其运行和入库由根任务另做。
- `probe-receipt-v1.json`绑定每次源冻结、压缩原始物理批次索引和结果，保留所有失败谱系与空的中断目录；没有把空目录算物理次数。

## 复现

在仓库根使用新run名称，旧记录不可覆盖：

```sh
python3 -m pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 \
  --name workshop-fresh-blockbridge-clean --stage clean
python3 -m pcg.prototype.creative_batches.batch30_blockbridge.verify_v1 \
  --name workshop-fresh-blockbridge-counters --stage counters
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name workshop-fresh-blockbridge-full \
  --rules pcg.prototype.creative_batches.batch30_blockbridge.api_v1 --index 1
```

`probe_v2 --stage clean` 与 `verify_v1 --stage recovery-clean` 会创建不可变选择文件；已有选择时使用冻结API生产，不覆盖或重选。上述第一次命令用于在另一个干净源码副本重做选择，不在本工作树原地重写。原生场景 `main_v1.tscn` 只是叠加格子、真实锚点和身体框，不改碰撞、人物、资源或机关。

人工观感、实际试玩、生产批准均 UNKNOWN。
