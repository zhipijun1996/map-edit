# 平原 Module：Block128 生产批次

当前[9份标准候选](manifest-progress-9-v1.json)，原库117版、平原优选99版；不是30份完成，也不是9种全新玩法。此前8份局部候选仍保留原资格，没有自动转为Block版本。当前Map合同来源为`research/l4-map-generator@a685fae`，见[源码绑定与交接](../../../docs/l4-mapgen/plains30-block-handoff-v1.md)。

| 内容 | 包围尺寸/拥有格 | 实际玩法与影片 |
| --- | --- | --- |
| C02-1/2 空中气闸 | 1408×896，47/46格 | 空中同枪反冲、关身后门开前门；[下沉出口](videos/BC02-1-v2/block128-serial-airlock-review-only.mp4)，严格录像比较未过，供观感 |
| C01-1/2 换脚桥 | 1792×1024/76格；1408×1024/61格 | 同枪撤旧桥造新桥，真实落桥回枪再出发；[升层版](videos/BC01-2-v2/paired-support-transfer-review-only.mp4)，严格录像比较未过，供观感 |
| C05-1 三口移动站 | 1536×1280，94格 | 同一乘行选择点：[早离台回折到西上岸](videos/BC05-near-v1/block128-moving-station-choice.mp4)或[继续乘行、换门去东上岸](videos/BC05-far-v1/block128-moving-station-choice.mp4)，351/341帧严格比较均通过 |
| D05-1/2 风铃台追接 | 见标准清单，均Block128 | 跳起左下击挂载铃，同枪反冲+启动台、台接住第一次落脚，回枪后二跳到岸；[325帧严格比较通过](videos/BD05-1-v1/block128-bell-carrier-catch.mp4) |
| C07-1 关墙刹车袋 | 见标准清单 | 同枪开前门/关后墙，以真实新墙接触刹住反冲，再落袋回枪；[246帧及原Motor接触逐帧一致](videos/BC07-1-v1/block128-new-wall-collision-brake.mp4) |
| C10-1 保枪纠错侧洞 | 896×1280 | [正常主路189帧严格一致](videos/BC10-main-v1/block128-retained-shot-recovery.mp4)；[失误入洞、真实返新A重试507帧](videos/BC10-retry-v1/block128-retained-shot-recovery-review-only.mp4)，后者1帧support_id不同，仅供观感 |

所有尺寸为128倍数；拥有格四邻接连通，可不规则。不生成外框，内部地形不缩放。SVG与可玩消费者显示Block轮廓、真实边界中心锚点和内部身体站位。Port锚点不是出生点：ground64地面在anchorY+32，人物中心在anchorY+14，本轮水平dock还向内24px。

C05是真正去向选择，不是额外安全口。A是低处西口，B是上方西口，C是高处东口；同一世界初态下分别验证A→B/A→C，其他四个方向UNKNOWN。它是新Block地貌规则，超出旧终岸±32适配域，因此重新校准；原型与旧版通过结论没有挪用。

六组成功生产运行共1038次真实Godot案例，含全部失败与精确反例。C02、C01、D05各两份及C05/C10的两条路线、C07一路均过原regular校准和独立留出。C05的动态世界clean/mild/moderate各12次，留出两路线各36/36；D05两接口留出各clean12/12、mild12/12、moderate11/12；C01/C02静态世界clean各1次，mild/moderate各12次。它们仅为有限程序策略资格，不是人工成功率。

C01/C02两个review-only影片各有3帧`support_id`接触体顺序差异，完整差异见其`review-only-manifest.json`和`strict-failure-audit-v1.json`；位置、输入、资源、机关、奖励字段一致。原严格比较仍失败，没有放宽。C05两片、D05、C07、C10主路共1452帧是严格比较通过的正常60fps原生连续输入回放，末尾约1秒冻结结果画面。

## 运行与检索

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py content-workshop-plains30-block-v1 --extract \
  --prefix results/workshop-batch30-blockc05-full-v1/
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-block-v1/manifest-progress-9-v1.json --list
python3 -m pcg.prototype.creative_batches.plains50_catalog \
  --manifest generation/workshop/plains30-block-v1/manifest-progress-9-v1.json \
  --play C05-1 --route far
```

默认进入手动试玩；加`--replay`为程序见证。复现生产使用`batch30_runtime.produce_v3`和新run名；固定协议在`pcg/creative-production/batch30/protocol-map-block-v1.json`。原CandidateLibrary持久化检索见[4份跨进程复用](retrieval-v1/receipt.json)，生成与物理调用均0；C05新增记录同样来自原磁盘库。

## 请求、失败与待做

C02实际消费最新B的`block-demand/exp1_0`，按其`rewards:[]`移除奖励并重验。C01/C05只响应明确的Task A派生需求，保留自己的宝箱，不能冒充B的无奖励或junction请求。标准清单保留完整请求、回应及逐方向关系。未知输入状态、反向、跨边界、Map奖励预算与整图不自动满足。

C06坠井选层的新Block规则尚未入库：高路完整校准moderate7/12，低于原.65门槛，整份三口拒绝，独立留出未运行。已用完两次几何修订，不靠改名补数量。第一轮曾把低路多付一枪、身体向入口外越2.89px误当机制反例；新分类保留了外部空间依赖UNKNOWN，严格名义身体检查未改，最终仍因真实瞄准容错不足拒绝。

D04r2的原中间岸既供主路离开又供同世界回程使用，朴素Block端口外邻还被高柱占用。当前返回具体`needs_design`，没有删回程或扩掩码假通过。气闸镜像接收器边界试件的第二轮只有11/13，未签接缝。D05错枪重试实际到奖，但身体越出入口外邻，因而新版本恢复资格仍UNKNOWN；不能继承旧恢复结论。其余内容继续按新版本验证。C10初次全量实际已过校准/留出，但反例ID后缀未绑定原canonical而被原库正确拒绝；仅修注册ID后完整重跑，不修改地貌、策略、噪声或门槛。旧155次失败保留，重复相同留出不算额外独立条件。现入口在0物理调用时预检反例ID/原几何/Block所有权绑定。

源码、全部失败、留出和冻结快照归档为`content-workshop-plains30-block-v1`；D05另在`content-workshop-plains30-block-v2`；C07/C10在`content-workshop-plains30-block-v3`。旧未准入原型及失败由`content-workshop-plains30-prototypes-v1`保留。最新网页兼容补丁[PR #6](https://github.com/zhipijun1996/map-edit/pull/6)已部署，[公网字节回执](editor-compatibility-v1.json)记录校验；内容索引仍通过现有“更新本仓库模块”按钮获取。

技术候选、视频观感、实际试玩和生产批准分别记录；人工趣味/试玩/生产准入均UNKNOWN。
