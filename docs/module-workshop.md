# Module 工坊

入口：[模块库与创意](https://zhipijun1996.github.io/map-edit/generation/module-workshop/)。编辑器和旧设计审阅页均有入口。

网页是现有库、审批和实现回执的只读投影，不是第二个候选库或 Map 生成器。正式资源仍由 `modules/catalog.json` 管理；设计继续使用 `pcg/module-design/v1`，实现交接继续使用 `feedback/manual-review/implementation-handoff-v1.json`，物理实验继续使用原 Godot Harness。

## 查看模块

大小用 Block 宽、高精确筛选，可叠加 Port 数、区域、进入侧、离开侧和能力。方向指 Port 所在边，不把角色移动向量或镜像当成反向认证。Route 方向和能力必须由同一条 Route 满足；往返还要求同一对 Port 的反向声明存在。能力筛选沿用 `allOf` 与 `anyOfGroups`；`partial/unspecified` 标记不完整，不升级为能力已满足。详情显示全部 Port、N×N 有向矩阵（含自环）、逐 Route 能力和 UNKNOWN，以及具体版本与证据链接。

首次接入以实现分支固定提交 `08012fbaed5c5eba2eca1b94de4823a97967b0b7` 为来源，PR #25 尚未合并。原报告67项PASS，其中157和174引用的设计版本与当前交接不一致，保持待对齐；其余65项包括已原样保留在主库的134，以及64项待合并候选。另有5项待修复；新增环岛设计认可后当前11项待实现。网页并未将候选提升为主库归档，也未重跑或重新认证物理证据。原生加载通过不等于所有 Route 的 Foundation/Map 认证通过。

- **已归档**：主库目录中真实文件及其哈希、内容版本和当前认可范围匹配；所有字段通过现有合同检查。134为人工原样认可的既有归档。
- **已实现候选**：实现回执绑定当前获认可设计；结果PASS、原生加载通过、真实 Module 内容版本与共享合同静态检查通过。来源分支尚未合并时仍是候选。
- **待修复**：现有结果失败、设计冲突或必要检查缺失。
- **设计版本待对齐**：实现引用另一设计版本，不自动追认实现侧的澄清。
- **待实现**：只有设计认可，尚无绑定当前设计的实现回执。

技术可靠性、人评设计、视频观感、真人试玩、生产准入分别记录。全部新内容生产、物理实验和旧迁移批处理未因此恢复。

## 创意进入和快速图文迭代

1. 人工填写创意原话、可选标题与约束。每份本机草稿有“修改/删除”按钮，修改回填原表单、可取消；删除可撤销并持久保存，已提交创意/已发布设计保留。修改已被仓库登记的本机ID时另存新ID，避免覆盖收到的原话。网页生成稳定 `idea-…` ID，保存本机草稿；可导出/导入JSON备份。原话与后续解释分开，不因解释改写原话。
2. 点击“复制给 Codex 画图”并粘回当前聊天。AI创意按钮生成带实际库背景的提示词，粘回当前会话后由真实大模型创作；网页没有独立模型接口或秘密密钥，也不假装已调用模型。模型来源、实际调用者和未知修订分别记录。
3. Codex读取真实库、Cell和历史失败，用当前skills做体验去重与支持检查，补齐观察/决定、动作因果、能力/资源、地貌、可见奖励、失败恢复、来向/回程差异和廉价解法。AI创意默认同一轮直接制作并发布版本化示意图，每批5份，文字仅作内部中间记录；无需用户另外要求出图。不支持的机关在图上明确标出缺口，仍不直接实施。
4. 用原图稿渲染器发布图片。你在网页选保留/修改/废弃，复制带设计版本和文件SHA的反馈回聊天。浏览器选择只是本机草稿，不能直接改仓库审批；改图产生新版本并重新待审。
5. 收到当前设计版本的人工保留，加入**现有**实现交接清单。独立实现会话按该精确快照补参数、实现真实Cell、执行原Harness及质量/反例/恢复验证。失败回到修复/图文迭代，原失败记录保留；不以 `implemented=true` 进库。
6. 实现会话仍写 `feedback/manual-review/implementation-results/` 的既有回执。网页索引链接回执、源码、可玩包及影片。经现有归档流程进入 `modules/` 并更新catalog后，网页才显示已归档；不自动给予生产批准。

已发布一份AI流程示例“环岛分流：追台，再选择离岛时机”，由当前Codex会话提出，参考用户以前的环岛方向；已按设计版本 `sha256:f665b6d2c9e342f2aac01a0cf27587a8261cb895664c94f47e4da0e84086b462` 获得人工保留并进入待实现；尚未声称新家族、已有圆轨规则或已验证三口互通。

## 可执行入口

```sh
# 更新只读展示索引；不运行工厂或物理
node tools/build_module_workshop.mjs
python3 -m http.server 8080
# 打开 /generation/module-workshop/

# 从固定实现提交刷新回执和真实接口投影；哈希逐文件校验，不合并实现PR
python3 tools/sync_workshop_implementations.py --ref 08012fbaed5c5eba2eca1b94de4823a97967b0b7 --pr 25

# 将网页导出的人工草稿备份登记到创意入口
python3 tools/module_workshop.py intake /tmp/module-ideas-backup.json
# AI入口也可提交 rows；sourceType=ai_idea并记录source.producer，stage仅可为IDEA

# Codex准备pcg/module-design/v1结构后，用原渲染器发布，旧版保留
python3 tools/module_workshop.py attach-design --id idea-xxxxxx --design /tmp/design.json

# 收到真实聊天反馈后登记精确设计版本；不能由AI自行制造人工保留
python3 tools/module_workshop.py record-decision /tmp/human-receipt.json

# 实现完成后链接已有标准回执；归档资格仍由主库真实内容决定
python3 tools/module_workshop.py link-result --id idea-xxxxxx --result feedback/manual-review/implementation-results/example/result.json

# 静态与浏览器检查
node tools/check-module-workshop.mjs
python3 -m unittest discover -s tools/tests -p 'test_module_workshop.py'
python3 tools/browser_module_workshop.py
```

人工回执最小格式：

```json
{"id":"idea-xxxxxx","sourceType":"human_feedback","verbatim":"用户在聊天中的原话","designVersion":"sha256:当前图稿版本","decision":"KEEP"}
```

`record-decision` 拒绝旧版或已解决版本。KEEP只增加待实现交接，不实现Module；CHANGE继续迭代；DISCARD保留来源与图稿备查。网页仅保存在浏览器的创意/审批必须复制回聊天或导出交给Codex，GitHub Pages不提供共享写入后端。

`npm run check` 前会自动重建展示索引，索引过期或批准/源码哈希不匹配会拒绝检查；归档流程更新主目录后无需手工改网页卡片。

新网页的构建资源也包含在 `tools/build_editor_site.py --no-history` 的静态资源闭包中；刷新目录读取已发布索引，不执行模型或运行未完成实现。

本轮人工创意 `idea-0363f85c-16c0-4b5f-b3b0-461335608db7` 提供2怪3×4与3怪3×5两份备选图稿。两个规格沿用同一人工原话/创意ID，不增加玩法家族数；审核反馈分别绑定各自版本。保留某个已发布方案时精确选择该版本进入原交接，废弃一份不自动废弃另一份未审方案；如需两份同时实施须按同一基础家族的规格适配交接，不冒称两个独立创意。解析尺寸预算和真实机制源码绑定见该创意的 `source-analysis.json`，不是物理通关证明。

创意阶段筛选同时覆盖本机文字草稿和已登记创意：纯文字未出图、已出图未审核、已审核未实现（包括待修复/版本待对齐），另有废弃记录。筛选保存在本机；已登记的本机副本可单独管理，不重复计待办。已实现的当前版本只在正常模块库展示；旧版本通过、布尔implemented字段或未合格实现均不能隐藏当前待办。

两怪/三怪方案已根据用户“新增加这两个保留”同时批准，分别绑定原f0829bf8…/61124f9e…版本，以`-enemies-2`和`-enemies-3`独立交接，保留相同sourceIdea ID。当前85项交接、13项待实现。批量精确批准入口：`python3 tools/module_workshop.py approve-variants /tmp/human-receipt.json`；回执包含真实原话、`sourceType=human_feedback`和已发布的`designVersions`数组，先全部核对再写入，任何旧版失败都不部分批准。设计认可仍不执行实现或升库。

随后用户按设计16d930fb…及文件d06d31fe…保留《错相升井》，当前86项交接、14项待实现。新创意`idea-31639e2c-1a4a-487c-b1ea-c52522549fa8`以一个人工原话来源提供六个独立审核规格：宽×高1×2、2×1、2×2，各含左↔上、左↔下两口。每份仅两块可穿平台，普通跳可行时接受；这是同一家族的接口适配，未宣称新玩法或已实现。六份分别使用已发布designVersion/SHA接收反馈，尚未获保留；真实双向、完整身体通行、回程、边界封口和接缝均UNKNOWN。

用户随后“均审核通过”保留这六个已发布规格；原批量精确批准入口核对全部版本与文件SHA后，为六个variantKey分别建立待实现交接，来源仍为同一个人工创意。当前92项交接、20项待实现；六份图稿不重绘、不改变版本，不授予技术验收或生产资格。

接口需求图的八个代表已登记为`idea-interface-s01-001`等八份文字提案，可在“纯文字未出图”查看。源需求和图像逐字/逐口索引见`feedback/module-workshop/briefs/interface-complements-v1.json`，左右岩体口与上下可穿口严格区分，不把刚认可六份可穿左口直接算成岩体口适配。S01/S15优先复用旧家族，其余只是新的用途设计方向；未画图、未认可、未实施，不增加交接数量。

用户随后“直接出图吧”授权八份图稿，现均转为“已出图未审核”，逐版本接收反馈；原文字来源保留。图稿严格匹配八份需求的尺寸与Port，S11/S12分别列6/12个有向目标，S13仅L→L奖励自环。S01增加128px起跳准备段解决旧双靶高度预算不足；S13明确新增入袋换门触发缺口，避免普通双门原路退回使回路冗余。图面、完整身体与机制证明分开，所有技术状态仍UNKNOWN，不增加92项实现交接或改变已认可图稿。

首轮八图反馈已收：S01/S13废弃，S02/S07/S11/S15保留。S09按“删一行后保留”裁去顶行成3×4并重新绑定新版本/文件SHA；原3×5需求原样保留，协商后的3×4与左口第0行单独记录，不能继续按旧接口匹配。S12仅加一只交接区空怪，修订版待审，未加入实现清单。当前97项交接、25项待实现；本批待审仅S12。重复内容优先复用、奖励应有相称挑战的经验保存在原话回执并写入创意skill；不因用户喜欢换门思路而复活S13设计。

用户随后“s12可以了”保留加怪版c0c0d757…/文件caf1aedb…，精确快照已进入原交接。八图审阅关闭：6保留、2废弃、0待审；当前98项交接、26项待实现。仅更新认可记录与网页状态，不重绘或实施，不授予真实12向可达、试玩或生产资格。

下一轮HQ01–HQ05已登记为“纯文字未出图”：双台冻结成阶梯、移动掩体、诱导冲锋换位、领取奖励后改走低回路、折射击铃。两项使用已有Cell提出新布局，两项缺控制/奖励事务绑定，一项缺镜面Cell；详细来源、去重与条件见`feedback/module-workshop/briefs/plains-hq-five-v1.json`。五份均未画图、未认可、未实施；尺寸和备选接口只是待求解条件，不增加既有交接数量。

用户明确以后AI创意直接出图；HQ01–HQ05现已全部转为“已出图未审核”，每份有独立版本、文件SHA和审核表单。图上直接显示关键路径/前后状态及支持缺口，HQ02画出已发射敌弹的预期实体截点，HQ04以两色区分取宝前后路线，HQ05区分反射弹丸长路与人物路线并保留重试接岸。绘图仅作静态几何与图面检查；未实施规则或运行物理。网页AI按钮提示词、创意skill与工作规范已同步为同轮交付图文，文字筛选仍用于人工草稿和中间记录。

HQ首轮反馈已收：HQ01/HQ02/HQ04精确版本保留，现101项交接、29项待实现。HQ03在左右横檐上方加带实体底层的危险区，并裁短顶接岸保留T口净空；HQ05按人工意见替换为受击固定方向发射炮台，蓝色玩家弹在炮台终止，紫色新机关弹再击铃。炮台不是反射镜，身份/资格/冷却规则需补；两份新图仍待审，旧图与来源反馈保留。此轮不实施真实Module或运行物理。

HQ第二轮反馈见`feedback/module-workshop/review-receipts/hq-feedback-002.json`：HQ05当前炮台版精确保留，HQ03改岩面边界地刺后重新待审，历史图保留。HQ06–HQ10同轮直接出图，提案及Cell缺口在`feedback/module-workshop/briefs/plains-hq-second-five-v1.json`，不新增真实Module。当前102项交接、30项待实现；图稿待审共6项（HQ03与新五份）。五份不自动计五个新家族，技术、实际回程、镜像和接缝均UNKNOWN。

HQ第三轮：原话回执`feedback/module-workshop/review-receipts/hq-feedback-003.json`。HQ03/HQ07/HQ08按当前已发布快照保留，105项交接/33项待实现；HQ06/HQ10设计废弃，来源和图稿保留。HQ09延长上门到模块全宽、改竖向只挡弹板，人物使用固定踏台；只挡弹且不承载是尚缺的碰撞规则，不是已有实体台能力。新图待审，不继承旧版认可；直接射铃绕过炮台仍明确列入反例。

HQ第四轮：回执`feedback/module-workshop/review-receipts/hq-feedback-004.json`绑定旧699e58图稿的修改意见。新版删除全宽门，采用出口可穿台上下表面尖刺初始伸出、目标铃命中后同组收回，平台本体始终保留；当前按一次收回/本场景不重伸画图，未获人工保留。竖板沿用只挡弹不承载。危险初态T尚未认证安全接岸，邻接模块带速/穿伤/绕刺和上侧访问待验；105项交接不变。

精确接口第二轮：`feedback/module-workshop/review-receipts/spec02-request-v1.json`逐字保存十份Block/Port需求与“h09 ok了”。HQ09最后dba700刺台版保留后106项交接/34项待实现。新`idea-spec02-*`十图仅为待审设计，尺寸/Port精确复用原话；S11六向、S12十二向、S13的L→L自返回，总33条目标全部UNKNOWN。来源、家族复用与缺Cell见`feedback/module-workshop/briefs/exact-ports-round02-v1.json`。与旧接口同形不继承旧审批，旧废弃S13不复活；本批十个规格不是十个新玩法家族。

精确接口首评：回执`feedback/module-workshop/review-receipts/spec02-feedback-001.json`冻结三项修改与“其他通过”。S02/07/08/10/11/12/13按原快照保留，113项交接/41项待实现；已保留七图不重绘。S04只加两空怪；S06移除射手掩体，改离台绕射台下随动铃并追接；S09移除静态锯口，改互补井盖与错侧安全段。三份新版仅待审，尺寸/Port不改。随台接收体及井盖危险面同步绑定仍缺，所有反例/恢复/回程与物理均UNKNOWN。

精确接口二评：`feedback/module-workshop/review-receipts/spec02-feedback-002.json`记录“S09没看懂，完全重新设计；其余ok”。S04/S06按最后图稿保留后115项交接/43项待实现。S09旧互补井盖退役，新稿只保留3×5及L/B精确端口，以一枚上下齿轮控制同一横穿窗口的上下净空；图中给出同一窗口两相位对照。不新增Cell、不调用物理，布局规则与实际可达/资源/恢复/绕行仍UNKNOWN；只有新S09待审。

精确接口三评：`feedback/module-workshop/review-receipts/spec02-feedback-003.json`记录左侧只留一平台/齿轮对齐、右中台换空怪。为守住原ROCK口，保留左入口岩台删下方观察台，齿轮中线和窗口上移96px；右y512中间台换plains_diver，另外两右平台不动。尺寸/Port不变、115项交接不变，新图待审；删台后的上返及敌死亡后返回未验证，不补台或刷怪。

精确接口四评：`spec02-feedback-004.json`记录“ok了，通过”，精确保留S09最后ba9155075c23版，图稿原字节不变。该十份规格设计全部保留，116项交接/44项待实现；无待审新图。本次只登记人工设计意见，不执行实施/物理，不升级技术或生产资格。


大房间取宝提案：`feedback/module-workshop/briefs/plains-large-treasure-three-v1.json`与原话回执`large-treasure-request-v1.json`记录LG01三台留路（10×7）、LG02双门连穿（9×8）、LG03三折刺檐（10×7）。三份同轮出图，均是单L口INOUT ROCK、含领取宝箱事件的L→L自返回目标，只需jump/shot_recoil，当前待审核，不增加116项交接或44项待实现。LG01保存去程冻结构型供回程使用，LG02两次独立限时门后接箱前制动，LG03低檐换向后追动态落点；是已有家族的连续Macro组合，不算三个新玩法家族。静态射线/边界/手机检查见`large-treasure-three-conformance-v1.json`，不能据此宣称反冲可达、时序窗口、真实防夹、失败恢复或回程已验证；精确版本保留前不实施。
