# 平原内容工坊：最新 Block 合同交接

本轮直接核对 `research/l4-map-generator@a685faebdb7596b0808538ab9ef299d6455d2320` 的策略、Python/JS校验器、真实适配与Map请求；检查时main为54d0cfc，随后网页兼容补丁PR #6已发布为75d2b02。逐文件URL、Git blob SHA和原字节SHA见[来源索引](../../pcg/creative-production/batch30/map-constraint-source-v1/source-index.json)。不是只依据README，也没有另建Map生成器。

当前真实配方只支持Block128。拥有格是四邻接连通的不规则轮廓，包围尺寸为128倍数，内部地形不缩放、不默认补边框。端口在拥有格的真实外边中心，外邻格不得同时拥有。ground64水平口的floor=anchorY+32、人物中心=anchorY+14；本轮dock还向内24px，标准文档分别保存anchor与`grid.stagingPosition`。所有权保留原恢复岸、两扇门、交互物与动作空间，不能只覆盖nominal轨迹。

生产入口：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name fresh-block-airlock \
  --rules pcg.prototype.creative_batches.batch30_blockpilot.api_v2 --index 0
```

使用新run名；固定协议、反例及原regular门槛，不从holdout挑策略。旧版没有`block_grid/block_ports`时会在0次物理调用后返回具体缺口。几何、端口、形状、策略改变后重新绑定版本与证据。

首交接为[两份气闸标准文档、原库记录与可玩场景](../../generation/workshop/plains30-block-v1/manifest-progress-2-v1.json)。它们实际消费B的`block-demand/exp1_0`，完整保留原请求，按`rewards:[]`生成无奖励版本。API拒绝Boss、junction、缺反冲、Block256、奖励服务等不支持需求；显式反向需求返回`needs_verification`，不会映射成普通A→B。`candidate_for_joint_mapping`仍需B完成端口边分配、输入/输出状态蕴含与区域支路回程组合。

换脚桥保留真实12币宝箱，只响应Task A派生的两份明确需求，不能冒充B的无奖励请求。其他Module须逐份声明其真实职责与支持域。

两份气闸的完整原regular：校准mild各12/12、moderate11/12与10/12；独立留出mild/moderate均各12/12，静态世界clean各1/1。34个/精确路线反例未否决目的；有限搜索不证明无其他解。标准版本只签A→B内部staging的有限策略，不签通用边界、反向、恢复、变换或全图。

边界试件保留两源实体的精确并集，不增平台或恢复资源。自身直接拼接存在所有权/恢复台冲突，见[静态拒绝](../../pcg/prototype/creative_batches/batch30_blockpilot/adjacency-refusals-v1.json)。镜像接收器只作为新的接收几何，不能继承镜像挑战资格。第一轮13小样仅6通过；控制器新版本修正settle停止点后为11/13，仍未过预注册筛选，因此完整校准/留出未运行。失败保留，不升级为接缝准入。

B当前原生消费者尚未安装本批互斥双门/移动铃Cell，这是明确集成缺口。Task A已提供隔离真实可玩消费者；共享Block校验器按上游原字节复用，Task A exporter另显式覆盖门B、移动铃包络与禁用承载器占位门，避免漏报或虚假远端占地。B整图验收继续由B执行。

人工趣味、实际试玩、生产准入均未授予。Block适配不是新增玩法家族；此前8份局部候选保留其原资格，不能自动算作符合新Block接口。

后续同批进展：[9份当前标准清单](../../generation/workshop/plains30-block-v1/manifest-progress-9-v1.json)包含换脚桥2、气闸2、真正三口移动站1、风铃台追接2、新墙刹车1、侧洞纠错1。移动站两个出口均过动态世界原regular校准及独立留出，Port分别为A西下、B西上、C东上；原生影片两方向351/341帧严格比较通过。仅A→B/A→C被验证；不是完成B探索图的junction请求。C10同世界入洞、返真实新A、再到B的整条策略另外完整验证；不能只靠名义跳射主路声称其用途完成。C06高路moderate7/12未过门槛，整份接口拒绝入库；D04端口冲突返回具体缺口。当前原库117、平原优选99，新版本人工趣味/生产批准UNKNOWN。
