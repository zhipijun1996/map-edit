# Map Notes / 关卡生成工坊

本仓库主任务为《失序之钟》的离线 Module 自动生成、真实物理验证和迭代。现有网页编辑器仍是草图和审阅工具，保留工程兼容与模块库；不要把草图预览当物理证明。

- 开始生成工作先读 `pcg/WORKSPACE.md`，按任务使用 `.agents/skills/` 中的相关skill。历史报告原样保存，新的结论写新版本。
- 当前物理基线12f6cb0与编辑器库74d8a06不同。不得只改版本标签或悄悄混用；更新真实绑定后重验。
- 先做小实验；固定预算、选择规则和独立留出，不从holdout挑幸运种子或事后降低难度门槛。所有失败与运行源、命令、哈希保留。
- 用户偏好短视频下载和聊天反馈，不强制亲自试玩/填网页。视频反馈可指导节奏、可读性、重复感和结构返工，记录为观感，不编造操作手感/真人通关率/批准。
- 新能力必须接入真实机制、资源恢复和可验证动作合同；词不同不等于玩法不同。优先Module质量，之后扩Macro/Map。
- 生成/验证由程序运行。AI辅助设计、实现和分析；无实际模型调用/训练时不称AI在线生成。
- `npm run check` 保护原编辑器；`cd pcg && python3 -m unittest discover -s prototype/factory/tests -v` 检查生成与反馈规则。Godot实验另有真实日志，不以合成测试替代。
- `pcg/archives` 为版本化原件，`generation` 为可发布录像/结果；不覆盖既有批次，不提交Godot导入缓存或官方引擎二进制。

- 后续交付Module/Macro沿用Map Notes `gunman-rush-level-sketch/v1`并附`generationContract`，执行`pcg/OUTPUT-CONTRACT.md`及`module-contract.js`检查。UNKNOWN不准入拼装；逐方向、状态和版本绑定，不能由单段见证推断回程/Macro/整图。


**岩井回环空间原型v1**：见[完整报告](docs/l4-mapgen/contact-grammar-v1.md)。三Seed 12/16实例、13/18零间隙接缝，37/37（12常规、18新扰动、7回归），每图2箱48币；两段真实原生录像3187帧严格一致。仅一种有限3/4层空间文法，5父版本，尚无128网格迁移、人工趣味/正式生产准入。旧25/30及28/35失败保留；恢复contact-grammar-v1归档。

**Graph + Block128 + Module第一版**：见[分析与真实证据](docs/l4-mapgen/graph-block-module-v1.md)和[增量契约](docs/l4-mapgen/graph-block-module-contract-v1.md)。128网格/实际轮廓/边界中心Port接入原CSP、标准Module文档与Godot Harness，三个有限Seed 33/33整图，16/16精确需求热库复用后5/5重验；Map补平台0。当前仅两种拓扑，0与1同摆放，仍有重复岩井，未证明更有趣。完整44节点蓝图仍NOT_RUN物理，5 Port枢纽/主要道具/实际Boss/人类分钟未打通，不作生产准入。恢复block-grid-v1归档。
