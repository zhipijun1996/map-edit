# 原游戏森林来源的输入绑定迁移（v9–v11）

本轮处理已登记的35个森林来源，不新增玩法。分类与精确输入位置见
`pcg/migration/foundation-v1/original-forest35-taxonomy-v9.json`；原游戏代码固定
`879b39eaa869be70cb799dedd1bb6ffc35e0b92f`，真实物理基线仍为12f6cb，二者不重标。

## 原程序的不同语义

- v9保留原H/R目标顺序与真实Coin/Note消费者，补齐接近路线、`approach_steps`、`action_start`、`departure`、原路线后缀和Directional命名输入驱动。普通主线允许无H的来源，H见证只描述该见证，不表示所有合法路线都必须H。
- v10翻译Hollow原司机的上窗H/R、floorless H0R、两个洞内落脚点及走落后的侧钩。原树干、危险、钩点和资源未重新设计。固定源司机及SHA见 `original-forest-drivers-v10.json`。
- v11修正两个新增观察触发器的DSL接线：必须有`state=free`，原Harness才调用`condition_met`。v9/v10当时的实际失败raw原样保留；不修改已冻结作者。第二次H还检查完整身体已离开原bay，外沿下落H检查真实空中位置。没有给角色写位置、速度或资源。
- 二选一区域奖励、挂钩释放及未绑定命名司机继续作为具体实现缺口，不标为物理不可行。金币/音符二选一不能转换成两个独立拾取物。源内奖励台、失误点和回归点不天然等于外边Port。

## 固定实验与复现

以下入口只在新的输出目录运行；旧输出与真实失败不覆盖。先clean筛查，`physics.run_clean`检查核心、所有外口、连续进入/离开及廉价反例；正式FULL前调用`holdout_guard.check`。

```sh
python3 -m pcg.migration.forest_feedback_v9 --out .cache/migration/forest-feedback-v9-new --name forest-source-policy-v9-new
python3 -m pcg.migration.forest_hollow_v10 --out .cache/migration/forest-hollow-v10-new --name forest-hollow-v10-new
python3 -m pcg.migration.forest_departure_v11 --out .cache/migration/forest-departure-v11-new --name forest-departure-v11-new
python3 -m unittest pcg.migration.tests.test_forest_source_bindings pcg.migration.tests.test_forest_departure_dispatch -v
```

这些命令不自动重新获得独立留出资格；同原来源的已观测条件仍锁定。首个clean通过策略固定后才校准；仅校准失败且未看留出时使用预登记的第二个源司机策略，每源最多两次修订，不降低原门槛。新文件名不重置预算。

## 已保存证据

- `original-forest-v9-preflight-v1.json`、`original-forest-v9-full-v1.json`、`original-forest-v9-directional-full-v1.json`及`original-forest-v9-packages-v1.json`：窗口、树冠绕路、Directional窄口完成正式物理与原生包。较长Directional保持原校准失败。
- `original-forest-v10-preflight-v1.json`、`original-forest-v10-full-v1.json`及`original-forest-v10-packages-v1.json`：deep/shallow/aircatch/upper四源；`original-forest-v10-standing-full-v1.json`与对应package清单保留两个洞内来源的原standing-H校准修订与独立留出。跳起版失败也保留。
- `original-forest-v11-elbow-standing-full-v1.json`及`original-forest-v11-packages-v1.json`：洞内转角完整身体走落后出钩的真实证据；最初未接线、修正后跳起策略的失败另存。

`forest_hollow_trunk_geometry__cavity`与`forest_hollow_upper_candidate__build_cavity`的原`data`逐字段完全相等，是明确去重候选；两个来源的实验不能计为两个不同玩法。正式代表项、alias与回收由统一迁移事务处理。技术合格与人工观感认可分开。
