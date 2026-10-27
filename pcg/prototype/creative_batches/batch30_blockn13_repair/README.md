# N13 外层控制修订

原 `batch30_blockn13` 的 51 probe／两规则失败保留；本独立范围由 `protocol-map-block-v8.json` index28 明确登记。新增 29 probe 已耗尽，谱系累计 80。原物理、地貌、门和资源机制均未改变。

改动为前移到台面前侧近距离停车，离台枪从左下 60° 改为左下 45°，减少弹丸再次击中挂载风铃的机会。两份 clean 均过；按预注册 first-valid 选择 control0，名义 mild6/6、moderate5/6。唯一失败发生在初次启动载台阶段，尚未执行停车或离台。八份强反例未发现新的结构性否决；不停车 337 帧／2 枪仍是快于停车 355 帧／3 枪的合法去程选择。

同世界 A→B→A 用途附证真实执行七次：clean1/1、mild1/3、moderate0/3。四次失败已经真实返台并向西承载 930–986px，但载台返东前未及时接上 A 岸，落入内部恢复底岸后又越出拥有格；不是放宽终点坐标就能认证。另一次失败在初次启动。clean 往返为 703 帧、4 枪、2 跳、12 币仅发一次。有限 clean 不能授权稳定返回、fresh B→A 或任意动态相位。

`probe-receipt-v1.json` 保留完整失败与状态；`return-failure-audit-v1.json` 保留真实身体、支撑与首次出界。当前 `needs_design_continuous_return_unqualified`，0 Module、0 full、0 held。API 与薄 exporter 为待交接文件，会在此状态明确拒绝签发；不能删掉回程失败把保门字段包装成可返回保证。是否只签独立 A→B 的停车末状态须由明确的新范围决定，当前未执行。

复现入口（使用新的不可覆盖运行名；预算已满，以下仅供离线复现，不代表新增授权预算）：

```sh
python3 -m pcg.prototype.creative_batches.batch30_blockn13_repair.probe_v1 --name NEW --stage clean
python3 -m pcg.prototype.creative_batches.batch30_blockn13_repair.probe_v1 --name NEW --stage noise
python3 -m pcg.prototype.creative_batches.batch30_blockn13_repair.probe_v1 --name NEW --stage counters
python3 -m pcg.prototype.creative_batches.batch30_blockn13_repair.return_v1 --name NEW
```
