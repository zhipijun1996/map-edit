# PCG 研究交接

最新 **PCG-FACTORY-05**：独立分支 `feature/offline-module-factory`，代码 `prototype/factory/`，说明 [FACTORY-REPORT.md](FACTORY-REPORT.md)。production-v1为冻结旧分类：1002物理/65批、82去重策略、136.15秒、658文本源/870原件无漂移；v2同6finalists同留出收紧为显式regular，4待真人+2返工，人评0批准0。父代配对诊断另36次，载人二段跳parent clean0/12→child12/12，mild6/12→12/12，moderate5/12→10/12，不代表趣味改善。

最终网页 `delivery/factory-v1/web-release` / `browser-release`，新场景 `main_factory`只观察原V3不改Motor，PCK216772字节；5回放/实际手动输入/隔离合成反馈/导出/草稿重载均过。**反馈导入用网页catalog.json**，它在技术v2catalog上另绑定实际PCK及表现/UI源；不要拿无表现绑定的技术catalog接受试玩反馈。合成反馈→实际Godot诊断返工见factory-feedback-loop-test-v2：1/1目的通过，生产/真人/批准均0。无真实人评可回收，不得把自动化测试计成人评。21Python测试过，独审见research/factory-audit.md。完整失败与快照在离线数据包，生产器没有resume CLI。

新批次/新模块需要新目录，旧轨迹、旧发布不得覆盖。扩大测试前先回收真实反馈，有限修复后重新留出和盲评。精密门槛必须事前指定，不能把regular失败事后改称高难通过；低成本反例即返工。正式游戏/Map Notes/Runtime/Macro未接入。公开入口和逐字节校验以PUBLICATION-05.md实际回执为准。

PCG05已公开：研究源7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6 / PCK b69a52727616，Pages39987039629 success，公网22项完整字节与5回放覆盖4模块/操作/评分导出/隔离均过。原始数据3分片已重新下载并合并，4111文件hash/CRC全过；下载脚本和清单在PUBLICATION-05。公网测试客户端IPv6及JS数字往返问题已修，失败/成功与实际工具源额外收据包26文件已公开复核，原页面/物理未更换。人评0，批准0。托管main af4e015仅追加非site收据，实际Pages仍182cf0b。CLI凭据失效时改走已连接GitHub API，blob/tree与本地Git完全相同，expected_sha非force更新；不需要用户重认证。

最新 **PCG-DYNAMIC-04**：见 [DYNAMIC-REPORT.md](DYNAMIC-REPORT.md)。新增真实原移动平台/锯轮/宿主荆棘/伤害政策和段落回退的正常Node调度研究worker；未改正式游戏或编辑器。动态搜索600次、最终留出/扰动/替代评价703次；12候选中4条发现更低成本通路并显式警示，不签动作必要性。载人二段跳随机初相位仅25/36通过，不能以4相位校准全过替代留出结果。

新增 RegionSpec JSON 与实际几何编译器，`prototype/dynamic/search_regions.py --region regions/sky_islands.research.json` 从基础Cells/动作生成：16提案→8真实连续合格浮岛模块，其中3条墙跳+空跳+钩索+反冲混合；轻扰动59/64、中39/64通过目的验证。区域几何变换必须使旧回执失效；2条中途落地假连续已剔除。弹射蘑菇/孢子气流未实现，mushroom proposed执行必须明确拒绝，不能普通平台改名。20区域合同测试通过。

`main_v3`/`modules_v3.json` 是新场景与17条预生成研究候选；不改旧V2。17条共7404帧在真实场景与生成器逐帧对照通过；四段28.2秒原生录像包括浮岛混合链。所有本地详细证据在 delivery/dynamic-v3，完整动态/区域原始结果在 results/dynamic-* 与 region-*（因原输出>100MB不纳入git，交付包应包含完整数据与逐文件SHA）。公开交付回执应查看 PUBLICATION-04.md；未有回执时不能沿用旧V2 URL冒充新版本。

当前仍不签人类趣味、苦痛之路级质量、任意未注册能力/机关、在线Runtime预算、多机关联合相位、正式区域Bible和Map Notes消费者。下一步以真人盲测/替代解规划/多种子多样性为主，再扩Macro/Map。下方保留历史记录。

最新 PCG-REPETITION-03：用户明确可反复蹬墙、二段跳恢复循环与重复组合，并将荆棘压力区/移动齿轮/移动平台列为后续核心。已修walls/anchors伪库存、加入真实再贴墙循环、显式长度预算、拒绝无词空串回退、接收面提前截断问题。详情见COMPOSABLE-REPORT最新段及research/repetition-review.md。repetition-v5的12墙链（含6蹬+6空跳）与4钩+4空跳均真实词匹配、无中途落地并稳定出口；纯四钩失败保留。v3/v4中途落地问题不得误签连续恢复链。

最新开发54573a对所核对动作路径与12f基线无差异，870原件无漂移。尚未验证慢时/构筑/正式动态消费者。下阶段先接真实动态对象与多相位规划，做3类机制黄金和真人试玩，再扩质量多样性/宏图。新版多settle模块尚无公平固定策略噪声对照，不能沿用旧V2成绩；本轮未发新Web。

第二轮公开交付与验收见 [PUBLICATION-02.md](PUBLICATION-02.md)。公网242项完整字节校验、20个真实输入回放全部通过；Pages已success。

第二轮 PCG-RESEARCH-02 已在独立分支 `feature/composable-action-search` 实现能力合同、动作树推导、真实运动布置、状态反馈、成对噪声与有限捷径反例细化。最新说明 `COMPOSABLE-REPORT.md`，独立审查 `research/composable-review-v2.md`。

16 个固定移动+跳跃基底能力组合生成覆盖；六ID的64子集绑定矩阵36合法/28拒绝，不等于全部挑战生成覆盖。三轮1134提案→2000几何→1668稳定，173实际动作词不是173种趣味。最终20候选反馈轻389/400、中363/400，对照固定306/400、219/400；8/8反例细化保留见证。三个退化模块及双钩低容错明确warnings；17个无发现捷径不证明能力必要性。

`prototype/composable` 是新算法；旧代码与产物保留。新默认场景main_v2，旧场景可显式运行main.tscn。生成器支持显式能力列表，新能力需真实绑定/合同/几何/测试，不允许仅添加ID。追加move+wall关闭jump和jump+double关闭move都生成正例，no-move首次失败保留。

20真实输入展开回放、20本地Web回放、六段原生录像和20份Map Notes草图结构检查已过。Web新pack约65MiB；公开发布应共用第一轮字节相同的JS/WASM依赖，避免碰900MiB guard。正式游戏/编辑器未修改。趣味、正式消费者、Runtime、真人设备仍未验。

下面保留第一轮交接记录。

研究运行源 7c7b42e46e33c895d51741c1ca5d26a516568a27；游戏基线12f6cb0；公开build 8f8ded8ce59a。

https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-RESEARCH-01/7c7b42e46e33c895d51741c1ca5d26a516568a27/8f8ded8ce59a/

完成：论文/代码/许可审计，受限同域582-case对照，609-case交付评价，6试玩条目（5几何），21项实际Web GUI与公开6回放，真实20.7秒录像，6 Map Notes草图。

已保留：校准失败、CP域不公平V1、修订V2、最小导出缺动态依赖失败、真实工具失败。

下一步：同状态替代解规划、动作图层变异、鲁棒性目标、独立多run和真人试玩。当前不签高质量、Runtime在线生成、正式伤害/交易/存档或手机验收。

发布收据：delivery/PUBLICATION.json；论文/审计和原始数据在REPORT.md及研究包。正式游戏与Map Notes代码未修改；原型独立，编辑器仅单向草图导出。
