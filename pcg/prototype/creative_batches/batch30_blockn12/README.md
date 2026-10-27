# N12：一枪投资、两种落岸

这是已有 `one-shot-two-routes / investment-fork` 的新 Block128 三侧口版本，不计新家族。共用同一 A 岸、满资源和全部实体：陡向反冲登近高岸 B 取真实12币，或稍晚平射飞向远低岸 C。选择来自同一空中枪的方向与时机；底岸是原样保留的内部恢复地貌，不贴第四端口。

原卡：`pcg/creative-production/batch30/block-next-ideas-v3.json` 的 B31-N12。新规则并不冒充旧≤32岸微调；薄高台整体保留24px厚度。当前 Map 实码绑定862b736c491502ae9934265bc7415805b4c122b9，世界拥有格不规则、没有默认外框。所有 Port 都是 Block 边中心，身体 dock 单独声明，三个外邻格均不拥有。完整24×36身体及相邻帧保守扫掠都检查冻结拥有格。

| Port | 边界 anchor | 身体 dock | floor | 职责 |
|---|---|---|---|---|
| A | [-128,448] W | [-104,462] | 480 | 共用入口 |
| B | [512,192] E | [488,206] | 224 | 近高奖励后续口 |
| C | [1024,576] E | [1000,590] | 608 | 远低主路后续口 |

只注册 A→B / A→C。B→A、B→C、C→A、C→B、任意外部入射状态、接缝、旧取奖后重汇、底岸返台和第四入口均 UNKNOWN，不由保留地貌或旧16帧越界轨迹继承证明。奖励需求是明确派生的上岸12币需求，不冒称满足 Map 零奖励请求。

真实探针38/80，两个规则预算已用：首6 clean、2普通跳对照；按事前首落全身水平裕度选择高c2(49.875px)、低c1(50.228px)；噪声12/12通过；14精确反例中未找到同目标机制绕过。低路另一个真实1枪1跳策略是合法替代，未按仰角词序拒绝。有限反例不是必要性的穷举证明。

第二需求将整个 C 岸提高128至入口同高，Port C 改[1024,448]，另外冻结一份新拥有格，不改第一份。新4 clean中 B通过；C-c0确实到达、无身体越界，但首次落脚24px身体水平裕度−2.742px，不符合事前选择准则；另两控制落底。该需求 needs_design，不交单高路，不放宽准则或追加第三规则。剩42探针未消耗。

原件：

- `pcg/results/workshop-batch30-blockn12-core-v1/`：8 core。
- `pcg/results/workshop-batch30-blockn12-noise-v1/`：12 noise。
- `pcg/results/workshop-batch30-blockn12-counters-v1/`：14 counters。
- `pcg/results/workshop-batch30-blockn12-second-core-v1/`：4 第二需求及失败。
- `pcg/results/workshop-batch30-blockn12-preflight-v1/`：原标准导出+Block JS，0 physics。

`api_v1` 只交第一份三口，全部28×2精确几何反例可用于原生产循环。源冻结后由 root 串行执行：

```sh
python -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --rules pcg.prototype.creative_batches.batch30_blockn12.api_v1 \
  --name workshop-batch30-blockn12-full-v1 --index 23 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v5.json
```

这份交接尚未完成完整校准/独立留出或入库。可玩原生场景 `main_v1.tscn` 继承原 Workshop，无新物理/Cell/Harness/Map Generator。人工观感、实际试玩及生产批准 UNKNOWN。


## 已完成：api_v2 + full-v3

最终冻结API SHA `c3f9e139b91fbc45b578a2752b476dad4cfc6adc5a23b05efd653558627b4a70`；新三口候选 `b961d4a468fdbd9219be77bfd2172e89c60713241f50cbe8c9cba33ad3b6e792` 已入原库。full-v3共170案例，A→B和A→C的原regular校准/独立留出各档全部通过。首份是真正去向选择，其他四对UNKNOWN；第二需求仍needs_design。

失败全保留：probe38，初full-v1最终query元数据写入相撞被原sourceguard在38案例中止；full-v2共70案例，发现取高奖后再落低岸的两种替代，其ONLY原因是B外邻身体越界。api_v2只将有真实B支撑/回枪/12币一次事务、1枪1跳、不更早稳定C、其余因果/资源均满足的外部空气替代显式记UNKNOWN，不接受为内部解、不加拥有格、不签B→C。原56反例逐raw审计仅两例改scope；之后按同协议/索引/seed完整重跑。谱系316 Harness尝试，另两次原生录制不混作新增候选或独立留出。

新命令（使用新的输出名）：

```sh
python -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --rules pcg.prototype.creative_batches.batch30_blockn12.api_v2 \
  --name fresh-blockn12-repro --index 23 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v5.json
```

两段原生60Hz程序回放为BN12-B-v1/BN12-C-v1，139/234物理帧逐字段严格一致；影片末尾约1秒冻结完成结果。旧上节api_v1命令及未验状态仅为原始交接历史，不能覆盖本次新绑定。
