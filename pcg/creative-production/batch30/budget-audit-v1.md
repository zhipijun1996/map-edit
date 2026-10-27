# Batch30 预算与证据成本审计

**主截止 2026-10-27 06:53:53 UTC：15,244 个 Harness 输入尝试，另有44次原生录制命令。** 将录制也纳入保守成本为15,288，距原24,000上限剩8,712。审计期间N11新增44个已闭输入；另一个截止07:01:06的增量观察合计15,332，剩**8,668**。这不是之后持续运行的最终余额，也不增加预算或授权扩大单提案上限。

审查者 `/root/block21_experience_review`；只读实物审计，0新Godot案例，未改库/profile/候选状态。原上限来自`protocol-v1.json`与`protocol-map-block-v5.json`，均为24,000。

| 主截止成本 | 实数 |
| --- | ---: |
| 原输入工件 / 运行目录 | 1559 / 347 |
| 输入cases总数（尝试口径） | 15,244 |
| 有frames的结果 | 15,210 |
| 零帧拒绝结果 | 34 |
| 缺结果 / 输入输出数量不符 | 0 / 0 |
| 原生录像命令 | 44 |
| 非空native trace / 无trace命令 | 42 / 2 |
| 原生trace合计帧数 | 15,817 |
| 保守合计（含全部录制命令） | 15,288 |

34个零帧结果中31个为`rejected_module_definition`、3个为`rejected_dynamic_unknown_id`。它们消耗尝试预算，但没有物理轨迹。有frames也不等于技术通过：失败、错误观察层、校准、留出、反例、完整重跑和连续试件都照计成本。仅静态元数据/合同/`--check-only`预检不冒充真实实验。

统计方法：逐个读取`results`中run名称含`batch30`的原`physics/*.input.json`，数`cases`；同逻辑路径、同SHA的本地与归档原件只计一次。排除所有`source_snapshot*`嵌套副本。不同真实run路径即使输入SHA一样也保留成本：本次35个这类SHA组若被全局去重，会错误少计398案例。

13份`content-workshop-plains30-*`归档均核分片与完整ZIP SHA，再读`PCG-ARCHIVE-INDEX.json`及相关对象；没有整包解压。1506份输入同时存在本地/归档、53份仅本地、0份只在归档；全部1559份原输入均核SHA。1558份进程执行元数据的目标input路径和SHA均与对应原件一致；没有同路径不同SHA冲突、无半写或不可解析输入。所有工件来源、哈希、每批帧数及运行分解见[JSON原账](budget-audit-v1.json)。

| 特别核对的谱系 | 从实际输入得到的成本 |
| --- | --- |
| N10 | probe80＝77有帧＋3拒绝；full107；held0；合187 |
| N03 | 8旧Cell拒绝＋8有效Cell＋16Module＋22cycle2＝54；有帧46 |
| N06 | 旧52＋修订28＋三口full154＋四口probe70＋四口full336＝640 |
| A2 | probe53＋三次full各199＝650；不能因同一关系重跑而抹掉 |
| 互斥双门Cell | Harness117＋native3＝120；这3次已在44次native内，不再加一次 |
| D03旧两次full | 1498＋1498＝2996，均已计入；其他D03探针也在总账 |
| N08（主截止内） | 9个run合153，含module57和loop50；不由候选数量推成本 |

两个孤立output是D04只读媒体提取目录：其解压后raw SHA精确对应已计的`full-fixtures-v2`两批各12结果；`source-run.json`也明确`new_physics_cases=0`，故不再加24。另1批12案例缺`.execution.json`，但原input与12份有帧output都在；案例成本照计，仅进程耗时/执行元数据未知。

原生录像另查了整个项目167份`--write-movie`命令工件，未发现本批录像藏在非batch30/plains30命名路径。计入44次：Block25、local13、原型3、Cell3。BC01-2-v1与BC02-1-v1有命令、无trace，也按尝试各计1。FFmpeg压缩或短节选不算新Godot调用。持久化命令不能证明所有终端历史从未覆盖或丢失，未留工件调用仍UNKNOWN。

截止与活动尾段：主扫描06:53:53冻结，读取结束06:57:49；当时无不完整输入。之后N11五份已闭input共44案例（8clean＋16critical＋20counter）在07:01:06另行核对，全部有结果，且未见新增native命令。之后N08/N11及其他仍可能继续写入；本报告不替未来调用预扣或放行预算。

未涵盖范围：早于Batch30的六基线、creative20、plains50和其他Map工作量，不作为本批新调用；源码中的`workshop-a1-holdout-v1`、`workshop-counters-v1`、`workshop-gate-window-v2`是既有基线依赖。两个`workshop-fresh-*`文档命令没有实际结果目录，未算运行。其他worktree、未持久化/被覆盖的进程历史未审计。因此只能说**已覆盖工件在明确截止内未到24,000**，不能宣称整个动态生产历史的最终预算合规已经证明。

重算命令（脚本完整嵌在JSON内，仅写`/tmp`和指定输出）：

```sh
python3 - <<'PY'
import json
from pathlib import Path
audit = json.loads(Path('pcg/creative-production/batch30/budget-audit-v1.json').read_text())
Path('/tmp/batch30-budget-recompute.py').write_text(audit['recompute']['python_source'])
PY
python3 /tmp/batch30-budget-recompute.py --root /workspace/map-edit-task-a --output /tmp/batch30-budget-new.json
```

精确重现主截止可加`--cutoff-unix 1793084033.2514014`。新一轮应使用当前截止重算；不能把本次8,668当作持续不变的余额。本审不评价人类趣味。
