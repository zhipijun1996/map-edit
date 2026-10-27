# 当前工作入口：离线 Module 生产、验证与归档

本仓库继续服务 Module；旧 Map 实验已终止，不能作为生产依赖或未来架构依据。固定提交、失败分析、迁移清单见 [归档说明](../archive/mapgen-failed/README.md)。旧阶段报告均为历史证据；其中的“当前入口”和 Map 要求不再生效。

## 代码与数据边界

- `prototype/factory/`：基础动作生成、评价与真实物理批处理。
- `prototype/plains/`：独立平原挑战；依赖旧 Map 搜索的 Macro 生成器已退出当前代码。
- `prototype/workshop/`：离线创意输入、配方生产、多路线、证据和交付。
- `prototype/creative_batches/`：各内容批次；已修改活跃查库入口以读取中立库，旧版本数据保持原件。
- `module_library/`：独立候选库管理、证据验证、离线精确配方匹配；默认数据在 `module_library/store/candidates/`。
- `results/`、`archives/`、`feedback/`：不可变证据、原始失败与撤回。冻结源快照中的旧代码是证据，不可加入导入路径或恢复为生产代码。
- `../library/`：编辑器参考库；`../library/workshop/`是候选库静态浏览导出。

现有94候选保持原内容版本和原技术范围，不代表94份新规范认证。旧 Map 实例和具体地图上下文载荷已单独隔离，不参与 Module 查库。历史路径的文件引用只能通过已登记且逐SHA核验的数据迁移表解析，不存在旧包导入别名或旧库目录。

## 当前命令

仓库根目录：

```sh
npm run check
npm run check:modules
python3 -m pcg.module_library.audit
```

基础工坊在 `pcg/` 执行：

```sh
python3 -m unittest discover -s prototype/factory/tests -v
python3 -m unittest discover -s prototype/plains/tests -v
python3 -m prototype.factory.core.producer --name new-run --tier regular
python3 -m prototype.plains.produce --help
```

新工坊在仓库根执行：

```sh
python3 -m pcg.prototype.workshop.production_loop --help
python3 -m pcg.prototype.workshop.creative_producer --help
```

配方的尺寸、端口、初态仅约束该离线配方；不代表新 Module 或 Map 的通用规则。`carrier_fixture`仅使用冻结的本地挑战需求，不执行 Director。退役 Map 适配配方明确返回 `needs_design`，不会生成地形或恢复旧实现。

## 物理与证据

Godot为官方4.7.2 Standard；二进制SHA `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`。真实游戏原件来自12f6cb0，受保护文件870份。编辑器177份参考模块来自不同版本74d8a06，不能继承这份物理结论。

原件来源与许可证见 `prototype/godot/source_provenance.json`、`asset_licenses_provenance.json`。运行前核对来源；Engine自动冻结本轮源、输入、输出和失败。新代码不能给旧内容补写验证通过。

恢复工具 `tools/restore_archive.py` 可校验历史归档、恢复仍有效的Module证据。包含已迁移候选或退役路径的全量恢复会拒绝；需要历史代码时使用归档固定Git提交，在独立目录检出，不覆盖活跃工作区。

## 交付与审核

现有输出格式见 [OUTPUT-CONTRACT.md](OUTPUT-CONTRACT.md)。保持内容版本、证据原件、能力与方向范围、UNKNOWN和撤回语义。人工观感、真人试玩、技术通过、正式批准分别记录，不能相互代替。

本轮隔离不定义后续新 Module 的矩形、Port、封口或镜像认证格式；这些由后续契约工作统一。更不引入新的 Map 算法、在线状态搜索或自动补缺链。
