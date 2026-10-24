# 真实物理实验适配边界

固定来源：`zhipijun1996/gunman-rush@12f6cb006d7119598e3235f4ca4f7323e4c9d092`，Godot `4.7.2.stable.official.ed1daf0bf`。

`source_provenance.json` 对提取的每个原文件保存 SHA-256。PlayerMotor、PlayerController、InputRouter、JumpAbility、ShootAbility、TraversalAbility、资源类、Definition 与配置均为原文件字节，未调整物理参数、动作次数、冷却或资源以迁就关卡。`extract_source.py` 以原玩家场景及类型/静态资源引用提取闭包；少数原代码有意使用的缺失路径（例如负例`missing-place-body.png`、离线`build/foundry/batch.json`）列于来源账本，实验不会执行这些路径。

新增的 `runner.gd`、`main.gd`、`lab_draw.gd`、`main.tscn` 与最小项目配置是实验适配器，不属于原游戏正式生成器。

- 每个case仅初次设置spawn，先4帧静止初始化；路途中不传送，不补资源，不变更运动参数。通过真实InputRouter提交动作，Controller.physics_tick使用固定60Hz，唯一位移仍在PlayerMotor。
- base只具有真实基础动作；`grapple` / `double_jump` / `all` 在起点通过真实TraversalAbility.grant授予所声明能力，不改PlayerTuning。正式主路线是否已授予此能力仍由正式消费者决定。
- 平台是实际StaticBody2D/RectangleShape2D。危险物是独立的声明区域，用24×36完整身体前后位置的保守合并矩形检测逐帧扫掠；接触即失败。没有实例化正式荆棘伤害/回退/存档事务，不能用此证明正式危险策略。扫掠包络可能拒绝部分实际安全的斜线轨迹，不能将失败认作不可通关证明。
- 钩点是原始GrappleAnchor Area2D，hang_enabled使用原挂点/弹起语义；勾到障碍、飞行、收回、拉近、悬挂/跳脱均由原TraversalAbility处理。
- 使用原玩家场景，但入树前将CourierVisual.use_plains_v3=false，选择原SVG回退外观，移除纯PlayerFeedback节点以消除搜索中的声音对象；未更换身体形状、Motor或输入。此为调试图形，不是最终美术。
- worker以physics_tick直接回放动作，未生成持瞄输入，不评估AirFocus操作；手动场景调用原Controller._physics_process(delta)，保留真实瞄准慢时和时间精力行为。
- 回放是存在一条见证输入的实测，不是完备动作规划，不能证明最小能力要求/必须使用某个动作。需要禁用动作消融、替代解搜索及真人操作进一步判断挑战设计质量。
- `goal_grounded`默认true，目标检查角色中心进入出口区域且落地。`trace_all=true`保留完整预算，即使先到目标也继续检测后续危险。

原资产许可原文在assets对应目录，额外来源清单见`asset_licenses_provenance.json`。Courier SVG的原来源声明在`assets/characters/courier/source/provenance.json`；美术原型不冒称新批准的视觉母版。

原生可视化录制实测可用：Xorg dummy显示器`:99`，Mesa llvmpipe OpenGL 4.5；Godot原生`--write-movie`输出AVI后由ffmpeg压为MP4。`toolchain/xorg-dummy.conf`与xorg日志可复查。录制是逐帧真实Godot绘制和输入执行，不是静图拼接。它是离线固定帧率录像，不代表设备实时性能。
