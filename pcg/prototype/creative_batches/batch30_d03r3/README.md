# D03 r3：真实射距与身体净空修复，仍有未通过路线

旧两轮full失败原件不变。新周期根protocol-v8批准2rule/120probe/1600full，校准261032001/留出261032002。此处实际只运行120probe，未运行任何新完整calibration/holdout，未入库，API目前**不可直接full或交付**。

原角度问题：敌人28×32，弹丸半径3、速度1200，第二枪距293–332导致实际角半窗仅4.11–4.59°，6°扰动产生31–35px偏移。不是冷却/随机seed问题。原0.25秒冷却要求至少15tick，名义18已保留。

新真实薄浮石[111,366,28,8]承托同一个3HP原sentry center[125,350]。west从80、east先真实地面走穿到170再起跳；首枪前已设朝enemy轴，反冲154px结束后直接回靠，第二枪独立18tick。干净实际第二muzzle183.55/183.82px，角半窗6.86/6.89°；静态角窗仅诊断，真实Godot仍独立验证。westbank右沿扩80，top/portC不变；第三枪.4水平分量。v2清洁两接口7路全通过，air moderate15/24、mild14/16；相同空间下西staged8/8保留HP。

**仍失败，不能由air结果替代全Module验收**：新perch让原main/eaststaged在输入扰动时跳入enemy身体，main moderate4/8，eaststaged2/8。staged另外2次普通首枪意外伤敌，目的要求保HP而被拒绝。更横向射击只修了clean，没有修扰动。i1eastair mild另一次第三枪提前进入高岸底角，head35.075卡在真实bankbottom35，不是可忽略观感。

120个预算已用完，2规则版本已用完。下一需root先登记：main/eaststaged从A地面走到170后再跳，staged恢复原-.6/.8使弹道远离enemy；east第三枪纯下射、名义18，必要时bank左侧切32..40而top/portB/right不动。没有私开第三规则或重复留出。

新增counter_recipes_v1按28个/精确路线输出：10普通直达、3省关键枪、15新perch/真实3HP清除/一hit后ground策略。17个此类probe已经真实运行。活敌占整块顶，不伤害落脚未成；实际3地枪清敌后踩到perch、获得原真实ground资源，但未用两跳直接得高奖。3地枪清敌后走原staged成功，是支付更多射击的合理替代，不能按没复现air按键判反例推翻。

剩1HP对照现在明确真实回到相同canonical x80再分支：两接口westair未得西奖但落底部安全，weststaged均得两宝且敌仍1HP。全世界未重建/传送/资源改写。receipt-v1给compact摘要与每份原engine压缩raw引用，不复制整段frames。


统计纠正：之前给根的进度消息误读了截断输出的首尾成功行，曾误报24/24与15/16。已逐条compact JSON及原gzip核对，实际moderate：i0east3/6、i1east4/6、两侧west各4/6，共15/24；mild两接口east各3/4、west各4/4，共14/16。前两次air hit在24moderate都发生，不能替代真正领奖/稳定到达。没有入库或完整留出以错误数字通过。

只读发现更多细节：首枪噪声下body329而enemy350，反冲过于水平，两次命中后第三枪source已经172，154px最后反冲不够高岸；另有在岸底撞头的独立问题。下一提案是原apex状态反馈起枪：jump→零轴6→jump_release(after10,state=apex)→shoot0，使源body约270..278；Y330/350域仍原授权，但新规则/预算需根先登记。此处没有增加run。
