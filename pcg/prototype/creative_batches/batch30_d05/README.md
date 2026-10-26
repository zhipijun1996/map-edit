# D05 风铃台追接（真实核心，完整准入待 root）

用户原话：`pcg/feedback/workshop/idea-sources/human-d05-bell-carrier-catch/v1.json`。

最终注册：`pcg.prototype.creative_batches.batch30_d05.api_v3`；它只选择已测的第三版物理规则 `api_v2.materialize(interface,1)`，不是第四次几何修订。两个接口分别为远岸和左移40/抬高30的接收岸。原 ShotLatch、原 ModuleMovingPlatform 和真实角色完全保留；`mount_v1.gd` 仅把原铃节点保留世界变换地挂到原平台，未写角色位置/资源/轨迹。实际铃相对平台偏移恒为 `[80,-120]`。

名义动作：原静态 A 走上停台，向右跳后朝左下击铃；同枪让人右上、平台启动向右；**首个射后落地必须是 catch-deck**，实际回充后再跳/反冲至 B 宝箱。第三版 speed750 的两接口 clean 首次射后支持均为152帧 catch-deck；独立 mild12/12、moderate12/12。52 个已跑强反例（每精确接口26个）没有相同出口+奖励成功，不代表排除所有解法。

旧 v1/v2 有真正设计错误：固定 Platform2 在147帧先接人并恢复枪，167帧才到移动台；旧 purpose 只看后来乘台而漏查第一落点。110 条旧实验及精确旧录像保留，但不作为用户要求核心成功。第三版把这块岩唇宽度80缩到35，角色真实清过其顶，仍以真实岩底打断简单被动乘台；不删碰撞/改资源。600速度接不住的两条 clean 也保留。

失败恢复在同一世界故意打偏铃、落底层、经四级地貌回原 A 再试，clean2/2成功；但当前控制 mild6/12、moderate10/12，**恢复尚未达到原 regular 门槛**。第一梯过晚向右起跳会真实撞底，另有少量重试错过台。建议 full 校准预算预注册“先垂直跳再右移、每梯实际 support 条件”的控制选择，不能把这些失败隐藏或把恢复标为已通过。

`receipt-v3.json` 绑定全部220/220实际 probe、失败及源码；full/held/入库均0。反向B→A、任意平台相位入口、通用接缝均 UNKNOWN。旧视频只代表有缺陷的旧版；第三版仍须原生重新录制。

root 统一入口（必须先补独立恢复 full 选择/留出）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v1 \
  --name workshop-batch30-d05-full-v3 \
  --rules pcg.prototype.creative_batches.batch30_d05.api_v3 --index 2
```

消费者需采用 `RUNNER_SCRIPT=runner_v1.gd`、`NATIVE_SCENE=main_v1.tscn`；源码依赖在 API `SOURCE_DEPENDENCIES`。标准输出需要把 `carrier_mount` 的铃宿主与实际包络显式绑定，不能按静态铃坐标导出。

人工观感、实际试玩和生产批准均 UNKNOWN。
