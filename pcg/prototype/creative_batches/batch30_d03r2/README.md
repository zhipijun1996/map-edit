# D03 r2：实际碰撞与落地余量修复

v8完整留出失败原件保留于 `pcg/results/workshop-batch30-d03-full-v1/finite-enemy-routes`，不是技术候选。本新周期由 `pcg/creative-production/batch30/protocol-v6.json` 预声明，新的完整calibration/holdout种子261031001/261031002交根执行；此目录仅120个probe，不宣称已过完整regular。

旧calibration证据：main/east-staged moderate trial1/5/8在第6帧受到shared-sentry实际接触伤害。axis先执行，受噪声影响jump第5帧才生效，身体尚未升至安全高度就进入敌人碰撞范围。east-staged trial11第54帧x355.94/y269.04、下帧脚通过平台顶290时仍在左沿370外，随后身体被侧面挡在357.93而跌落。

v1先原地跳，6帧后向右，保留原真实动作/资源；东第一接收面向左扩至300+接口35，右沿/顶部不动。所有7路线/奖励/敌人共享这个新世界，两接口均保留。未改角色、敌人HP/碰撞体、射线、物理、噪声或门槛。

结果：两接口clean14/14；每路6个旧cal moderate共84例，east-staged/main/west-staged两接口均6/6；air及以air开头的连续线4/6，失败为第二枪真实射偏，保留原件。额外接口0 east-staged/main moderate trial6..11均成功，因此这两路各12/12；两接口关键路线mild8/8。新几何剩1HP的实际对照仍成立：west-air失败但落底层安全，west-staged取得两宝且敌仍1HP。总120/120预算。

冻结入口 `pcg.prototype.creative_batches.batch30_d03r2.api_v1`，规则 `rules_v1.py`。完整反例/新calibration/新独立holdout/标准合同/入库交根统一。不得由probe改善将旧held失败改标通过。receipt-v1.json给全部原件SHA、真实失败与命令。

```sh
python3 -m pcg.prototype.creative_batches.batch30_d03r2.screen_v1 --name fresh-d03r2-clean-i0 --interface 0 --level clean
```

复现需独立新目录，不覆盖原件。开发probe预算已耗尽，不重跑挑种子。
