# R2 拓扑驱动的真实岩谷整图 · 实施记录

状态：单张真实整图的工程里程碑已通过；人工趣味与生产准入仍未签署。沿用 research/l4-map-generator / PR #1；main b9318cf 已包含。正式游戏未修改。

## 本轮验收边界

交付一张由既有 R2 拓扑驱动的完整平原：不再绑定八槽；不同尺寸、多入口出口、Module 零间隙直接拼接；分叉汇合、实际反冲挑战、实体奖励与连续回程。仍不等于超过原版规模的最终区域验收、Boss 战、跨区域或多 Seed 品质验证。

## 复用与增量

- `experiments/l4-mapgen/region_network.py`：原 R2 点采样、Delaunay、双连通核心、两段奖励远征，未另写拓扑生成器。
- `direct_join/layout.py`：既有 CP-SAT 接触布局增加可选尺寸/接触约束与求解设置，默认行为保持兼容。
- `woven_region/design.py`：可执行 RegionPolicy 子集，职责影响尺寸域；不支持的政策拒绝。当前仍不支持把任意自然语言编译成规则。
- `plains/woven_landforms.py`：在既有 room_modules 与已测反冲/风铃关系上作需求适配；新增岩岸、高差、反冲竖向转移及物理封闭的奖励腔。源 Module 输出全部地形，Map 不添连接短平台。
- 复用 canonical export/reload、assemble/audit、CompleteEngine 与原奖励/商店/ShotLatch 服务。
- `woven_region/pilot.gd` 仅扩展输入策略：已声明的上层单向落点截获反冲时，使用原下穿输入到达精确目标。未修改角色或资源。

## 保留的失败与设计反馈

三次固定 Seed 的布局阶段及所有内容/策略批次均在 `pcg/results/woven-*`，不覆盖。独立留出尚未执行时，才允许校准修订。

1. 384wu 接触区无法容纳上下端口净空：同拓扑调整空间预算。
2. 奖励房被穿行楼板占满：向既有布局求解器反馈 side_ports_at_base，重算同一拓扑。
3. 160wu 地板预留大于 144wu 最小接触重叠：产生负高度廊道，拒绝后修正。
4. 实心岩体改变下穿和跳跃净空：低廊道保留显式单向平台，高廊道通过实际竖向开口下降。
5. 短尾差和重复落点导致原 Motor 下穿例外无法解除：不改保护游戏源，改为均匀攀升间距。
6. 跨区落点必须提前横向控制；返回起点要选与目的地同侧的下落踏点，避免下落过快错失接收岸。

协议分阶段写入 protocol*.json；前阶段失败保留。新阶段基于具体反例，未使用独立留出筛选。没有把失败预算静默延长或换 Seed。

## 持续边界

- 内容词汇仍有限，重复反冲竖井/岩岸需要后续 A 任务扩充；没有自动证明趣味。
- 目前空间预分配仍为矩形接触区域，内部地貌不规则；不是任意不规则形状嵌套求解。
- 一张真实拓扑；不宣称多 Seed 体验多样性已完成。
- 泛用端口状态转移 UNKNOWN；有限整图输入策略不证明任意运动状态/任意逃课都可返回。
- 独立候选、人工认可与生产准入严格分离。

## 冻结交付结果

源代码提交 `0008ea6c564088838a8aa55bdb9a162dd7da0cd3`，固定 Seed `plains-weave-0`。

- [实际整图、A/B/C/D 正常速度视频与结构化结果](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-WOVEN-REGION-01/0008ea6c564088838a8aa55bdb9a162dd7da0cd3/ed958626ff83/report.html)
- [真实 Godot 网页试玩](https://zhipijun1996.github.io/gunman-rush-previews/launchers/MAPGEN-WOVEN-REGION-01/0008ea6c564088838a8aa55bdb9a162dd7da0cd3/ed958626ff83/index.html)

`woven-release-v1` 25/25 连续整图策略通过，含预先登记的12条独立输入扰动（±1 tick、±1°），一次留出尝试；没有根据留出结果返工。8条巡回实际覆盖全部50个声明方向，静态审计19 Macro / 27直接接缝 / Map新增地形0。三种尺寸为1024×432、1536×576、1536×720。

两处物理封闭宝箱（8/12金币）和原ShopService商店。取宝后实际购买，余额8→0，未补金币。限时门的真实关门、内部真实射铃重新开启与连续返回另有完整见证。两个闭门自由空间检查均阻断；4条省略可选射击的普通/长按跳跃策略均在相应奖励挑战失败，保留原始失败，不宣称穷举所有替代操作。

19个新硬形状需求进入版本化隔离候选库；`woven-warm-reuse-v1` 全复用19个相同内容版本、生成调用0，重新拼装后13/13整图测试通过，不能由此算第二张随机地图。

`woven-return-value-v1` 4/4配对路线通过。每对取宝前的位置、输入和资源轨迹哈希相同：奖励远征1回程11.37s→6.47s，节省4.90s；远征2为19.60s→8.25s，节省11.35s。这是实际路线测量，不是环路数量评分。

4段原生完整录像共13,822帧逐字段精确一致，正常60Hz/1倍；另有两段35秒片段，clip-manifests记录来源哈希与起始时间，完整录像保留。WebGL手动移动/跳跃/射击/重试/整图smoke独立签署，不将浏览器自动输入视为真人试玩。

已有 npm check、31个L4、33个Map、26个Factory、19个Plains检查通过；CI仅增量检查本次合同及19份标准文档。

候选完整离线验证124.07s，热库再拼装复验79.65s，所选CP-SAT布局阶段55.01s。最大累计子进程RSS观测493,348KiB。上述含进程/冻结/读写，布局也使用了已冻结artifact，不代表Runtime生成性能；跨机器按同Seed重求最优布局的字节确定性尚未签署。

当前地貌仍有长水平层和重复竖向反冲，内容也集中在少量关系原型；没有敌人/齿轮生态。区域空间语法、地标真实视线、所有非预期跳落/逃课以及低资源状态仍需继续验证。第一张整图跑通不等于最终设计质量验收。

## 复现与后续路径

在既有WORKSPACE的官方Godot与已绑定资源恢复后，执行：

```sh
python3 pcg/tools/restore_archive.py woven-region-v1 --extract
python3 -m pcg.map_directed.woven_region.run --name fresh-woven --layout pcg/map_directed/woven_region/release-layout.json --mode all --held
python3 -m pcg.map_directed.woven_region.checks --run pcg/results/fresh-woven --out pcg/results/fresh-woven-checks
```

旧run目录不可覆盖；复跑新批次不重新签署原留出选择。canonical文档按源commit/producer SHA绑定，新的导出版本需要自己的整图证据。当前完整物理批次、校准失败、库记录、原生轨迹与媒体保存在 woven-region-v1 去重归档中。

下一里程碑：同一固定内容库下三张结构不同的真实地图；逐步落实区域结构语法、占用mask与动作净空共同求解、实际可走图反查和低资源回程。内容侧优先扩充能回应新形状/端口需求的动作关系，继续区分技术认证与人工趣味认可。

归档：21,875条原路径、2,253份唯一内容，200,096,614 bytes / 20分片；SHA-256 `bfe64726c3437ba2492df0357df2418770fd23c26117a2197b06297f16d2784b`。逐条恢复校验通过。媒体在归档的 `results/woven-media-v1/media`，与 `generation/maps/woven-region-v1` 原件逐字节一致。公网14资源与3页面字节核验、四播放器实际播放和手动输入smoke均通过；Pages运行40211140985成功，旧站点文件及900MiB限制未改。
