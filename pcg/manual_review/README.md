> 最新实现：累计 62/63 项技术通过，196 设计合同冲突；新增三项可玩包、四条录像及废弃删除回执见 [review-031-v1](../../feedback/manual-review/implementation-results/review-031-v1/README.md)。

> 最新前 30 项实现与废弃删除交付见 [first-30-v2](../../feedback/manual-review/implementation-results/first-30-v2/README.md)。下文保留旧反馈 001 的历史状态。

# 首批人工审批修订

本轮只执行 `feedback/manual-review/batch-001/human-feedback-001.json` 的五项反馈。正式 `modules/`、其版本、认证与索引保持原样；新版是待复审、未完整认证的隔离候选。

| 审阅编号 | 旧尺寸 → 新尺寸（Block） | 修订 | 当前实测范围 |
|---|---|---|---|
| 01 | 10×9 → 10×6 | 裁底3行；中庭上方增加原生俯冲怪 | 四条原路线、端口试件、有限反例首轮通过 |
| 02 | 12×11 → 12×6 | 删除底部5个平台、裁底5行；最高台增加哨兵 | 双向首轮通过；去程越过哨兵落在另一侧，允许合理替代解 |
| 03 | 11×6 → 6×4 | 左1格、空隙4格、右1格；裁底2行；增加空中/陆上怪各1 | 低路通过；高奖励路线仍待修，未入正式库 |
| 04 | 8×8 → 8×5 | 保留核心，删底台、裁底2行与顶部1行 | 两条原路线、端口试件、有限反例首轮通过 |
| 05 | 8×8 → 6×5 | 裁底3行及左2列；A口与真实支撑移到新左边界 | 原路线、端口试件、有限反例首轮通过 |

所有端口仍在128像素Block外边中心；削薄/删除真实岩体，重新编号支撑，不只移动标记。新敌人复用真实 EnemyActor / EnemyAttackBehavior / 接触伤害 / 命中回充。俯冲资源从本地游戏参考原样复制，来源SHA及VCS缺口见 `runtime/diver-provenance.json`；不改正式游戏、原共享plains_cells或物理模拟。

03的固定80控制搜索周期失败后完整保留。第二稿曾取奖并稳定抵达，但完整身体上越界24.8px；第三稿移开出口站位上的陆上怪，去掉多余到岸上冲，仍在守岸怪前受伤。第三稿低出口可达；不把native可加载、旧稿抵达、设计修改或截图当作新高路认证。初始仍仅一发空中射击，当前低路实际通过命中怪物回充继续反冲，不再声称单枪跨越。

校准、独立留出、通用接缝、镜像/换边组合、人工试玩与新版生产认可均未进行。04的“保留”记录为旧版玩法认可并附裁剪请求，不自动继承到新版。

## 审阅与重建

固定网页：`generation/manual-review/?batch=batch-001`。原话、原尺寸/旧图、修订稿和待修项同时保留；意见按新源SHA重新待审。统一队列仍225项/45批，不新增模板计数。

```sh
python3 pcg/tools/restore_archive.py manual-review-batch001-feedback001-v1 --verify-parts-only
python3 pcg/tools/restore_archive.py manual-review-batch001-feedback001-v1 --extract
python3 -m pcg.manual_review.publish_batch001
node tools/build_manual_review.mjs
```

归档包含全部新旧候选、失败、冻结输入、完整压缩raw、真实执行命令、原生包与源码快照，按SHA去重并逐条核验19525项；没有删除工作区原件。最终四个通过首轮的原生包在 `batch-001/revision-002/<module-id>/playable-final/`。03待修包在 `batch-001/revision-003/b31-n12-three-side-port-interface0/playable-final/`，高路原生回放失败保留。

例如启动01原生可玩草稿（需要已安装仓库的原Godot项目资源）：

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --path pcg/prototype/godot "$PWD/pcg/manual_review/batch-001/revision-002/b31-n06-fourport-two-low-ingress/playable-final/demo.tscn"
```

A/D移动、空格跳跃、鼠标射击；`-- --replay --case 0` 可按各原生包支持的冻结输入回放。原生校验使用既有 `godot_package.run_package_validation`，不另建Harness。

`revise_batch001.py`、`refine_batch001.py`、`finalize_batch001.py` 和 `refine_reward_guard.py` 是本次版本化修订记录，已有输出时拒绝覆盖；它们不是恢复其他批处理的授权。已完成内容重新审阅后，再决定目标修复或下批，不自动生成新模块。
