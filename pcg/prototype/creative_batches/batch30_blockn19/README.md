# N19 折角双门气闸

状态：一空间、两份 canonical 已筛选，等待原完整校准／独立留出，尚未入库。是原 C02 XOR 气闸的折角适配，0 新基本家族声明；人工趣味、试玩、生产认可分别 `UNKNOWN`。

玩家从西高岸走上横闸 A，击铃会撤掉脚下支撑、同时封住东侧闸 B。落入下层 M 后，真实地面恢复资源；走到原 access 允许的右侧射位再次击铃，横闸封回、侧闸打开，再跳到可见的 10 币箱。两次射击既产生真实地面反冲，又交换原双门碰撞。没有隐藏命中次数、直接位移、补枪或重建世界。

标准入口：`pcg.prototype.creative_batches.batch30_blockn19.api_v1`，仅 interface0。1024×1024／64 个 Block128 拥有格；A 为西面 `[0,320]`、内部 dock `[24,334]`，B 为东面 `[1024,704]`、dock `[1000,718]`。只声明 A→B；两条不同 routeId 分别为正常路线和真实漏接 M／落原阶／空中反冲回 M 的恢复路线，属于同一个 Module。B→A 的已取奖同世界尝试失败，保留 `UNKNOWN`，不签 foldback。

78/80 次输入：77 份真实步进、1 份原定义零帧拒绝，使用两版规则；full／heldout 均为 0。正常路线 mild12/12、moderate12/12；恢复路线 mild6/6、moderate6/6；最终 API 两 clean 均过原物理／Block／标准导出预检。24 个有限反例含普通跳、桥边下落、安全岸／空中预开、逐枪省略、侧门底绕与实际射位／时机变化，未找到设计否决；5 个正常因果替代被保留。有限搜索不证明不存在其他绕法。

原规则首批留下实质失败：概念下 access 嵌岩、岩体封住 M 头部侧向通道，均在首实验前解冲突；首次真实实验又显示原 return-side access 要求射手 x≥588，M 上原射点 x521 的弹丸虽碰铃但不触发。最后规则在真实 M 上移至 x600 射击，并以原岩薄挡沿遮住安全岸提前射线。原 24×36 身体、防夹、弹丸、资源和恢复底岸／步阶全部保留。

来源与协议见 `idea-source-v1.json`、`protocol-v1.json`、`protocol-v2.json`。`probe-receipt-v1.json` 记录完整支出与失败；`frozen-source-v1.json` 固定交接源码。`recovery-observer-audit-v1.json` 对原 12 个恢复 raw 追加只读严格观察：原阶实际接地、空中枪实际耗尽、随后 M 真回枪；不把观察重算成新物理或独立留出。

根任务正式验证命令（本作者未执行）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_N19_FULL --rules pcg.prototype.creative_batches.batch30_blockn19.api_v1 \
  --index 29 --interfaces 0 --protocol pcg/creative-production/batch30/protocol-map-block-v8.json
```

小样入口为 `core_v1`、`core_v2`、`screen_v1 --stage noise|counters|recovery`、`api_probe_v1`。各自要求新的 `--name`，旧结果不可覆盖。标准文件使用原 `export_block_v1.mjs`，不含新 Cell 语义。真实 Map 的奖励预算、双门消费者安装、任意进入状态、接缝和整图均须单独绑定，不冒充满足某个实际 Map 节点请求。
