# 静态准备失败

这三次没有调用 Godot，不计入 1713 个 Harness 输入。失败输入原样保留，随后只补齐已有 schema 必需的展示/接缝字段：

- `01-missing-route-duration/`：新增设计路线缺少现有编辑器要求的正数 `duration`，报“运动时间无效”。
- `01-invalid-animation-mode/`：首个默认展示 `mode=walk` 不在既有枚举，报“运动模式无效”；改用已有 `once`，不改物理。
- `01-missing-seam-mapping/`：新接缝元数据缺少 `portId/allowedOverlap`，报 `Module contract: port seam mapping`。

之后五项均通过原合同校验；这些失败稿不参与可玩包或技术结果。
