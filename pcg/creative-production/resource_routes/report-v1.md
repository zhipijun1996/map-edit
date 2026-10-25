# Resource routes — 四个局部玩法关系候选

真实创作来源：`llm_subagent_proposal`，任务 `/root/resource_routes_creator`。全部由同一原 production_loop / WorkshopEngine / regular 门槛生产。不是在线模型服务；趣味、人类试玩与正式生产批准均未取得。

| 关系 | 玩家核心选择 | 留出 clean/mild/moderate | 同几何反例 |
|---|---|---|---|
| sightline-backtrack | 先远离左侧出口，穿低道绕过高挡视石取得高铃射界，再沿原道折返穿永久左门。 | 1/1/12/12/12/12 | 31，同核心安全替代1 |
| trapdoor-commit | 走到横门承重桥上取得高铃射界；开铃即撤去自身支撑，承诺下落领取。允许空中开桥等合理替代。 | 1/1/12/12/12/12 | 30，同核心安全替代3 |
| ordered-target-transaction | 两个编号目标入口共同可见可命中；同两次命中顺序交换会改变真实最终门状态，部分进度持久。允许地面先预开与误序后补射。 | 1/1/12/12/10/12 | 35，同核心安全替代5 |
| moving-ray-window | 人物不碰/乘运动板；预测出射投射物抵达时挡板的位置，择时命中后方铃。允许其他相位和飞行时机。 | 12/12/12/12/10/12 | 43，同核心安全替代11 |

标准 JSON/SVG、精确版本、原 review_cases、私有原 CandidateLibrary 与原证据路径见 [统一manifest](../../results/workshop-creative-resource-routes-delivery-v1/manifest.json)。4次跨进程磁盘查询全部精确命中；全部自有实验1112 cases / 121批的原始解压字节SHA和13762份冻结源字节已核验，见同目录audit.json。

失败保留：低挡视石允许提前跳起射铃，故v5探身样品拒绝；v4返回跳跃不稳而拒绝；初版有序登台承接面过高导致regular失败；原drop-v6虽通过regular，追加21条射线反例发现早枪绕过后已撤回，v7修订只作适配不计新家族。旧空间串联双铃也只作适配，不计新家族。

所有反方向、通用进入/离开状态、变换、拼装、接缝和整图仍为UNKNOWN。原资源恢复未改。导出显式包含第二接收器、原顺序门/无面积顺序门区别；没有复制运动、伤害或投射物物理。

原命令与原日志路径保存在各批 execution.json/source_binding.json；源的每次修订均为新版本，不编辑正在运行的冻结源。最终生产入口为 recipes-v6.py（仅第一项）、recipes-v5.py（仅桥项）、ordered-target-v2.py、moving-ray-v1.py。
