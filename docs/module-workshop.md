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
3. Codex读取真实库、Cell和历史失败，用当前skills做体验去重与支持检查，补齐观察/决定、动作因果、能力/资源、地貌、可见奖励、失败恢复、来向/回程差异和廉价解法。只制作版本化设计和示意图；不支持的机关明确列缺口。
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
