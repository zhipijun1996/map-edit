# 既有生成候选新地基迁移盘点 v1

只读审计日期：2026-10-27。规范依据：根目录 `MAP_FOUNDATION.md` / `MAP_GENERATION_GUIDE.md`。本次 0 新物理、0 旧记录修改、0 新地基认证。逐版本完整路径、哈希、端口、输入输出与缺口见同目录 JSON。

## 数量与状态

- `candidate_versions`: `134`
- `technical_statuses`: `{"passed_scoped": 79, "passed_scoped_multi_route": 55}`
- `technical_withdrawn`: `0`
- `human_design_holds`: `4`
- `model_design_holds`: `2`
- `block_contract_versions`: `26`
- `declared_dimensions_128_multiple`: `26`
- `all_ports_on_full_declared_rectangle`: `10`
- `complete_old_block_masks`: `10`
- `all_ports_source_candidate_ROCK`: `122`
- `versions_with_all_original_clean_input_output_files`: `134`
- `old_evidence_hash_mismatch_references`: `46`
- `old_evidence_missing_references`: `0`
- `foundation_certifications`: `0`
- `base_template_count`: `"UNKNOWN_PENDING_PORT_STATE_MIRROR_AUDIT"`

134 是版本数，26 是旧 Block 合同版本数，均不是基模板数。人工暂扣、模型暂扣、技术撤回独立保存；旧技术通过没有被重标为新地基通过。

## 矩形、端口和状态判据

对每份原声明 `space.bounds` 检查正整数 Block 尺寸，并独立检查各口是否在完整矩形外边的 Block 中心。凹 owned mask 的内凹边不算矩形外边。另给出已知初始 Cell/环境包络的紧 bbox 及零相位 Block 包络，后者仅为诊断：允许保留更大的原完整矩形，不强制缩框。动态角色/敌人/弹丸运动不拿来扩大静态 Module 占地。

旧 support 能提出 ROCK/ONE_WAY_PLATFORM 候选判据，但不能据此认证。初始 INPUT/OUTPUT/INOUT 全部要求明确来源，不能从 planned route、entry/exit 或机关打开后的观察倒推。旧有限反例和旧 relations 不能覆盖全部真实有向关系；AA、未用口物理封闭组合、封闭后活动路线仍需新版本证据。

## 推荐顺序：保几何试迁

|顺序|家族 / 版本前缀|理由|旧矩形静态检查|
|---|---|---|---|
|P1|wall-projection-unlock / `87731645f7be`|最小两口与永久铃门：完整8×8矩形，先解决初始权限/ROCK与单向关系，几何暂不动。|128尺寸=True；外边中心=True；实体在内=True|
|P2|cross-shaft-direction-fork / `21fc69bcbdcc`|三口互斥门：完整8×8矩形，检验分叉有向关系、未用口封闭及双门初态。|128尺寸=True；外边中心=True；实体在内=True|
|P3|timed-gate-return-catch / `87b8ed50f5b8`|四口同门回落接力：完整10×8矩形，已有四向真实见证与连续接缝附证，适合多入口迁移。|128尺寸=True；外边中心=True；实体在内=True|
|P4|pass-receiver-turn-fork / `88c75d0f8e7a`|三口反身击铃：完整8×8矩形、两个timed门，检验计时机关/分支关系及封口互不干扰。|128尺寸=True；外边中心=True；实体在内=True|
|P5|folded-reward-upper-out-lower-back / `1685840df001`|折页回廊：保留取奖事务与50例同世界A→B→A证据，试迁AA而不从fresh双向推导。|128尺寸=True；外边中心=True；实体在内=True|
|P6|central-two-wing-bridge-choice / `9450553d8135`|三口静桥选择：原paired Cell与真实M落地分流，检验桥状态及不同出口权限。|128尺寸=True；外边中心=True；实体在内=True|

每个 pilot 的精确 `case(s).json`、原 Godot `.input.json` / `.output.json.gz`、原 scene 与存在性/哈希保存在 JSON `recommended_pilots`。建议先 P1 锁定元数据与认证流程，再 P2/P3 测多口；P5 专门测同世界 AA。上述推荐尚未执行迁移，也没有补封口或新增权限。

## 复用与风险

严格旧 geometry+奖励字段重复组 0；平移归一初始静态 Cell 多重集重复组 1；水平精确静态镜像线索 0 对。它们不证明端口 ID、方向权限、机制、初态、控制、资源、奖励和全路线等价，不合并、不删候选。按 family 分组也只是检索线索。

平台重叠、包含和冗长只标 potential。必须审查 hazard host、latch、support、port、恢复、合法替代与未见进入方式后再决定；不因 nominal 未踩就删。

当前134目录与历史6份撤回通知的12个版本无交集；完整通知版本与哈希仍收录 JSON，不能据此宣称历史无撤回。46处历史导出引用哈希差异集中于当前 `module-contract.js` 与 `module-contract-render.js` 两个共享文件，并非46份物理raw损坏。

另有两份 underledge-brake-return 明写 `mirror=False/True`，本审计未确认完整静态 Cell 精确反射一致，保留为意图谱系线索，不合模板。

原证据路径不存在时标缺档，不能冒充可重放；历史绑定哈希与当前源码哈希不同时保留差异，不自动否定当时历史记录或改写它。catalog play/replay 命令仅提供入口，本盘点没有运行。现 88 个版本通过现有 catalog 的只读哈希/身份预检，90 个版本找到绑定的现存原生scene；其他版本的原物理输入输出仍齐全，但原手玩入口缺绑定，明确记缺口。多向入口已给逐route命令，回放使用 `--play VERSION --route ROUTE --replay`。全部307个端口的初始权限仍UNKNOWN；ROCK/ONEWAY仅为source-derived候选，不是新认证。

## 暂停且未入库

N21、N25 按各自 checkpoint 原样绑定，均为暂停原型，不计 Module；N25 Cell 校准不等于 Module 已成立。

## 134 版本索引

|版本前缀|family|旧技术状态|Block|尺寸128|全矩形端口|撤回 / 人工扣 / 模型扣|
|---|---|---|---|---|---|---|
|`01c1569a6399`|landing-reload-relay|passed_scoped|False|False|False|False / False / False|
|`027935f4f6f8`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`028d294a4d39`|park-for-return-repaired|passed_scoped_multi_route|False|False|False|False / False / False|
|`04a93aeaf9d4`|gate-brake-return|passed_scoped_multi_route|False|False|False|False / False / False|
|`08aed42071a3`|bell_lift|passed_scoped|False|False|False|False / False / False|
|`0bdf37eeca23`|under-column-escape|passed_scoped|False|False|False|False / False / False|
|`0c9656cb57d1`|timed-cache|passed_scoped_multi_route|False|False|False|False / False / False|
|`0e52e3732ffb`|enemy-clear-sightline|passed_scoped|False|False|False|False / False / False|
|`106e4362c838`|one-shot-two-routes|passed_scoped_multi_route|False|False|False|False / False / False|
|`115f754a1ce9`|woven-bridge-interchange|passed_scoped_multi_route|False|False|False|False / True / False|
|`11c4b82f4c8c`|step-off-wall-return|passed_scoped|False|False|False|False / False / False|
|`1215efd08c9e`|grapple-bounce-brake|passed_scoped|False|False|False|False / False / False|
|`12ca61f568f3`|low-ray-recoil-return|passed_scoped|False|False|False|False / False / False|
|`167dcb6ec336`|gate-brake-return|passed_scoped_multi_route|False|False|False|False / False / False|
|`1685840df001`|folded-reward-upper-out-lower-back|passed_scoped_multi_route|True|True|True|False / False / False|
|`16ac1de2691c`|air-refund|passed_scoped|False|False|False|False / False / False|
|`1b61e4024681`|block128-underledge-brake-return|passed_scoped_multi_route|True|True|False|False / False / False|
|`1e2a5ff03ebb`|air-refund|passed_scoped_multi_route|False|False|False|False / False / False|
|`21029b907d05`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`21fc69bcbdcc`|cross-shaft-direction-fork|passed_scoped_multi_route|True|True|True|False / False / False|
|`23510fdcf52d`|carrier-dual-service|passed_scoped|False|False|False|False / False / False|
|`24f33e573c24`|block128-retained-shot-recovery|passed_scoped_multi_route|True|True|True|False / False / False|
|`26544bbf5c94`|chase-landing|passed_scoped|False|False|False|False / False / False|
|`2a1efc95dcbb`|thorn-slot|passed_scoped|False|False|False|False / False / False|
|`2c5246ef3fbb`|enemy-sensor-hold|passed_scoped|False|False|False|False / False / False|
|`2cd4444ee767`|block128-human-A1-bidirectional|passed_scoped_multi_route|True|True|False|False / False / False|
|`2e69026fb65a`|enemy-clear-sightline|passed_scoped|False|False|False|False / False / False|
|`30216efd77d3`|brake-under-ledge|passed_scoped_multi_route|False|False|False|False / False / False|
|`30f7380fbf66`|block128-serial-airlock|passed_scoped_multi_route|True|True|False|False / False / False|
|`331f331fdce3`|carrier-rendezvous|passed_scoped|False|False|False|False / False / False|
|`33a31084073e`|moving-ray-window|passed_scoped|False|False|False|False / False / False|
|`35a76f5584c9`|ordered-target-transaction|passed_scoped|False|False|False|False / False / False|
|`383496cb92cb`|block128-bell-carrier-catch|passed_scoped_multi_route|True|True|False|False / False / False|
|`3adef88ab9ff`|windgap-junction|passed_scoped_multi_route|False|False|False|False / True / False|
|`3b5ea33ef146`|bell-carrier-catch|passed_scoped_multi_route|False|False|False|False / False / False|
|`3c09d08f5a13`|paired-support-transfer|passed_scoped_multi_route|True|True|False|False / False / False|
|`3c1c61652792`|air-refund|passed_scoped|False|False|False|False / False / False|
|`3db49838ae45`|grapple-hazard-window|passed_scoped|False|False|False|False / False / False|
|`40dce915d0c5`|serial-airlock-recoil|passed_scoped_multi_route|False|False|False|False / False / False|
|`416535f94907`|refill-short-gate|passed_scoped|False|False|False|False / False / False|
|`46296acaa278`|enemy-displace-landing|passed_scoped|False|False|False|False / False / False|
|`46e54910a60c`|brake-gate-catch|passed_scoped|False|False|False|False / False / False|
|`47a74c8bf948`|enemy-attack-relay|passed_scoped|False|False|False|False / False / False|
|`490a5f1478c3`|timed-cache|passed_scoped|False|False|False|False / False / False|
|`4aa99b6f4b96`|air-refund|passed_scoped|False|False|False|False / False / False|
|`577021d1f4e0`|sightline-backtrack|passed_scoped|False|False|False|False / False / False|
|`5ab81cab175d`|bell-carrier-catch|passed_scoped_multi_route|False|False|False|False / False / False|
|`5afb538da580`|block128-human-A3-bidirectional|passed_scoped_multi_route|True|True|False|False / False / False|
|`5d5af8cc8720`|prepared-air-sequence|passed_scoped|False|False|False|False / False / False|
|`6043706fd951`|paired-support-transfer|passed_scoped_multi_route|True|True|False|False / False / False|
|`610b9bbe8efe`|enemy-sensor-hold|passed_scoped|False|False|False|False / False / False|
|`615eeddd3116`|brake-gate-catch|passed_scoped|False|False|False|False / False / False|
|`619301668382`|block128-active-chase-bidirectional|passed_scoped_multi_route|True|True|False|False / False / False|
|`671c68bdd229`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`6731b446fb96`|park-for-return|passed_scoped_multi_route|False|False|False|False / False / True|
|`6a036fea58d4`|timed-cache|passed_scoped_multi_route|False|False|False|False / False / False|
|`6a586b10102e`|grapple-jump-refill|passed_scoped|False|False|False|False / False / False|
|`6b9d2d9858db`|chase-landing|passed_scoped|False|False|False|False / False / False|
|`6d96e4e0357c`|trapdoor-commit|passed_scoped|False|False|False|False / False / False|
|`6dc4c0eb7179`|park-for-return-repaired|passed_scoped_multi_route|False|False|False|False / False / False|
|`708a6dd6002a`|sightline-backtrack|passed_scoped|False|False|False|False / False / False|
|`71f3c62d99ef`|block128-moving-station-choice|passed_scoped_multi_route|True|True|False|False / False / False|
|`747d7f54552a`|enemy-attack-relay|passed_scoped|False|False|False|False / False / False|
|`79769580e6f6`|landing-reload-relay|passed_scoped|False|False|False|False / False / False|
|`7acc4cdfa042`|moving-ray-window|passed_scoped|False|False|False|False / False / False|
|`7aef28e0dbe7`|late-air-rise|passed_scoped|False|False|False|False / False / False|
|`7bf07d9995b1`|trapdoor-commit|passed_scoped|False|False|False|False / False / False|
|`7c06b9a528bb`|air-refund|passed_scoped|False|False|False|False / False / False|
|`82d2d47c4d0f`|block128-bell-carrier-catch|passed_scoped_multi_route|True|True|False|False / False / False|
|`851be7661e7c`|enemy-sensor-hold|passed_scoped|False|False|False|False / False / False|
|`87731645f7be`|wall-projection-unlock|passed_scoped_multi_route|True|True|True|False / False / False|
|`87b8ed50f5b8`|timed-gate-return-catch|passed_scoped_multi_route|True|True|True|False / False / False|
|`881c3c38531a`|enemy-displace-landing|passed_scoped|False|False|False|False / False / False|
|`88c75d0f8e7a`|pass-receiver-turn-fork|passed_scoped_multi_route|True|True|True|False / False / False|
|`89300bb54eb5`|grapple-anchor-gap|passed_scoped|False|False|False|False / False / False|
|`89cc9ca617c8`|thorn-slot|passed_scoped|False|False|False|False / False / False|
|`8c90c97e8fc1`|timed-cache|passed_scoped|False|False|False|False / False / False|
|`8e0ad37d208f`|one-shot-two-routes|passed_scoped_multi_route|False|False|False|False / False / False|
|`8f066baa2327`|folded-floor-side-XOR-airlock|passed_scoped_multi_route|True|True|True|False / False / False|
|`8f308dc1ea1a`|prepared-air-sequence|passed_scoped|False|False|False|False / False / False|
|`934403a04df4`|bell-wall-rebound|passed_scoped|False|False|False|False / False / False|
|`9450553d8135`|central-two-wing-bridge-choice|passed_scoped_multi_route|True|True|True|False / False / False|
|`9bd1cff9a906`|ordered-target-transaction|passed_scoped|False|False|False|False / False / False|
|`9c2b5f3c7424`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`9e704f936271`|paired-support-transfer|passed_scoped_multi_route|False|False|False|False / False / False|
|`a1af6569a708`|evacuate-rejoin|passed_scoped|False|False|False|False / False / False|
|`a4e02aaf4b17`|park-for-return|passed_scoped_multi_route|False|False|False|False / False / True|
|`a8b3f205807d`|chase-landing|passed_scoped_multi_route|False|False|False|False / False / False|
|`aa4aa60a36d6`|thorn-slot|passed_scoped|False|False|False|False / False / False|
|`ab5d60871a32`|thorn-slot|passed_scoped_multi_route|False|False|False|False / False / False|
|`af12390291ec`|central-two-wing-bridge-choice|passed_scoped_multi_route|True|True|True|False / False / False|
|`af3cbd68127b`|air-refund|passed_scoped_multi_route|False|False|False|False / False / False|
|`b0a994d20b21`|carrier-dual-service|passed_scoped|False|False|False|False / False / False|
|`b3e5b6101b47`|windgap-junction|passed_scoped_multi_route|False|False|False|False / True / False|
|`b4634207ffe0`|trapdoor-commit|passed_scoped|False|False|False|False / False / False|
|`b901a01e4309`|wall-slide-launch-window|passed_scoped|False|False|False|False / False / False|
|`b961d4a468fd`|one-shot-two-routes|passed_scoped_multi_route|True|True|False|False / False / False|
|`baad7e601085`|paired-support-transfer|passed_scoped_multi_route|False|False|False|False / False / False|
|`bc83b615bdf9`|one-shot-two-routes|passed_scoped_multi_route|False|False|False|False / False / False|
|`bee87fe2de0b`|enemy-attack-relay|passed_scoped|False|False|False|False / False / False|
|`bf2761ddec8c`|chase-landing|passed_scoped|False|False|False|False / False / False|
|`bfb0e2996b1a`|chase-landing|passed_scoped|False|False|False|False / False / False|
|`c039ba158429`|ordered-target-transaction|passed_scoped|False|False|False|False / False / False|
|`c3268da6f09c`|brake-under-ledge|passed_scoped_multi_route|False|False|False|False / False / False|
|`c5825cd70475`|thorn-slot|passed_scoped|False|False|False|False / False / False|
|`c98366c7d7fb`|block128-underledge-brake-return|passed_scoped_multi_route|True|True|False|False / False / False|
|`c99a287ae8fc`|thorn-slot|passed_scoped|False|False|False|False / False / False|
|`ca4aa8bdf05b`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`cb14b0aaa167`|serial-airlock-recoil|passed_scoped_multi_route|False|False|False|False / False / False|
|`cd678ae924a9`|bell_lift|passed_scoped|False|False|False|False / False / False|
|`d111648359a5`|evacuate-rejoin|passed_scoped|False|False|False|False / False / False|
|`d5fe842b15c1`|enemy-displace-landing|passed_scoped|False|False|False|False / False / False|
|`d65bc5715ce9`|chase-landing|passed_scoped|False|False|False|False / False / False|
|`d8c58bc54db2`|brake-under-ledge|passed_scoped|False|False|False|False / False / False|
|`d9391ea2ff89`|thorn-slot|passed_scoped_multi_route|False|False|False|False / False / False|
|`dbb99f259703`|carrier-dual-service|passed_scoped|False|False|False|False / False / False|
|`de3f1cb2b245`|moving-ray-window|passed_scoped|False|False|False|False / False / False|
|`e1aed107d2df`|saw-pursuit|passed_scoped|False|False|False|False / False / False|
|`e3d75c7964b4`|block128-human-A1-bidirectional|passed_scoped_multi_route|True|True|False|False / False / False|
|`e49f2d38b96e`|enemy-clear-sightline|passed_scoped|False|False|False|False / False / False|
|`e53e91571f0d`|low-ray-recoil-return|passed_scoped|False|False|False|False / False / False|
|`e90dfa359fd0`|one-shot-two-routes|passed_scoped_multi_route|False|False|False|False / False / False|
|`eb5193eb519c`|woven-bridge-interchange|passed_scoped_multi_route|False|False|False|False / True / False|
|`ebfdac3d0305`|sightline-backtrack|passed_scoped|False|False|False|False / False / False|
|`ec4d2d7c66f3`|block128-new-wall-collision-brake|passed_scoped_multi_route|True|True|False|False / False / False|
|`edb7ee7a3d7c`|block128-serial-airlock|passed_scoped_multi_route|True|True|False|False / False / False|
|`f485c275bafd`|switchback-wall-ascent|passed_scoped|False|False|False|False / False / False|
|`f5b43214c3b5`|timed-gate-return-catch|passed_scoped_multi_route|True|True|True|False / False / False|
|`f5d535499ccf`|refill-short-gate|passed_scoped|False|False|False|False / False / False|
|`f678fdeefc8b`|under-column-escape|passed_scoped|False|False|False|False / False / False|
|`f7a091b3c8a5`|block128-human-A3-bidirectional|passed_scoped_multi_route|True|True|False|False / False / False|
|`fa1ab9221e4c`|adverse-refund-reversal|passed_scoped|False|False|False|False / False / False|
|`fad52f5cc43e`|adverse-refund-reversal|passed_scoped|False|False|False|False / False / False|
|`fad73947ee6c`|thorn-slot|passed_scoped|False|False|False|False / False / False|
