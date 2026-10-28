# 固定 Module 审批中心

入口：`generation/manual-review/index.html`。同一网页每批 5 个，当前现有 225 个 Module 编成 45 批；只整理审阅材料，不生成、修改或物理认证 Module。

增量更新：`node tools/build_manual_review.mjs`。读取当前 `modules/catalog.json`，检查文件 SHA，复用原编辑器 `renderContractSvg(doc,{review:true})` 生成图；已有编号与内容不变的文件保持稳定。新增项追加，删除项不复用编号。

意见按 Module ID + 源 SHA 保存在本浏览器，切换批次不丢失，新内容不继承旧版认可。首批原页面的本地意见按完全相同版本迁入。点击复制本批评价，粘回 Codex 聊天，才算收到人工反馈；备份 JSON 包含绑定版本，不自动变更正式库。

首次 5 张定制图保留；其他图复用现有渲染器，显示 Block、Port、地貌、机关与归档动作，不把路线当作全条件可通行证明。

## 第一批反馈修订

原话已收录，首批5项显示修订稿、原意见与修改前图；基于新版本重新待审。现有正式库不变。01/02/04/05通过首轮基础动作、端口试件与有限反例检查；03低路通过、高奖励路线待修。完整校准和独立留出未运行。

本批重绘/导出：`python3 -m pcg.manual_review.publish_batch001`（先按 `pcg/manual_review/README.md` 恢复版本化证据归档），再运行统一队列更新命令。

## 当前：先设计，定稿后实现

第一批设计文件独立存放于 `designs/batch-001/feedback-002/`，格式为 `pcg/module-design/v1`，不能作为可执行 Module 或物理证据。只修改这份设计的地貌示意、端口、玩法文字，再运行：

```sh
python3 tools/publish_design_review.py generation/manual-review/designs/batch-001/feedback-002
```

本入口只重绘和更新网页，不导入工厂/编译器/Harness，不运行Godot。设计“保留”与实现、技术、试玩和生产批准分开；旧实现意见保留在原浏览器存储空间，不自动转移成设计认可。已有实现草稿和实验保留并暂停，直到设计定稿。

批次更新会合并 revisions 索引，不覆盖其他批次。已收到的人工设计意见在 `feedback/manual-review/received-design-decisions-v1.json` 按版本绑定；新版改图重新待审，旧版保留/废弃不继承到新版本。08、09 的设计废弃只改变审阅状态，当前阶段保留原库与历史图。

钩索审阅图支持 `reference_display`：直接引用原Module文件、SHA和参考版本，只补画零尺寸钩点及来源动作顺序，保持原技术状态与待审批问题。此模式不重写Module、不生成新设计版本；与几何修订设计稿分别标识。

当前排序按 `order-policy.json`：前8批及后续已收到人工意见的批次冻结。未审内容按“平原无钩索 → 其他无钩索 → 钩索”重排，每批至多5项；Module稳定编号、来源SHA、内容版本和意见键不变。普通钩索图由共享SVG渲染器的审阅模式自动绘制蓝环与H编号，使用hooks-v1图片路径防止旧图缓存；运行 `node tools/build_manual_review.mjs` 即可增量更新。

收到旧版修改意见后，新设计稿仍需复审；默认入口按当前版本是否已保留/废弃定位，而不是单凭批次已冻结就跳过。第9批116–120成员在本轮修改后继续保留。
