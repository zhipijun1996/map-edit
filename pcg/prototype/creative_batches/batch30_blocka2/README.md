# A2：Block128 主动追台与双向接口

这是 repaired workshop-v2 A2 的岸口适配，不继承 withdrawn v1 或旧物理结论。原始候选来源 26544bbf… / 6b9d2d98…；原停驻启动、暂停、真实承载、惯性、弹丸、冷却、接地回枪和原恢复底岸全部保留。无新增 Cell / 模拟 / Map 生成器。

实际读取 Map `6c864ae6423b6409990564371aca34a322b66253` 的 `block-demand/exp0_0`（两个 incident 边均 bidirectional、rewards=[]、expedition_0 foldback）。原请求全文与 Git blob / 文件哈希留在 `source-map-demand-v1.json`。无奖励是具体 Map 需求，未假称原 A2 必须有箱。内部两个相反动作方向由同一完整实体和同一原初始静止载台开始。

A anchor [-128,448]，内部人体检查点 [-104,462]；B anchor [1024,320]，内部 [1000,334]。完整角色24×36，横向 ground64，外邻无所有权。所有岸的物理修改≤32px；内部路径不缩放，不默认补外框，原完整底岸保留。预冻结空气占用和完整运动包络，所有实际相邻帧的保守完整身体扫掠参与检查。出入实际边界穿越、任意平台相位和接缝仍 UNKNOWN。

去程从新 A 岸真实走至原起跳位置，再空中射铃启动、追上原载台、真实站台随行、选择离台时机跳起射 access 暂停，反冲进入 B。首 i0 clean 中两枪 frame74/177，两次实际开停76/182，承载49帧，其中中立随台36帧/62.5px，250帧首次稳定出口。返向从同一冷初态 B 左跳+右下射击，真实落原静止台回枪，沿台向左后普通二跳回 A；不是假反转平台。首 i0 clean 第113帧实际载台接地，枪1/冷却0/跳0/精力100，242帧首次稳定 A。逆向无需伪造开停因果；替代路线按真实可达比较。

固定预算2规则、80 probe。实用53案例：v1 clean8（i1返程3失败保留）；v2 clean4通过；noise24；精确反例16；同世界去返 clean1。v2 i0双向 mild3/3、moderate3/3，小筛通过但非技术准入；i1去程6/6但逆向 mild1/3、moderate1/3，真实射偏错过冷台、落底后左行越所有权，**needs_design，未 full / held / 入库，不再出第3控制规则**。

i0 的16反例含8种未启动静台接力和8种普通回跳，未达到同目标；完整 API 另含逐枪省略、普通直跳、地面提前开停和被动等待，共去程21/返程20个精确绑定策略。有限搜索不证明不存在绕路。`body-and-resource-audit-v1.json` 是原轨迹只读审计，0新案例。

`roundtrip_v1` 是另外的连续状态试件：去程实际到 B 稳定20帧后走落原底岸100帧，再起跳反冲回 A；同世界3枪3跳、0重置、0身体越界。**仅1 clean，通用 foldback / 扰动 / Map expedition 整链仍 UNKNOWN**。不可用两份 fresh-world 反向案例替代此状态证明。

冻结入口：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 --name workshop-batch30-blocka2-full-v1 --rules pcg.prototype.creative_batches.batch30_blocka2.api_v1 --index 12 --interfaces 0
```

已完成0物理Godot语法、原static exporter、Block JS/Python、精确counter身份/几何绑定预检。`api_v1`只支持i0，i1返回具体失败；标准 Module 文档/候选由原生产器生成。full 由根任务运行，不能把本文小样统计当作已入库。人工观感、真实试玩和生产批准 UNKNOWN。

原件：`pcg/results/workshop-batch30-blocka2-{clean-v1,clean-v2,noise-v2,counters-v2,roundtrip-clean-v1,zero-preflight-v1}/`。复现须使用新输出名，不覆盖原件；所有53实际运行和失败已保留真实输入、gzip结果、源快照及SHA。

## 完整生产与版本化接口修复

最终准入入口为`api_v3`，原规则/Cell/动作/初态不变。原Map请求的UNKNOWN关系与未分配空间保持在source_map_request；本地map_specification显式给两有向对、实际尺寸、normals与隐含基础move桥接。原expedition foldback仍完整保留且未由本地两向代签。

full-v1实际199例通过物理但末尾缺route require_bell/via_ports，0入库；仅补此元数据的full-v2又199例通过，但原Map UNKNOWN relations不是原Module存储器需要的有向对象列表，仍0入库。两次失败、真实代价398和各自源快照均保留。新独立元数据协议补完整本地接口，新full-v3同Seed完整重跑199例，原regular/反例通过，入库61930166…。正向cal/held各36/36；反向cal clean/mild12/12、moderate11/12，held36/36。三次同一留出不算额外独立样本，无物理/策略调优。

原native两片各1000帧严格比较通过；实际250/242帧已稳定抵达，trace_all后段为验收停留。另有显式字幕的6秒前缀审阅节选，保留完整视频，移除的只是后续停留，不隐去操作或失败。节选不是新物理证明。
