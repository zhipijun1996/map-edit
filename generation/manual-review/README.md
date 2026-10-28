# 固定 Module 审批中心

入口：`generation/manual-review/index.html`。同一网页每批 5 个，当前现有 225 个 Module 编成 45 批；只整理审阅材料，不生成、修改或物理认证 Module。

增量更新：`node tools/build_manual_review.mjs`。读取当前 `modules/catalog.json`，检查文件 SHA，复用原编辑器 `renderContractSvg(doc,{review:true})` 生成图；已有编号与内容不变的文件保持稳定。新增项追加，删除项不复用编号。

意见按 Module ID + 源 SHA 保存在本浏览器，切换批次不丢失，新内容不继承旧版认可。首批原页面的本地意见按完全相同版本迁入。点击复制本批评价，粘回 Codex 聊天，才算收到人工反馈；备份 JSON 包含绑定版本，不自动变更正式库。

首次 5 张定制图保留；其他图复用现有渲染器，显示 Block、Port、地貌、机关与归档动作，不把路线当作全条件可通行证明。
