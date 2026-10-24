# PCG-DYNAMIC-04：V3 UI 验证原始脚本

这里保存本轮**实际成功运行**的 UI 逐帧验证和手动撞刺脚本。所有 `.gd`、参考帧及候选快照均从原证据位置按字节复制；`manifest.json` 记录原路径、SHA256 和字节数。整理期间没有修改冻结 UI/worker，也没有再次运行引擎。

| 原始脚本 | 实际验证 | 对应结果 |
| --- | --- | --- |
| `ui_replay_v3.gd` | 前 12 个正式动态候选，5154 帧，对照归档原 Motor 位置与 module.clock | `delivery/dynamic-v3/ui-replay-results.json`、`ui-replay.log` |
| `ui_replay_sky_v3.gd` | 5 个带 region_profile 的浮岛候选，2250 帧 | `delivery/dynamic-v3/ui-replay-sky-results.json`、`ui-replay-sky.log` |
| `ui_manual_damage_v3.gd` | 真实 KeyboardMouseAdapter 按 D 撞宿主荆棘；HP5→4、actor epoch1→2、原 SegmentRespawn 回退且机关时钟继续 | `delivery/dynamic-v3/ui-manual-damage-results.json`、`ui-manual-damage.log` |

两组回放合计 17 个候选、7404 帧；最大位置差约 5.0e-12wu，最大时钟差约 5.0e-14s，均为 JSON 数字精度范围。UI 演示与人工趣味性、真机认可分开；这些脚本不代签后两者。

## 依赖和路径约束

- Godot **4.7.2 Standard**，固定物理/演示帧率 60Hz。
- 完整 `prototype/godot` 研究工程及其原 Player、Module、伤害、资源、素材和导入依赖。不要只复制这三个脚本运行。
- 本目录两份 `ui-expected-*.json` 来自实际归档的 `result.frames`，不是输入-only 的 `recorded_frames`。其中动态参考来自 `results/dynamic-search-v3/archive.json`，浮岛参考来自 `results/region-sky-v1/archive.json`。
- `tested-candidates-v3.json` 是前 12 条实际测试输入快照；`tested-sky-candidates-v3.json` 是随后 5 条快照。保留这些输入才能复现原有对照范围；不要用未来追加/修改后的候选列表冒充同一次测试。
- `thorn-real-return.json` 是手动撞刺负例的真实宿主平台/荆棘 Definition 输入。

**原始脚本含绝对路径 `/workspace/pcg-research`，直接执行需要原工作区布局。** 它们读取 `results/dynamic-worker-v1/` 下的参考/夹具，向 `delivery/dynamic-v3/` 的固定文件名写结果。不要直接重跑并覆盖既有证据。下面命令复制独立工程并只对临时脚本做路径替换；本目录原件及已冻结源码保持不动。

## 独立重放命令

以下为复现命令，整理本目录时没有执行这些引擎命令。先取得当前团队的 Godot 独占租约，避免和其他验证/导出并发。以 Bash 在研究仓库根目录运行：

```bash
cd /workspace/pcg-research
pcg_verify_root=$(mktemp -d /tmp/pcg-v3-verification.XXXXXX)
pcg_godot=/workspace/pcg-research/toolchain/Godot_v4.7.2-stable_linux.x86_64
mkdir -p "$pcg_verify_root/prototype" "$pcg_verify_root/results/dynamic-worker-v1" "$pcg_verify_root/delivery/dynamic-v3"
cp -a --reflink=auto prototype/godot "$pcg_verify_root/prototype/godot"
python - "$pcg_verify_root" <<'PY'
from pathlib import Path
import shutil, sys
stage = Path(sys.argv[1])
source = Path('prototype/dynamic/verification')
fixtures = stage / 'results/dynamic-worker-v1'
for name in ['ui_replay_v3.gd', 'ui_replay_sky_v3.gd', 'ui_manual_damage_v3.gd']:
    original = (source / name).read_bytes()
    (fixtures / name).write_bytes(original.replace(b'/workspace/pcg-research', str(stage).encode()))
for name in ['ui-expected-v3.json', 'ui-expected-sky-v3.json', 'thorn-real-return.json']:
    shutil.copy2(source / name, fixtures / name)
shutil.copy2(source / 'tested-candidates-v3.json', stage / 'prototype/godot/modules_v3.json')
PY
```

若源码归档不含 `.godot` 导入/全局类缓存，先在临时工程重新导入：

```bash
"$pcg_godot" --headless --path "$pcg_verify_root/prototype/godot" --editor --quit
```

按原验证范围分开运行；日志和结果均写入临时树，不覆盖归档：

```bash
"$pcg_godot" --headless --path "$pcg_verify_root/prototype/godot" --fixed-fps 60 --script "$pcg_verify_root/results/dynamic-worker-v1/ui_replay_v3.gd" > "$pcg_verify_root/delivery/dynamic-v3/ui-replay.log" 2>&1
cp prototype/dynamic/verification/tested-sky-candidates-v3.json "$pcg_verify_root/prototype/godot/modules_v3.json"
"$pcg_godot" --headless --path "$pcg_verify_root/prototype/godot" --fixed-fps 60 --script "$pcg_verify_root/results/dynamic-worker-v1/ui_replay_sky_v3.gd" > "$pcg_verify_root/delivery/dynamic-v3/ui-replay-sky.log" 2>&1
"$pcg_godot" --headless --path "$pcg_verify_root/prototype/godot" --fixed-fps 60 --script "$pcg_verify_root/results/dynamic-worker-v1/ui_manual_damage_v3.gd" > "$pcg_verify_root/delivery/dynamic-v3/ui-manual-damage.log" 2>&1
```

回放脚本输出逐例 `UI_V3_REPLAY`，应核实 `safe=true`、`stable_frames>=6`、`hp=5`、`contact_frames=0`、`compared` 与输入帧数一致及位置/时钟误差。手动负例输出 `UI_V3_MANUAL_DAMAGE`，应核实 HP4、safe=false、finished=false、真实提交/回退记录、epoch2，以及回退前后时钟相同、随后十帧时钟增加。脚本是观测器，退出码0本身不替代这些字段检查。

旧输入-only 参考导致的第一次校准失败日志保留在 `delivery/dynamic-v3/ui-replay-input-only-reference-failure.log`；本目录保存的是修正后真正用于成功对照的原始脚本，不把失败运行记为通过。
