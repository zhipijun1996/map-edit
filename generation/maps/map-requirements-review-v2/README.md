# Map需求重新核对与固定骨架退役

[完整要求、架构与后续里程碑](../../../docs/l4-mapgen/map-requirements-reset-v1.md)。

旧43实例图在设计审核中被拒绝。三个预先固定Seed仅输出42/43/41逻辑槽位、3/2/3主路和各6条三类支路；没有空间物化或Godot执行，没有新影片。通用Graph物化尚待实现，工坊needs_design保留为缺口，不计补缺成功。

五段骨架/旧小图生成和相应选型、路线、录像入口已经删除，无legacy回退；67个旧Map上下文版本标记退役，94个原Module父版不受影响。

summary.json为审计范围，previous-map-design-review.json为旧图反例，plan-*/保存全部逻辑输入/输出/缺口/哈希，source_snapshot/保存本轮实际审核源。checks.json是静态/逻辑检查结果，不能当作物理或趣味证明。
