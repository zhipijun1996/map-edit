# 接纳 actual-profile：实际覆盖提取与边界

在 PR78 `812e89050e062c866a5dd7e8c258e47d3897bc4d` 上继续，仍锁模块包 **1.1.0 / `5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723`**。实现位于本 PR 分支，尚不等于已合入 main；不修改 Module、不发包、不合并PR77、不执行全库生产。本轮没有运行Godot/SDK/主游戏。

## 来源审查与同一 producer

上游审查对象：[PR129 / 46eb3960a592374b5fb99d7df588962a3680f86b](https://github.com/zhipijun1996/gunman-rush/tree/46eb3960a592374b5fb99d7df588962a3680f86b)，[合同](https://github.com/zhipijun1996/gunman-rush/blob/46eb3960a592374b5fb99d7df588962a3680f86b/docs/worklines/mapgen_godot_04/upstream_contract.md)、[证据入口](https://github.com/zhipijun1996/gunman-rush/blob/46eb3960a592374b5fb99d7df588962a3680f86b/docs/evidence/mapgen_godot_04/README.md)。交接head是46eb，实际运行源是 **f6b61ee7026bc4c696d15fa26b09de5ff03be903**，两者不混称。

入口仍为 [tools/runtime_audit/check_930001.py](../../tools/runtime_audit/check_930001.py)。接受外部候选的共享 `extract_inventory` 重构与显式 `--actual-profile` 分支；原默认CLI/43输入锁/两ZIP/10输出不变，没有第二套提取器。候选补丁应用后的源码SHA=`52e36a13…`，先复现其两个完整输出的原SHA，再补强。完整差异和来源SHA见 [producer-review.json](../../evidence/runtime-integration-actual-04/producer-review.json)。

新增的是输入/证据校验，不是新的游戏Module契约、地图生成器或场景消费者。`verify_actual_profile.py` 只调用这个producer开展重放/篡改测试。

## actual-profile 七角色必须绑定什么

profile 格式仍为 `profile=actual-0.4.0`，含 host_commit、mapgen_commit、generation_package_sha256、恰好七个 `{path,sha256}` 文件角色；相对 `--inputs` 解析，越界/缺文件/错SHA拒绝，所有验证完成前不写表。输出必须是新目录，不覆盖旧冻结目录。

| 角色 | 新实现实际检查 |
|---|---|
| result | 原完整 generation-result/v1、PASS、0.4/stable-v3-reward-space、seed、实例/连接ID唯一及端点存在；不接受只有切片的content_store |
| provenance | generated_memory；原request/config、模块1.1.0、算法ZIP7aa3…、source=b21c8890…、release=6bf07ab5…相互绑定 |
| protocol_payload | **原GDScript编码的精确字节**SHA等于result/provenance/map中的指纹；解码对象等于request/config/library/implementation。Python不重造GDScript canonical数值编码，追加换行也拒绝 |
| host_bindings | 同一指纹；selected/resolved实例集合、module/version/role/origin/transform、root、内部连接完整内容和计数均与实际map一致；spawn平台引用、world/local原点关系、spawns和身体尺寸互相一致。不是从官方sample填宿主事实 |
| host_provider | 原字节SHA必须出现在before/after源向量的真实Provider路径；读取其ADAPTER_VERSION及字段拒绝列表，保留代码SHA。看到相似类不等于兼容 |
| host_source_snapshot | commit=profile源提交，记录的before/after相等；原生receipt一致、源数量一致、changed_paths为空；用原Python源向量ASCII/sorted/indent2编码重算两份记录digest。`deleted`条目保留，不冒称本轮物化了所有源文件 |
| validation_evidence | receipt等于snapshot内同一receipt，head/源digest与harness commit一致；按原Python报告编码重算嵌入harness_report的SHA。保留检查状态/失败/范围；不据报告存在为任意机制行打通过 |

源向量/报告编码已与PR129原`final-native/source-before.json.gz`解压字节、`report.json`逐SHA核对；与GDScript指纹编码是两件事。见 [encoding-reference-checks.json](../../evidence/runtime-integration-actual-04/encoding-reference-checks.json)。

完整性守门读取已核SHA的原ZIP compiled：根字段集合、所有层级的数组长度、对象字段、容器/数字类型、稳定本地ID与引用均保留；仅接受原反射允许的ellipse_x_sign差异与左右face变化。核移动体/敌人/奖励/门/刺/Port/Route引用；原compiled中未建模的非空内容也拒绝，不静默少计。固定台/索引/元数据不冒充机制对象数。

**不证明的事项**：不重实现坐标镜像，不证明调用者重锁后的所有数字等于物化变换，不执行Provider/物理，不独立证明所有Git源或同次运行的真实性。可信来源边界是固定PR129与其输入归档；若调用者连七记录及所有SHA一起伪造，离线一致性检查无法代替独立执行/签名。

## 新旧结果与三种事实

结果见 [verification.json](../../evidence/runtime-integration-actual-04/verification.json)、[实际default覆盖](../../evidence/runtime-integration-actual-04/default/mechanism-coverage.json)、[实际gears覆盖](../../evidence/runtime-integration-actual-04/gears/mechanism-coverage.json)。

| 模式 | 实际结果 |
|---|---|
| 旧默认0.3 | 43原输入；原producer/接纳版/PR78原件三方10输出逐字一致。原/新各缺件及M35篡改，共4次拒绝且无输出 |
| actual default / seed930001 | 46实例、58连接、21个模块版本、13组、109对象 |
| actual gears / seed930007 | 43实例、55连接、20个模块版本、14组、110对象 |
| actual拒绝 | 保留原38项；新增48项：binding错配、Provider/源/receipt错配、嵌套删改/稳定ID/接口引用/路径缺件等，86/86拒绝且无输出；另2个输出覆盖守门通过 |

接纳版新增 `assessment`；删掉这一个新增节，两个完整JSON仍分别匹配候选原输出SHA `3c79e25e…` / `dfcab57b…`，不只是数量相同。新表所有行仍 `UNVERIFIED_CURRENT_HOST`。`timed_gate` 沿用旧producer组名，实际行可能含paired_gate/initial_open/额外接收点；完整原值保留，不能据组名当普通计时门适配。

- **数据存在**：`assessment.dataPresence` 只证明完整结构、引用和输入锁。13/14少于旧17来自真实新布局，不是删字段后少计。
- **适配器支持**：`assessment.provider` 保存精确版本/SHA/拒绝列表，`adapterObservationsByGroup` 区分字段不在白名单、要求空、仅通过字段存在筛选。后者仍需后续转换/几何/同模块其他机制检查，不叫兼容PASS。
- **实际执行证据**：`assessment.execution` 原样列同源native receipt与12项状态，resolvedSelection分别为default的三模块和gears的M35；证据范围是受控切片。它不是109/110对象逐项执行表，不改变各行状态。

原主游戏默认双fresh300秒Web消费者仍 **FAILED/BLOCK**；独立gears或TARGETED_ONLY取消诊断不能改签该aggregate。手机、硬帧预算、整图、全机制/敌人/奖励/Boss、全部跨缝仍未验证。

## 复现命令

取 [input-custody.json](../../evidence/runtime-integration-actual-04/input-custody.json) 中固定archive URL；归档SHA=`59cb6e2b5c30133a752c2dd044ab3fbf98a8e080822904d2053d8a64eec6d789`，13叶（含两profile）逐项SHA不变。它是宿主原始证据运输包，不是模块新发行包。

```bash
ACTUAL_WORK=$(mktemp -d /tmp/map-edit-actual04.XXXXXX)
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/gunman-rush/46eb3960a592374b5fb99d7df588962a3680f86b/docs/evidence/mapgen_godot_04/coverage-inputs-f6.tar.gz' -o "$ACTUAL_WORK/inputs.tar.gz"
python3 - "$ACTUAL_WORK" <<'PY'
import hashlib,json,pathlib,sys,tarfile
root=pathlib.Path(sys.argv[1]);archive=root/'inputs.tar.gz'
lock=json.loads(pathlib.Path('evidence/runtime-integration-actual-04/input-custody.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==lock['sha256']
with tarfile.open(archive) as t:
    leaves={m.name:m for m in t.getmembers() if m.isfile()}
    assert set(leaves)==set(lock['members_sha256'])
    for name,m in leaves.items():
        p=pathlib.Path(name);assert not p.is_absolute() and '..' not in p.parts
        data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==lock['members_sha256'][name]
        out=root/'inputs'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
PY
ZIP110="$ACTUAL_WORK/module-pack-1.1.0.zip"
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/47aefebe07f4f0e7471f3d1546214502a6b2aade/releases/map-edit-modules-1.1.0.zip' -o "$ZIP110"
python3 tools/runtime_audit/check_930001.py \
  --actual-profile "$ACTUAL_WORK/inputs/default-profile.json" \
  --inputs "$ACTUAL_WORK/inputs" --zip110 "$ZIP110" --out "$ACTUAL_WORK/default-output"
python3 tools/runtime_audit/check_930001.py \
  --actual-profile "$ACTUAL_WORK/inputs/gears-profile.json" \
  --inputs "$ACTUAL_WORK/inputs" --zip110 "$ZIP110" --out "$ACTUAL_WORK/gears-output"
python3 tools/runtime_audit/verify_actual_profile.py \
  --inputs "$ACTUAL_WORK/inputs" --zip110 "$ZIP110" --work "$ACTUAL_WORK/verification"
```

旧兼容全重放在最后命令附 `--legacy-inputs "$OLD_43_INPUTS" --zip111 "$ZIP111"`；两项成对提供，原恢复命令见 [930001旧交接](930001-handoff/README.md)。ZIP111只供原默认兼容测试，不进入actual消费。验证器工作目录必须未存在；原actual输入不变、输出/合成篡改在独立测试目录。原始拒绝日志合并保存于 [verification-trace.txt](../../evidence/runtime-integration-actual-04/verification-trace.txt)，每日志SHA见同目录log-hashes.json。

下一批钟门见 [windchime-04-recheck.md](windchime-04-recheck.md)。在新适配commit到达前，本轮工具接纳、复现、拒绝测试和最小输入交接已完成；不预签新宿主。
