# D04：去程留下的平台，改变回来时的动作

最终几何在 `rules_v5.py`，控制修复域在 `rules_v7.py`，正式注册入口 `api_v3.py`。原ShotLatch启动/暂停、原ModuleMovingPlatform承载、原角色动作/弹丸/落地恢复；无新Cell或共享Harness变更。

同一layout的全部路线使用相同初始Cells与平台相位。先在A启动下层平台，再在上层跳跃中向左下击铃；同枪反冲跨上B并暂停平台。中位约x550/598服务直接回程，奖励侧约x820/881接住B下落并通向右侧宝箱C。两种布置来自不同射击时机，不是两次不同初态拼凑的选择。

标准Module只有A→B与A→C两个已请求方向，3个真实口A/B/C；其他方向UNKNOWN。原A返回是独立不计入Module数量的持续fixture：A→B→A，或A→B→C取得12币→同一平台→下层两段反冲→A。原Definition拒绝相同entry/exit坐标，所以fixture保留B作为Definition marker、实际goal为原A；它不创造第二个A端口，也不交给标准合同冒充A→B。

`case.required_carrier_park`以及`spec.objective.route_world_outcomes[route_id].required_carrier_park`声明目标停位与running=false。外在结果比较读取真实workshop.carriers及最后moving_platforms.position。3枪岸上预停再跨越是有额外动作成本的合法替代；不能因未复现指定按键自动否定。全去回反例还必须用`fixture_task_outcome`，它有意不检查最后park，从而能发现不停台却同样取宝/返回的漏洞。

## 真实进度与限制

- v1–v3保留12+12+8个早期探针，以及2个远岸稳定射线反证；空中布置先通过，回程goal/恢复几何曾失败。
- v4中位完整回程4/4；奖励回程仍失败，未改名通过。
- v5两个接口共16探针：i0 control0、i1 control1均完整完成中位与奖励侧回程。奖励侧实际7枪；中位3枪。
- 最初注册8/8 clean，但96小扰动仅78通过，不作准入。v5已有control3替代i1跨越后12/12 mild通过。
- v6四控制域小扰动21/48通过；最佳545/.5为11/12，侧缘迟到仍保留。
- v7在相同几何上预声明四种更近起跳/更高射角，两接口8 clean中7成功，默认i0 r0、i1 r1均通过。该cycle至此60新probe预算已用完；完整cal/held由根任务在原regular门槛下执行，不能把这些小探针标成入库通过。

主cycle188探针，修复cycle60，共248次；`probe-receipt-v1.json`汇总23个历史run及其`batches.json`、source binding与原始证据哈希。原额外授权在根`pcg/creative-production/batch30/protocol-v2.json`和`protocol-v3.json`，不覆盖旧协议与失败。

`api_v3.layouts(recipe,interface)`导出两条前向路线；`api_v3.fixtures(interface,return_control=0..3)`导出持续回程。接口0较短，接口1右岸/奖励洞向东偏移、平台路程更长，采用既有control3跨越；不计新家族。完整物理、留出、标准导出、入库与录像尚由根统一执行。


## 主动完整任务反例（程序已交根，尚未运行）

`adaptive_counters_v1.cases(interface)`每接口16条、共32条程序。每接口8条先在中位真实落台、走到平台东缘x620/665，再用低角反冲尝试钻B桥底去C；另外8条从B东落后主动选更晚的发射位置。每种前进法配两种适配中位世界的返程，包含安全底层攀回，避免把“安全恢复”隐藏成免费的通用奖励回路。没有改变世界初态、平台相位或资源，也没有在缺失的奖励侧平台上空等。

必须使用`api_v3.fixture_task_outcome`比较实际12币、原A落稳、HP/能力和连续性，忽略最后停位。若该路线比奖励侧布置更便宜，应据实际shots/jumps/ticks返工或缩小设计承诺，不能由`required_carrier_park`拒绝它。脚本只做了Python导入与结构检查，物理结果保持UNKNOWN，由根在full1600预算内执行。
