# 失序之钟 PCG 研究原型

最新 **PCG-FACTORY-05**：见 [离线生产与评审报告](FACTORY-REPORT.md)。已运行1002次真实物理测试，按严格regular门槛筛出4个待真人候选、2个返工；人评0、批准0。新增双档案质量搜索、完整源/失败留存、独立留出、网页亲自试玩评分/导出与版本绑定的返工工具。`python3 -m prototype.factory.core.producer --name new-run --tier regular` 为新入口；当前仍是有限注册家族，未签趣味、Runtime或正式游戏准入。

[打开最新试玩与评分](https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/b69a52727616/) · [发布、源码数据和校验回执](PUBLICATION-05.md)。评价只保存在浏览器，需要导出后发回。

最新进展见 [动态机关与区域输入报告](DYNAMIC-REPORT.md) 和 [PCG-DYNAMIC-04发布回执](PUBLICATION-04.md)；前轮见 [能力组合生成报告](COMPOSABLE-REPORT.md)，第一轮论文/架构研究见 [研究报告](REPORT.md)。这是独立研究工作区；没有修改/合并游戏正式源码。

V3已接真实荆棘/移动锯轮/载人平台/伤害回退及结构化区域输入。浮岛16提案有8条连续动作正例，含3条墙跳+二段跳+钩索+反冲混合；弹射蘑菇/孢子气流未实现并明确拒绝。最新手动入口：`Godot --path prototype/godot res://main_v3.tscn`，17个预生成候选；5条有已知退化或低容错，标为诊断REWORK。生成命令、原始数据与成本见新报告；默认旧场景继续保留供历史复现。

推荐现在采用动作驱动核心（A）；只有在动作树变异、容错评价确有收益时升级为混合C。本次不宣称高质量、Runtime或趣味性目标已经完成。

- `research/`：论文、7仓库审计、项目架构与独立审查。
- `prototype/`：可运行Python生成/评价、原Godot真实输入worker、可玩场景、Map Notes导出。
- `results/holdout-v2/`：同域修订对照；V1保留原不公平实现结果。
- `results/deliverables-v2/`：扰动、删动作、连续拼接、奖励位置/出口和稳定末态。
- `delivery/`：真实录像、Web、GUI证据和Map Notes工程。

## 重现

需要Python3.12、Git、Godot4.7.2 Standard（项目指定）、OR-Tools9.15.6755，制图另需matplotlib；不需要Mario/FI源码。`requirements.txt`列本次环境版本。pyribs已研究但本次未调用其优化器。

1. 将游戏固定到 `12f6cb006d7119598e3235f4ca4f7323e4c9d092`，放在 `/workspace/gunman-rush-latest`，或用提取器 `--source` 指定。提取器只按该Git提交读取依赖，不能用后来main替代。
2. `python3 prototype/godot/extract_source.py --source /workspace/gunman-rush-latest` 恢复真实运行依赖；来源hash见 `source_provenance.json` / `asset_licenses_provenance.json`。
3. Godot二进制放在 `toolchain/Godot_v4.7.2-stable_linux.x86_64`。ZIP官方SHA为 `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`。`--headless --editor --path prototype/godot --quit` 导入。
4. `python3 prototype/experiment.py --samples 32 --generations 3 --seed 724030 --name my-run`
5. `python3 prototype/evaluate_deliverables.py my-run my-deliverables`。结果实际绑定本次源码/物理，结果目录请另取名字以保留原件。
6. `Godot --path prototype/godot` 默认操作第二轮20个能力组合候选；第一轮入口用 `Godot --path prototype/godot res://main.tscn`。A/D移动、Space跳跃、左键松开反冲、E或右键松开钩索。Replay提交真实输入，不搬角色。
7. `python3 prototype/mapnotes_export.py` 导出本次固定交付参考；这是单向评审草图，不是编辑器已能回写游戏。

`experiment.py`将每次命令/退出码/墙钟/CPU/峰值写进 `*.execution.json`，保留输入/完整轨迹/失败。超时或错误退出不生成成功报告。工作内存/时间是桌面headless样本，不能作为Web手机保证。

前两轮原型只验证静态危险完整身体扫掠，未接正式荆棘伤害、敌人、奖励交易、保存或动态相位；这段历史限制不应套到已新增真实动态组件的V3。各轮仍未证明最低能力条件和趣味/设备评价；详见对应报告和ADAPTATION。
