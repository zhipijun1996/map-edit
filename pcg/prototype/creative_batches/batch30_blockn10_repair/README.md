# N10：近铃让出第二条弹道，闭门后还能真实重试

**最终状态：needs_design，0 Module，held未跑。** 根full-v1实际107例，正常cal mild12/12、moderate11/12；恢复cal mild12/12、moderate5/12，原regular拒绝整份双canonical需求。没有删除恢复路线救过、重开第三周期或改源。只读`full-failure-audit-v2.json`核出：4例恢复枪实际打到闭Near门，1例恢复成功且重落M但后续单向定位没回到正确射位；另2例实际到奖到出口，但闭门站位1118/1122超出作者1108±6检查，原拒绝保持，即使按raw到达7/12也不足.65。全部失败均先真实到M，问题不在初段登M。

冻结入口 `api_v1.py` 提供**同一个物理世界的两条 A→B canonical**：正常2枪2跳，及真正等Near关闭、射右恢复铃重开、重新落M回枪、再射Far的3枪3跳路线。两条都必须通过根任务原 full，才可入库及声明这份恢复；B→A仍UNKNOWN，不能把两条见证计为两个Module。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_IMMUTABLE_NAME \
  --rules pcg.prototype.creative_batches.batch30_blockn10_repair.api_v1 \
  --index 18 --interfaces 0 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v4.json
```

原模型卡 B31-N10 在 `creative-production/batch30/block-next-ideas-v2.json`。近/远是两个独立原ShotLatch：近铃先真实拦弹、开门时自己的接收器变layer0；人物落M真实回枪，第二弹穿过失活近铃击Far。近铃关门恢复layer8时会重新拦截。三组原机制对照3/3通过，有实际layer和impact，未造sequence框架。它是G03/G11/G21的扩展假设，不按标题认定新家族。

完整原型增加普通岩体深腔、窄喉和外伸屋檐，限制直接绕背；开口本身不是玩法。Far在[832,672]，Near在[864,672]；屋檐迫使首枪从第一门前的空中射窗发出，先近后远由碰撞决定。M[1064,800,128,64]是真实中岸；B改为下行864地面，属于明确派生空间需求。A锚点[0,704]、身体dock[24,718]；B锚点[1280,832]、dock[1256,846]；10×9 Block、128倍数尺寸，没有外框、Map补路或资源赠送。

先前周期的2规则、63个Godot输入完整保留为needs_design，其中60个实际跑帧、3个在定义检查时0帧拒绝。首版moderate2/6，后续实体修订清洁通过，但发现真实M侧闭门会挡住返回主铃的弹丸，旧迟射试件因此失败，不能忽略软锁入库。新周期只增加原有`return_access=[1088,672]`，全部其他地貌、门、普通控制不改；其原右侧发射条件、弹丸、health epoch、防夹、承载、枪与冷却仍由原组件执行。

新周期严格1规则/17 probe：正常clean2/2，固定c0后mild6/6、moderate6/6；真正闭门重试clean/mild0/moderate0共3/3，分别586/602/590帧。重试先站1108远离Near防夹范围、等140ticks，观察原门闭合、主/恢复接收器layer8；下一枪仍瞄Far，但实际被右Near恢复铃截获。原身体重新落M回枪后，第三枪到Far；同一个角色、资源、时钟与奖励事务，没有重建或重置。

正常Near→Far约79ticks；恢复后最新Near→Far为68/74/66ticks，均在原2.2s=132ticks窗口内，观察使用原`clock-opened_at`，不把防夹延时当计时余量。每帧24×36身体、两扇实际门碰撞层、M回枪、远岸稳定与12币均检查。此前三组机制对照不能代替完整路线，新世界也没有继承旧几何反例结论。

根full将实际执行正常20个、retry23个精确绑定反例，含绕背、越顶、普通长跳、省两枪、地面提前准备、真正站M长等、防夹、迟射和省恢复。旧late-M模板实际先向左走再等，已保留旧输入并在新路径修正。省掉人工刻意延迟，或多付准备枪，只要实际Near/Far/M/身体/奖励/窗口成立，就是可接受解；`counter_policy_v1.py`按实际核心判定，未使用counterkind白名单。canonical恢复见证仍严格要求真实闭门、恢复弹丸与重新落M，不用普通解冒充。

原件在 `pcg/results/batch30-blockn10-repair-{clean,retry,screen}-v1`。`probe-receipt-v1.json`保存源码SHA、旧63+新17=80输入案例账本（实际跑帧77、0帧拒绝3）及闭门/impact/回枪记录；`latest-map-static-v1.json`按最新862b原Block/spec校验。这里只消费明确派生的12币下行需求，没有冒称满足实际Map奖励预算、任意入口状态、完整图或通用接缝。额外底岸恢复、反向、人工趣味/试玩及生产批准仍UNKNOWN。
