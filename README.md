# Module 工坊与生产库

唯一可编辑源库是 [`modules/`](modules/)，入口为工具生成的 [`modules/catalog.json`](modules/catalog.json)。每个稳定 ID 只维护一份当前原件和 `record.json`；开发设计、已保留实现、运行交付与退役状态分别记录。编辑器、工坊和更新按钮使用同一目录，正式更新分支为 `main`。

生产步骤见 [Module 生产说明](docs/module-production.md) 和 [生产 skill](.agents/skills/pcg-module-production/SKILL.md)。几何、Port、实际有向 Route 与配置约束以 [MAP_FOUNDATION.md](MAP_FOUNDATION.md) 为准。

```sh
npm run check
npm run test:production
python3 -m module_pipeline build --version 1.1.0
```

当前库保留 115 个已审核实现、3 个待审开发设计；148 个退役 ID 仅留记录，原件退出生产。具体版本、交付状态与排除原因以目录和包为准。新增用 `add`，同 ID 修改用 `update`，精确版本审批用 `review`，真实物理证据准入用 `qualify`，废弃用 `withdraw`；上述子命令均属于 `python3 -m module_pipeline`。

[1.1.0 模块包](https://github.com/zhipijun1996/map-edit/releases/tag/modules-v1.1.0) 是自动生成产物，交给 [map-gen](https://github.com/zhipijun1996/map-gen) 和 [gunman-rush](https://github.com/zhipijun1996/gunman-rush) 按明确版本使用。读取、实例定位、稳定实例 ID、原生宿主依赖和外部玩家绑定见 [下游接入说明](docs/module-package-consumers.md)。完整导出 `reward_sites`，路线关联沿用 `resourceProfile.requiredRewards`。map-gen 统一镜像完整内容并选择 Port 子集、添加齿轮封口和检查剩余路线；原认证范围保留，新配置不会自动获得认证。奖励关联缺口随包自动生成。

历史可从合并提交 `9b712fe814ef228b368c0eb9adf660e39de29e37` 或不可变 `pcg/archives/` 恢复，当前生产不扫描这些内容。清理与验证事实见 [`evidence/module-production/`](evidence/module-production/)。

本地编辑器：`npm run serve` 后打开 `http://localhost:8080/`；工坊位于 `/generation/module-workshop/`。

交付验收见 [`evidence/module-production/final-package.json`](evidence/module-production/final-package.json)。`releases/` 中的 ZIP、校验和与元数据均为固定版本生成物，不在其中编辑 Module；精确复建请先检出包内 `manifest.json.source.commit`，再执行上述构建命令。
