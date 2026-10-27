# R2 是否能使用现有 Module 拼装

2026-10-24。结论：现有内容可作为主体，但目前尚未完成整图自动装配。不同尺寸是空间求解器应处理的常态；真实多出口、可逆性和运动状态接口是更主要的约束。

本次重新检查 Map Notes 固定快照 `gunman-rush@74d8a06b42cb2bc2c5023f1bfe1a4fbc4b163074`，逐文件校验内容 hash。不能把此快照直接视为最新游戏全部场所接口。

## 实际尺寸与接口

| 内容 | 原始世界尺寸 | 接口 |
| --- | --- | --- |
| `plains_skip_stones` | 580×440 | entry / exit，高度不同；开发试玩 |
| `plains_recoil_span` | 800×740 | entry / exit；已有正式消费者 |
| `plains_fork_rest` | 800×720 | entry / fork_right / fork_up；接入待核实 |
| `forest_exploration_modules__root_meadow` | 880×460 | 森林 factory 的 entry / exit 支撑、requires grapple；未转换为统一运动端口契约 |

不能通过拉伸平台或任意旋转模块使其适配方格：这会改变跳跃、射击反冲、钩索、重力和机关关系。默认保留原始尺寸、内部几何与动作，允许平移；镜像或变形需要单独证明。

R2 的代理图也不能直接放大成世界坐标，或把代理走廊画成真实平台后称为可玩。最终位置必须与模板选择联合求解，以真实边界和净空校验重叠，并让长模块、竖井、枢纽各自获得空间。空的房间内部区域、动作净空、动态危险扫掠范围不能仅由静态平台矩形推断。

## 对 R2 40 份图的新检查

运行已有 `check_real_catalog.py`，只检查“每个图节点对应一个 Resource、每条邻接使用独立端口”的必要数量条件。共 72 份有显式 Resource 端口记录：68 份双端口、3 份三端口、1 份五端口。森林 Dictionary/factory 的完整端口未被这个 Resource 检查器推断，结果不代表森林无可用多出口场所。

- R2 每图有 13–18 个三向及以上邻接节点，最大邻接数为 6。
- 仅用当前已核对正式消费者的 25 份 Resource：40/40 无法直接逐节点替换，因为该池均为双端口。
- 放宽到全部 72 份 Resource，并忽略区域、玩法职责、能力和方向，只看端口数量：36/40 通过；4/40 有六连接节点，超过当前最大五端口。
- 这 **不是 36 张布局/物理通过**。多端口资源的接入仍待核实，同一个端口数足够不证明任意端口对可达、可逆或资源状态兼容。

数据：[real-port-capacity.json](../../experiments/l4-mapgen/results/region-network-v2/real-port-capacity.json)。复现：

```sh
python3 experiments/l4-mapgen/check_real_catalog.py \
  --inventory experiments/l4-mapgen/results/content-inventory.json \
  --runs experiments/l4-mapgen/results/region-network-v2/runs.json \
  --output /tmp/region-network-v2-real-port-capacity.json
```

## 建议的真实内容映射

- **探索节点 → 一个 Macro 场所**：可以由多个现有 Module/Cell 组成，不要求一个图方块对应一个 Module。核心枢纽需要真正的分岔空间。
- **探索连接 → 一段有方向的动作路线**：选择水平跨越、上升、下降或单向回程模块，必要时由已验证连接 Cell 衔接；不能默认正向通行就能反向通行。
- **少量复用/补齐的枢纽 → 保留区域网络**：优先核验现有多出口候选和森林场所。若接口不足，需要连接 Cell 或新的枢纽 Macro；仅串接双端口模块不会凭空产生第三条路线。可将高连接节点展开为同一场所内多个相连枢纽，但需要重新验证，不能悄悄删边或改成线性主干。
- **模板域先参与布局**：读取候选的真实占用、入口出口局部坐标、方向、能力及运动/资源条件，再回溯放置与闭合回环。失败时换候选、移动邻近场所或返回上游职责求解，保留失败原因。

接口最少包括：`occupied/clearance/swept geometry`、`ports(local position, direction, movement/resource requirements)`、`entry→exit transfer evidence`、支持的能力与回程、固定内容版本。具体字段沿用 [统一架构契约](architecture.md)，不再创建一套同义正式格式。

后续最小验证是一个含分岔、异处汇合和奖励回程的真实片区，再扩为整图。先证明异尺寸几何及实际接缝动作，再验证完整路线和真实探索；本次只完成资料与端口容量检查，未新增任何物理通过记录。
