# N16：斜射开高门，原墙可投影

原假设是玩家必须先贴墙，把斜射铃产生的横向反冲交给墙消去，才能沿墙登顶。真实试验推翻了“必须贴墙”：近墙和64px离壁方案都用1枪1跳开同一永久门、登同一高岸并取8币，离壁更快、上岸高度余量更大。**归已有定向反冲玩法的 Block 接口适配，新增家族0。** 不以缺 `wall_contact` 字段拒绝有效解，也不加刺强迫原案成立。

近墙演示的原碰撞确实有效：真实 `move_and_slide` 法线为左，burst期间 `recoil_velocity.x` 归零而 y 仍向上，角色完整跨过256px高差后落到原墙顶；墙侧接触没有回枪，只有顶面或原低岸实际接地才回枪。使用原 Motor / ShotLatch / 枪资源 / 弹丸，0新Cell。新增 runner/main 只是读取原碰撞和速度的观察器，无人物/世界状态写入。

```text
                                  永久门       B →
                        石壁顶━━━━┃━━━━━━       floor352
                        │ ↑
A →━━━━低岸━━━━ 起跳     │
                  ↙铃   │                     floor608
           保留恢复阶                          floor736
                 保留底岸                      floor864
```

原卡 B31-N16：`pcg/creative-production/batch30/block-next-ideas-v4.json`，SHA fac274d6…，当前 Codex 子代理来源。A W边中心[0,576]、身体dock[24,590]；B E[1024,320]、身体dock[1000,334]。8×8 Block128完整拥有格，不造实体外框；W/E外邻均不拥有。初低岸比概念延长12到墙面608，保证近墙全身体支撑；其他原墙、恢复阶和底岸全部保留。门后真实一次8币箱在拥有格内，不冒充零奖励Map请求。

48/80真实探针，两规则已用：

- 首8：580/hold24的贴壁投影与532/hold20离壁方案都成功。near596准备阈值不可达到：原safe_margin使身体中心最大595.925，5例射前超时；全部收费、原件保留。
- 第二规则仅把596准备阈值改592，其余几何/物理/能力不变。新8：两个near控制和一个原6°瞄准扰动通过；64离壁成功、128离壁与普通跳失败；地面预开+竖射2枪1跳是合法方案；横射失手→真低岸落地回枪→同世界重试2枪2跳成功。
- noise前按事前近墙清洁案例的完整身体高度余量，固定580/hold24(31.567px)，另近墙596/hold20为26.045px。匹配离壁532/hold20为46.535px；初样276帧对近墙281帧更快。
- 公平噪声24/24：near与离壁各 mild6/6、moderate6/6。near12/12实际投影，离壁12/12无burst墙投影，支持“机制可选、原创新关系冗余”结论。
- 7优先精确反例无额外机制反驳；零枪、射空、2枪越门未到同目标；离壁和地面提前开门均按实际目标接受。
- 同世界去程取奖、B真正稳定19帧、沿已开门返回A：1枪1跳525帧，通过一次clean。不是 fresh B→A通用资格。静态Definition保留真实A/B marker，fixture实际goal/end明确A，未伪写Module自口路线。

所有成功名义与上述成功试件的完整24×36身体/相邻帧保守扫掠均在冻结拥有格。原结果路径：`pcg/results/workshop-batch30-blockn16-{core-v1,core-v2,noise-v1,counters-v1,return-v1,preflight-v1}/`。失败、提前开门、原永久开门状态和资源逐帧保留。

标准只交 A→B；fresh B→A、泛化恢复、任意输入速度、第二镜像接口、接缝和全图 UNKNOWN。一份clean恢复/返回不替代原regular完整验证。第二规则额度已用于真实阈值修复，未为镜像再追加第三规则。原Python Block/route消费者、20精确反例绑定、原标准导出/Block JS、runner/native Godot语法均通过，0physics检查不计技术准入。

```sh
python -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --rules pcg.prototype.creative_batches.batch30_blockn16.api_v1 \
  --name workshop-batch30-blockn16-full-v1 --index 26 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v7.json
```

源冻结后由root执行原完整校准/留出/入库；这里尚未声称通过。可玩 `main_v1.tscn` 继承原Workshop。人工观感、试玩、生产准入 UNKNOWN；不建第二物理/验证框架/候选库/Map Generator。
