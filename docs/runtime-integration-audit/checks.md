# 检查与复现

本次比较 main 固定为 `9b712fe814ef228b368c0eb9adf660e39de29e37`，不是执行时重新抓一个会变化的 main。运行审计分支中的工具，生产 `modules/` 必须仍等于该基线。工具只读原件，向指定 `--out`/外部临时目录写审计结果。需要 Python 3、Node、Git；原生探针另需 Linux、strace、包锁定 Godot。外部只读核对使用已授权的 `gh`。

合入统一源库后，当前 `modules/` 已不等于此历史基线。复现本页的 main 对比时，请使用审计提交 `2ec243842567a56a49b84fc93ce4aa750b11ff5f` 的独立 worktree；不要将旧 82 项断言用于当前目录。actual-profile producer 的独立回归仍可在当前树执行，见 [整合记录](../main-integration-20261104.md)。

## 输入与静态检查

在仓库根目录执行，`AUDIT_WORK` 是独立临时目录，不能指向当前生产目录或历史包目录：

```bash
AUDIT_WORK=$(mktemp -d /tmp/map-edit-runtime-audit.XXXXXX)
ZIP_SHA=5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/47aefebe07f4f0e7471f3d1546214502a6b2aade/releases/map-edit-modules-1.1.0.zip' -o "$AUDIT_WORK/modules.zip"
printf '%s  %s\n' "$ZIP_SHA" "$AUDIT_WORK/modules.zip" | sha256sum -c -
```

必须上一步成功才继续；所有工具也在 ZIP 解析之前重复检查该 SHA。重算作者 fingerprint 需要来源提交中的原始 index，发布 index 去掉了 sourcePath，不能简单比发布图谱值：

```bash
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/02b5cb53b06d7009225b2ecff9351f315e46b12e/runtime/module_runtime/index.json' -o "$AUDIT_WORK/authored-runtime-index.json"
mkdir "$AUDIT_WORK/later"
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/c2e23fec3ec424a7b8e41552bbe2c4ed2a6c8afd/evidence/module-production/reward-claim-validation.json' -o "$AUDIT_WORK/later/reward-claim-validation.json"
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/c2e23fec3ec424a7b8e41552bbe2c4ed2a6c8afd/pcg/archives/reward-claim-validation-v1/manifest.json' -o "$AUDIT_WORK/later/manifest.json"
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/c2e23fec3ec424a7b8e41552bbe2c4ed2a6c8afd/pcg/archives/reward-claim-validation-v1/reward-claim-validation-v1.zip.part001' -o "$AUDIT_WORK/later/reward-claim-validation-v1.zip.part001"
printf '%s  %s\n' baf28c8f04639b829b7ecb1172a55f5600f9fa0dc8b388e49da19175434961d8 "$AUDIT_WORK/later/reward-claim-validation.json" | sha256sum -c -
python3 tools/runtime_audit/check_inputs.py \
  --zip "$AUDIT_WORK/modules.zip" --sha256 "$ZIP_SHA" \
  --main-commit 9b712fe814ef228b368c0eb9adf660e39de29e37 \
  --authored-runtime-index "$AUDIT_WORK/authored-runtime-index.json" \
  --later-evidence "$AUDIT_WORK/later" --out "$AUDIT_WORK/results"
python3 -m unittest discover -s tools/runtime_audit/tests -v
```

后续报告仅作为证据输入，不覆盖历史包；脚本核归档 manifest、分片、索引成员、解压原始输出的 SHA，确认 15 组领取/钱包/出口与 owned Cells 相等。省略 `--later-evidence` 就不出此项结论；省略 `--authored-runtime-index` 就不声称重算作者 fingerprint。

`check_inputs.py` 复用当前库的 `validateGenerationContract`、`audit_cases` 和 `verify_package`。旧 verifier 对两个 main 样本缺少忽略的外部原生资源，错误原样保留在 `legacy-verifier.json`；这一步不是悄悄跳过物理失败。直接几何一致性检查成功，原生定向探针在下文独立执行。

依赖检查结果 `dependency-checks.json` 覆盖包脚本字面量 preload/load/extends、场景资源路径，以及人工核到的动态 plains_sentry/plains_charger 白名单；检查其存在于包 manifest 或两份宿主锁。任意代码计算的资源名不在静态证明范围，宿主完整传递依赖仍须逐文件哈希安装与实际加载验证。

## 干净原生宿主与真实 Godot

先从**已经核 SHA**的 ZIP 解出只读参考包到外部目录：

```bash
python3 -m zipfile -e "$AUDIT_WORK/modules.zip" "$AUDIT_WORK/reference"
python3 "$AUDIT_WORK/reference/integration/install_host.py" \
  --lock "$AUDIT_WORK/reference/runtime/host-lock.json" --target "$AUDIT_WORK/native-cache"
python3 "$AUDIT_WORK/reference/integration/install_host.py" \
  --lock "$AUDIT_WORK/reference/runtime/host-lock-current-game.json" --target "$AUDIT_WORK/api-cache"
```

安装器是包内既有工具，下载锁定提交的文件并逐个核 SHA。也可用 `--source` 指向既有干净缓存，加快复现；不得覆盖到最新主游戏工程。原生锁 1,389 文件/API 锁 1,600 文件，API 锁不参与本轮 native 探针。

取得 `runtime/host-lock.json.godot` 指定的官方 Linux x86_64 Godot 4.7.2，二进制 SHA 必须是 `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。将下面的路径替换为该二进制；runner 会再次核 SHA，复制到干净目录，安装原生锁，执行真实 headless import 和 60fps 探针：

```bash
python3 tools/runtime_audit/run_probes.py \
  --zip "$AUDIT_WORK/modules.zip" --sha256 "$ZIP_SHA" \
  --host-source "$AUDIT_WORK/native-cache" \
  --godot /absolute/path/Godot_v4.7.2-stable_linux.x86_64 \
  --work "$AUDIT_WORK/godot" --out "$AUDIT_WORK/results/godot-probes.json"
```

`--work` 必须尚不存在，防止旧导入缓存冒充干净验证。`--host-source` 可省略，由既有安装器下载精确文件。runner 使用现有包 loader + **测试夹具注入**的原生外部玩家/服务；并未实现新的主游戏装载器。夹具给风铃样本增加的是生成器假设的封口，不改原件；环岛原始开放内容只作独立语义对照，不改被审计的封口配置。

runner 用 strace 记录探针文件读取，拒绝读取作者工作树、旧 implementation 和 pcg/results。输出 `authoringOrLegacyWorkspaceRead=false` 只描述这次实际执行路径，不能扩成所有 115 项/任意资源的动态证明。完整 import/file-read 日志留在外部 `--work`；提交中的 `godot-execution.json` 和 `godot-probes.json` 记录实际命令、引擎/脚本/输入/日志 SHA。无图形录屏，本轮不重做影片。

## 只读下游核对

```bash
python3 tools/runtime_audit/check_external.py \
  --zip "$AUDIT_WORK/modules.zip" --sha256 "$ZIP_SHA" \
  --native-cache "$AUDIT_WORK/native-cache" --api-cache "$AUDIT_WORK/api-cache" \
  --sources "$AUDIT_WORK/read-only-downstream" \
  --out "$AUDIT_WORK/results/external-source-checks.json"
```

固定 map-gen `178c40164c2f7371ce1c8a56cde658e84a4f42c2`、gunman-rush `30e36c9abe223f26e666ceaf796e3fe9cb58e10f`，从 commit 取真实 tree SHA，逐 Git blob 核对 15 份选定源码，比较两份宿主锁所有文件。此命令不执行生成器、不修改两个下游仓库。人工提取的公开 API/路径观察保存在 `host-api-observations.json`，不能当成 ABI/行为认证。

## 本次实际结果与未验证项

结果都在 [evidence/runtime-integration-audit-20261103](../../evidence/runtime-integration-audit-20261103/)：

| 检查 | 结果 |
|---|---|
| 输入 ZIP / manifest | SHA 相符；657 文件哈希/集合通过 |
| main artifacts / 文档 | 82 项，1,663 产物哈希；82+115=197 份原件验证通过 |
| 对比 | 81 共同 ID 全部内容版本不同，80 原生字段不同；包独有 34，main 独有 1 |
| 作者 runtime fingerprint | 从原来源 index 重算 `434d2227…` 成功 |
| 五项后续奖励证据 | 15 原始 case/三组策略实测逐项核验；不是本轮重新运行 15 条路线 |
| 真实 Godot 定向记录 | 16 行观察：6 非法初始放置、6 风铃候选通过、2 未射击阻挡对照、1 环岛封口查询组、1 原内容领取对照 |
| 检查工具回归 | 7 项测试通过，包括错 SHA 先拒绝、manifest 篡改、路径逃逸、源偏移、全区阻塞/非包含反例、未声明宿主资源 |
| 初次启动失败 | 仅测试脚本 Array 推断错误；保留 `godot-initial-setup-failure.log`，修正后在新的 v2 目录通过，不把失败算 Module 失败 |

未验证：最新主游戏整体兼容、实际起点实例的镜像/封口/邻模块快照、风铃出口完整跨邻接缝、全部平台/敌人/伤害/Boss 接入、任意初相、所有镜像/封口/换边配置、整图可玩性。本轮没有增加认证、变更原件、迁移模块、发布包或自动合并。
