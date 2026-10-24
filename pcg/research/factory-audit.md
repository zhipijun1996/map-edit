# 离线 Module Factory 独立审查

审查者 `ability_contract_audit`，实现者为父代理。依据仓库 `level-module-creator` 的独立审查要求及 `gameplay-reviewer` 方法，仅审查源码、冻结数据与纯Python反例，不修改算法、不运行Godot、不把旧V3试玩签成新工厂验证。范围为 `prototype/factory/core/{producer,quality,engine,feedback}.py`、`feedback_cli.py`，以及本轮收紧派生代码与完整运行回执。

## 正式生产与收紧派生：限定范围 ACCEPT

**已验证它能离线搜索、留存失败并筛出供真人评审的技术候选；没有证明批量产出好玩模块或实际真人闭环已完成。** `factory-production-v1` 冻结证据完整，`factory-production-v2` 只在同一批证据上按显式regular门槛收紧，未偷换几何或重挑样本。最终4个待真人、2个返工、人评0、批准0，口径正确。

独立脚本 `evidence/factory-audit/review_production.py` 退出0，`production-review.json` 的 `failures=[]`。审查者逐65批解压并复算，无Godot、浏览器运行；21项当前纯Python测试通过。

| 检查 | 实际结果 |
| --- | --- |
| 运行账本 | 1002物理case、65批、每批≤16；16 motion、648 discovery0、36 discovery1、205 holdout、97 alternatives。82个去重策略，初始提案族预算与总账一致。整体wall136.15秒是这次批次耗时，不是单Module/Runtime时延。 |
| 压缩原件 | 每批gzip SHA、解压后的原字节SHA/长度、输入SHA、case ID、引擎退出与日志均过。完整原输出190,167,051字节，压缩9,890,792字节，失败完整帧可恢复，没有只存成功。 |
| 完整文本运行源 | 658份实际源字节逐SHA匹配，包含feedback_cli；source manifest SHA `02184707e2df0170e651f35b57e6fa9acdafc065f1a97b59cb71506e7d2601d2`进入catalog binding。不是用当前v2扩展版解释旧v1。870受保护原件另核0漂移。 |
| 真实行为与违反量 | 684条discovery compact逐一回到gzip真实帧，实际词、hook抵达、ground连续性、carrier支持、换向/静止描述、完整词违反距离均与存档一致。不是只检查自报标签。 |
| 档案与父子 | 重建全部82次插入、替换与分区历史：6可行cell、6不可行cell；12次可行、13次不可行的“写入/替换”包括首次插入，不能夸大为25次设计改善。冻结变异函数与父代选择可按原字节复现。 |
| 留出隔离 | 六个finalist由discovery档案预选；catalog features仍为discovery结果。205条留出重新复算，180个动态初相位值及扰动seed与独立holdout公式一致，未借holdout重选候选或更新搜索。 |
| 反例门槛 | 97个有界替代策略回放与实际词重新分类，和catalog一致。反冲平台虽留出全过，发现低成本解仍返工；无发现不证明最低能力或动作必要。 |
| 严格v2 | 同6个UID、scenario、描述、calibration、validation、替代见证逐项一致。四个导出case的全部非别名字段与v1完全一致，module SHA及录制输入未变；只改匿名显示别名。没有新物理case。 |

确有一条来自不可行档案的真实修复转移，而非手写标签：

- parent `65e54e607d7d...`（carrier_double）平均违反4.1979467466；子 `19278fdcf137...` 将接收台与goal/出口共同左移32wu，平均违反降至0.0037324230，校准clean4/4、mild4/4目的通过。
- 子代随后在独立holdout获得clean12/12、mild12/12、moderate10/12，满足regular；旧parent失败与另一个更差child均保留。
- 该转移证明有限FI搜索能修复一个实例，不能外推所有不可行设计都能自动修复，也不能把几何左移等价于学到了高级动作设计。

| 最终候选（UID前缀） | clean | mild | moderate | regular结果 |
| --- | --- | --- | --- | --- |
| thorn_wall `393922fb07` | 1/1静态 | 12/12 | 8/12 | 待真人 |
| hook_saw `3f1dfbca0f` | 12/12 | 12/12 | 11/12 | 待真人 |
| hook_saw `738f1a5556` | 12/12 | 12/12 | 9/12 | 待真人 |
| hook_saw `aa132c6ef4` | 12/12 | 9/12 | 6/12 | 返工，未自动降为precision |
| carrier_recoil `2041aacc3d` | 12/12 | 12/12 | 12/12 | 返工，已有低成本替代 |
| carrier_double `19278fdcf1` | 12/12 | 12/12 | 10/12 | 待真人 |

门槛是当前有限样本自动策略的工程政策。Wilson区间已留存，12/12不是100%总体保证；点估计合格也不代表人类容易、专家有趣或长期稳定。普通静态clean只执行1次，正因为没有随机初相位；其噪声仍12次各档。运行只覆盖本轮注册构造族，不能宣称“任意区域/能力组合都可可靠生产”。

## 当前状态

实现前发现3项应修问题，已修并进入冻结production-v1；显式regular门槛随后进入v2派生。初始源与独立反例保留在 `evidence/factory-audit/initial-source/`、`initial-counterexamples.json`。后续源副本在 `post-source/`。早期20项/最终21项纯Python测试均通过，但这些是合成测试，不是真人报告，也不是引擎复跑。

| ID | 独立发现 | 修复与范围 |
| --- | --- | --- |
| FACT-R1 | Engine源快照只glob factory/core，遗漏实际反馈入口feedback_cli.py；catalog原binding没有完整代码manifest hash。 | 当前加入factory/*.py，source_manifest_sha256进入binding并随catalog绑定。旧pilot保留原656源快照，未追签CLI已包含。 |
| FACT-R2 | 约束距离只比较预期词前缀：预期ground_jump，实际ground_jump→air_jump，在安全出口时purpose=false却total=0。 | 改完整编辑距离并增加独立purpose_failure项；不能让错误动作链在FI档案里被当零违反。反例旧输出total=0已留存。 |
| FACT-R3 | excessive_wait反馈用于无saw的carrier时，mutate静默转成接收台位移，仍称targeted child。 | mutate明确拒绝该组合；调用端先记录manual_design_review_required并continue，不误标修复、不终止整轮生产。只有有真实对应参数的目标才进入变异/全验证。 |

一个已完成的门槛调整：初版gate会在regular未达`.85/.65`时自动退到precision_review的`.70/.40`。两者虽均只进人工队列、无自动批准，但不能拿这种事后分档声称regular可靠性通过。production-v1原分类保留；显式requested_tier默认regular，使用同批完整留出数据作**更严格**派生v2，复核通过；不重选幸运候选、不降阈值、不把precision偷偷并入regular。

## 档案是否真的使用行为与不可行搜索

源码具备可审计的有限MAP-Elites基线：cell来自真实执行词、真实横向换向和运动静止比例，未以family名/几何标签当行为；可行与不可行各有独立存储，分别按校准质量和违反距离替换；两区档案都实际供父代选择与变异。它不是只输出一个“QD/FI”标签。

边界也明确：word hash本身会细分cell，但词不同不保证新增玩家判断；描述取“违反最小的单条真实轨迹”，距离取各运行平均，不能说描述代表整个随机分布。frontier/候选族/变异均有限；没有展示真实跨cell替换与不可行→可行转移前，不应把档案格子数称覆盖率或把首次插入当优化成功。实测最终要核对archive_history与实际父子链，不能只看summary数量。

discovery质量由clean/mild目的成功率和静止比例构成，是自动策略校准分数，不是趣味。可行区的clean全过/mild≥.75只是搜索入口；最终仍需独立clean/mild/moderate、样本下限、替代解与人工门槛。自动搜索可偏好少等待，但不能据此推定观察与恢复空间都应删除。

## 留出、可复现与数据保留

源码将discovery seed与holdout seed分开，最终候选先按discovery档案选定，再做一次holdout。holdout不用于后代选择；最终只从已通过门槛者导出见证，不以挑一个幸运clean替代完整成功率。多模块使用共同随机数是明确的比较设计，不能将跨模块rollout当独立玩家样本。

Engine限制batch_size1–24，逐批运行、压缩完整输出，保留gzip hash、解压后原字节hash与长度、case index及执行日志。原始失败帧没有被压成只有summary；只删除本轮刚生成且已打包的重复raw输出。每批前检查被冻结源是否漂移，能阻止中途换实现。

快照的“完整”应称**完整文本运行源**。原870原件还包括PNG/SVG/font/audio；这些受保护索引会检查hash，但原型快照不复制全部二进制。恢复全部内容仍需固定base包/游戏提交、全base SHA及原件清单。引擎也以实际二进制SHA绑定，不把版本字符串当二进制身份。不要把656份文本源误写为包含全部游戏资产的自足包。

## 真人反馈与修复闭环

导入绑定catalog SHA、candidate UID、module SHA；几何/控制/录制输入变化会改变module hash，改标题/匿名别名不会改变。replay不能作为manual attempt，synthetic_test不能进real store，test_only store不能生成真实repair job或批准。导入只积累报告，不生成approval。retain还要求技术门槛、两份不同reviewer_code报告、显式human-confirmed curator与原因；即便retain也只有experimental offline approval，formal_game_ready始终false。

reviewer_code、manual帧数、输入事件与human_self_report都是**未签名客户端声明**，不是身份或真的人类手动玩的证明。代码已标为requires_curator_confirmation；不能让AI替用户确认，也不能把合成自测改成human_self_report充当真人闭环。两份不同code不自动等于两个人，实际确认属于curator职责。

feedback repair_job绑定旧module hash。当前可自动实现“扩大接收台”“缩短saw周期”等有限变异，子代必须完整重验，旧批准不会转移。boring/unneeded_mechanic等没有可验证的自动变异时，保留manual_design_review_required，不声称已解决趣味问题。后续正式证据需展示实际child_uid进入search、产出新轨迹、独立准入结果；仅生成任务JSON或写状态字符串不足以证明任务被消费。

没有真人报告时，human_feedback与approved_offline应维持0。可以验证软件闭环，但真实真人闭环尚未发生；诊断用的合成反馈需隔离为test-only，不能为演示实际repair运行而伪装真人。

## pilot-v1 独立只读核算

`evidence/factory-audit/pilot-review.json`：16批gzip逐个解压的原字节SHA/长度与case ID配对均正确；656份源快照hash全部匹配。165次物理case，54个稳定出口计数只是全阶段原始结果，不是54个产品模块。3个holdout候选全部rework，待真人模块0、批准0；其中pilot只有4次validation，最终政策仍要求至少12次，未为演示放宽样本门槛。

20项当前纯Python测试退出0，包括额外动作违反、陈旧catalog/module、布尔评分、replay/合成隔离、去重与不自动批准等。该轮pilot没有迭代轮，不能用其3个可行/4个不可行cell证明已经发生FI改进；正式production数据另验。旧pilot的文本源遗漏与前缀距离问题保留为历史诊断，不覆盖原件。

## 未验范围

正式production、requested-tier收紧派生与真实FI转移数据已复核。实际真人反馈驱动repair任务尚未发生，不伪造生产反馈；新UI自动化证据与合成诊断消费见下节增量复核。没有签正式随机池、Macro/Map资源连续性、区域美术、设备、趣味或长期批量质量。技术合格子集也应称awaiting_human_review，不能把“已能生产评审候选”写成“已证明大批好玩模块”。

## 最终网页与合成闭环增量复核

**限定软件/回执范围 ACCEPT，未发现阻断发布的人评污染或现有包绑定问题。** 本次不重复65批物理，只读 `build_review.py`、`main_factory.gd`、网页源、发布包、浏览器回执及一个已有诊断物理原件。`evidence/factory-audit/review_incremental.py` 退出0，回执 `incremental-review.json` 的 `failures=[]`。

- 网页catalog只在严格v2技术catalog上增加presentation_binding与原技术catalog SHA，技术候选/统计没有改变。实际PCK SHA为 `b69a52727616d877b776baf808cfac5ed604b51e8d3ca9d44421e9a42d39d315`；7份镜头/网页源hash、实际部署HTML/JS/CSS及PCK中四个case JSON manifest均匹配。反馈应使用 **`delivery/factory-v1/web-release/catalog.json`** 导入，不能拿技术catalog替代新的网页catalog。
- `browser-release/browser.json`确记录5次真实输入回放，覆盖4个不同模块（0号重复一次），全部无伤稳定；普通加载及只看Replay不能开启评价。自动化实际按D导致HP5→4并按真实政策返回，形成manual输入记录；没有把这位自动化测试者称为人类玩家。合成模式导出、重新载入草稿与错误检查通过。
- 最新网页catalog SHA绑定到导出反馈及诊断job/store。正常导入明确拒绝synthetic_test；test-only store默认不能驱动真实repair，且即使传human_confirmed也不能批准。诊断入口必须显式diagnostic/test_only，生产入口继续拒绝这种job；真实反馈/批准数仍为0。
- `factory-feedback-loop-test-v2`实际消费1个“落点难读”合成任务，接收平台左扩16wu、总宽增32wu，生成新child并真实运行一次。gzip原字节/输入/执行记录一致，实际目的词、无中途落地、HP5且无接触均通过；没有写生产catalog或review_cases。**1/1是诊断程序闭环成功，不是12次留出技术准入，不证明落点已被人读懂，也不是一次真人反馈闭环。**

本增量认可已有自动化回执与绑定，不冒充审查者亲自运行浏览器、观看画面或听取真人评价。匿名先评界面和回收/返工通道现已可用；实际真人参与、人工curator决定、视觉/手感与设备认可继续未验。
