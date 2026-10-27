# N11 / A4：同侧错位端口的反冲入檐袋

冻结入口 `api_v1.py` 交根任务原full index22，两接口各一条A→B。W/W与真正水平镜像E/E都重新跑原物理，不继承旧库或镜像资格。这是原A4 family的两个Map适配版本，不计新基本玩法，人工趣味/试玩/生产批准UNKNOWN。

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 \
  --name NEW_IMMUTABLE_NAME \
  --rules pcg.prototype.creative_batches.batch30_blockn11.api_v1 \
  --index 22 --interfaces 0 1 \
  --protocol pcg/creative-production/batch30/protocol-map-block-v5.json
```

构图是同一厚岩的上下两面：先从上岸走到外侧，完整身体落至檐底308以下，向外开枪刹落速并折回，落入可见10币袋。主见证1枪0跳；原底岸上的1跳1枪恢复是真实付费替代，按原资源执行。反冲方向、枪、跳、目标、所有实体和actor_x比较都在E接口完整镜像，重力不镜像。

|接口|A边界锚点 / 身体dock|B边界锚点 / 身体dock|拥有形状|
|---|---|---|---|
|W/W|[-256,192] / [-232,206]|[0,448] / [24,462]|35格，不规则，1408×768|
|E/E|[256,192] / [232,206]|[0,448] / [-24,462]|35格，不规则，1408×768|

上岸左/右延26、袋外边裁25、袋内沿75→96延21，均在预登记32px单岸范围；上岸顶改+16、袋顶+14/−16时保持原bottom，上岸仍到底308，袋厚51/81，没有负高度。两份原底岸完整保留。没有外框、Map补平台、传送或恢复赠送，所有外邻拥有格保持排除。

`protocol-v1.json`在首probe前登记宽75/96以及每接口2个外探枪点，共每接口4候选。8clean全通过，但75宽部分首次真实袋落脚只是悬边，身体左右余量为负。各几何四个0枪/最长跳反例共16次全部未到同奖目标，随后严格按clean首次真实袋落脚24px身体左右最小余量排序，noise前冻结两口都宽96/control0：W20.500px、E24.833px。没有看noise/held换选择。

当前76/80 probe、1/2规则：8clean、16几何反例、20更多反例、24名义扰动、8恢复扰动。名义mild/moderate两接口各6+6，24/24；更多反例0反驳，其两份原底岸恢复clean通过，252/260帧，1枪1跳；恢复另mild2/moderate2各接口合计8/8。恢复只是这些有限小样，未签原regular/held或通用失败恢复；B→A仍UNKNOWN。

所有物理使用原WorkshopEngine、Motor、Router、枪和SimpleRoomReward。除每帧24×36身体拥有格，另用膨胀12/18的原厚岩和真实帧间线段检查完整身体的二维扫掠，接触不当穿透，不能只看角色中心。确认实际Platform1袋顶落脚、原回枪、最终dock稳定和10币，不把碰袋底/侧面当到达。16个0枪失败不证明不存在其他绕法，根full仍每精确源执行20个反例。

原A4两份有效case/record/doc的实际文件SHA核验在`source-baseline-v1.json`；原模型N11卡与W/W、E/E空间需求在`idea-source-v1.json`。`source_map_request`保存明确派生需求，实际Map的edge赋值、奖励预算、全部有向对仍待联合绑定，不以单A→B顶替双向需求。最新862b合同静态回执在`latest-map-static-v1.json`。

原输入、压缩raw、源码快照、全部候选和失败在`pcg/results/batch30-blockn11-{clean,critical,counters,screen,recovery}-v1`。`probe-receipt-v1.json`提供计数、来源、身体余量、选择及源码SHA。完整校准/留出、持久入库与标准文档由根full生成；单Module成功不替代边界接缝或B整图验证。
