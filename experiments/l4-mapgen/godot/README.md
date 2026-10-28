# 真实游戏生成基准（外部只读脚本）

`baseline_export.gd` 在现有游戏项目的 Godot 上下文调用原生成器，但脚本和输出都属于 Map Notes/map-edit。不修改正式游戏源码、生成器、数值、模块或准入规则。它只证明实际数据生成和回放验证，不装配场景，不证明物理可玩或趣味性。

## 已执行

- 游戏来源：`integration/four-lines-20261023@f50fe78630fd98339186349f4ea91d92540d6c5b`。
- 引擎：Godot `4.7.2.stable.official.ed1daf0bf`，Linux x86_64；无预热，按profile、map、seed顺序串行。
- `l4-baseline-00..09`，两图，三profile，60次完整 public generate。每次另做 public validate 和 JSON serialize→parse→validate。
- `../results/baseline/report.json`：原始每次参数、版本、hash、计时、内存计数及通过状态；`summary.json` 是同一数据的统计摘要。
- 6份未改写原始manifest：每profile两图seed00；其余54张保留hash/结构数量/性能，不保存整份几何。
- `../results/baseline-native.log`：实际引擎输出，最终标记 `PASS / 60 rows / 0 failures`，退出码0；所列源文件前后hash一致，游戏 tracked 工作区未改变。

## 复现

先使用游戏本来的工具链完成一次干净资源导入。外部脚本依赖该项目的全局class缓存和真实资源；不独立复制生成器。以下示例输出目录必须尚不存在。

```bash
/workspace/toolchains/godot/4.7.2/Godot_v4.7.2-stable_linux.x86_64 \
  --headless --path /workspace/gunman-rush-l4 --check-only \
  --script /workspace/map-edit/experiments/l4-mapgen/godot/baseline_export.gd

/workspace/toolchains/godot/4.7.2/Godot_v4.7.2-stable_linux.x86_64 \
  --headless --path /workspace/gunman-rush-l4 \
  --script /workspace/map-edit/experiments/l4-mapgen/godot/baseline_export.gd -- \
  --output-dir=/workspace/map-edit/experiments/l4-mapgen/results/baseline-rerun \
  --seed-count=10 --seed-prefix=l4-baseline \
  --source-commit=f50fe78630fd98339186349f4ea91d92540d6c5b
```

可选 `--profiles=plains,forest_v15,forest_v18`、`--maps=1,2`；限定1..100 seeds。禁止输出到游戏目录或覆盖已有实验。日志自行重定向至 map-edit 实验结果目录。

## API与实际参数

| Profile | 实际public调用 | 与App对齐的选择 |
| --- | --- | --- |
| plains | `PlainsRegionGenerator.generate(seed,tuning,false,"",difficulty)` | `root_bell_mode`按V3/V2的`PRODUCTION_ADMITTED`选择；此来源为v3，结果版本`plains-region-v12-root-bell-spaces`。map1 intro、map2 advanced，使用`PlainsRegionCampaign.seed_for`。直接使用生成器默认值会误测历史v10。 |
| forest_v15 | `ThornForestRegionGenerator.generate(seed,tuning,map_index,snapshot)` | 显式`forest-bible-world-v15`，当前普通入口默认；`grapple:true`、abilities仅H、pulse_gun、空items，拒绝假设墙跳/二段跳/武器演化。 |
| forest_v18 | 同上 | 显式`forest-exploration-places-v18`，开发候选，`production_pool:false`；能力与v15一致。 |

`tuning`由游戏`PlayerTuning.load_default()`读取，不重复物理常量。森林seed使用原`ThornForestRegionGenerator.seed_for`。完整参数写入每一条row。

## 计时含义与限制

- `generate_ms`含原generate内部全部验证、重建/回退，未绕开到`_candidate()`。
- `validate_ms`是返回后再调一次原public validate；不加入generate统计。JSON编码与roundtrip validate单独记录。
- 首行可能含惰性资源加载。p95为20个样本的nearest-rank第19项；这里只是一次进程的配对seed样本，不是跨硬件性能估计。
- `MEMORY_STATIC`/`MEMORY_STATIC_MAX`是Godot进程内计数；不等于单图RSS、泄漏或Web峰值内存。
- canonical hash/回放通过不能推出无Softlock。报告明确`physics_status:not_run`、`human_playtest_status:not_run`。

## 复用既有真实森林Motor验证

最小原有Python入口（单Seed/单图/单路线，非80案例）：

```bash
cd /workspace/gunman-rush-l4
python3 tools/run_forest_depth_region.py \
  --output build/l4-baseline-motor/fresh \
  --seed forest-depth-hollow-00 --map 1 --route fast \
  --layout forest-bible-world-v15
```

若所有产物都要留在map-edit，可直接调用原始runner，输出绝对路径；随后必须用原`run_forest_depth_region.py`验证函数做离线验证，不能仅凭进程exit0称原Python门禁通过：

```bash
/workspace/toolchains/godot/4.7.2/Godot_v4.7.2-stable_linux.x86_64 \
  --headless --fixed-fps 60 --path /workspace/gunman-rush-l4 \
  --script tests/forest_depth_region_runner.gd -- \
  --seed=forest-depth-hollow-00 --map=1 --route=fast \
  --layout=forest-bible-world-v15 \
  --output=/workspace/map-edit/experiments/l4-mapgen/results/motor-fresh/trace.json
```

runner实际使用DemoApp、Router和PlayerMotor、无中途位置/资源注入，但输出scope明确排除Boss战。外部脚本的本轮生成性能实验没有运行上述Motor命令；实际是否执行由单独日志和receipt证明。
