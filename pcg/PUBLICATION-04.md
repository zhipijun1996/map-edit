# PCG-DYNAMIC-04 发布回执

- 试玩：https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-DYNAMIC-04/3c3c632119900bf757a95aced5c2d3c9e6fa7103/a5602bfd6b8d/
- 报告：https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-DYNAMIC-04/3c3c632119900bf757a95aced5c2d3c9e6fa7103/a5602bfd6b8d/report.html
- 四段原生Godot录像：https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-DYNAMIC-04/3c3c632119900bf757a95aced5c2d3c9e6fa7103/a5602bfd6b8d/modules.mp4（28.2秒，862945字节）。
- 完整研究源码与原始实验数据：https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/1c01f9af95620dcdd28c313b5e77aafa664019d4/artifacts/PCG-DYNAMIC-04/3c3c632119900bf757a95aced5c2d3c9e6fa7103/pcg-dynamic-04-source-and-data.zip
- 研究源：`3c3c632119900bf757a95aced5c2d3c9e6fa7103`；Game基线 `12f6cb006d7119598e3235f4ca4f7323e4c9d092`；Godot4.7.2。
- PCK：`a5602bfd6b8d`，完整SHA256 `a5602bfd6b8d64d4f31b963abf1c9c84f73a5162e49ffda42446d9e924186c6f`，562432字节。相同旧Base PCK与官方JS/WASM按不可变URL复用。
- 数据ZIP：28621271字节，SHA256 `3a06e8e7785ba6259df4f9ece1846fff88a859376db7f808eb30b42916d77014`。从公网下载逐字节核对通过。压缩包CRC全过，含逐文件SHA、正式全部输入输出/失败与历史源；原游戏素材按固定源恢复。
- Pages部署：`f76826604d99c2b0329d7f1f4da2bb869e80ce5e`，[run39976835041](https://github.com/zhipijun1996/gunman-rush-previews/actions/runs/39976835041) success。
- 公网37项完整字节校验（34新文件+3不可变运行依赖）全部通过，共109674846字节，preview身份与本地一致。
- 本地最终17个回放及D/跳/R操作通过；17候选共7404帧UI/worker对照通过；20区域合同+2能力快照+12既有动作回归过，870原件无漂移。
- 1011既有站点文件哈希零变化；正式游戏站点未动；900MiB guard未提高。完整数据放仓库 `artifacts/`，不计入Pages站点。

## 发布适配与保留失败

最初托管提交遗漏被仓库ignore的PCK，已显式纳入；早期两个Pages运行39976137851/39976188935失败保留。现有托管器要求 `index.<hash>.pck`、`build-info.pack`与 `index.cache-sw.js` 完整性清单，现已按原要求补齐，PCK字节和运行物理没有改变；没有改guard/验证工具绕过检查。原有official verify-host本地及CI均过。新目录在首次成功部署前完成这些适配，未覆盖任何旧公开版本。

Release上传返回401；没有要求用户重新认证。改为同仓库非站点数据目录，固定数据commit `1c01f9af95620dcdd28c313b5e77aafa664019d4`，下载哈希一致。研究源3c3c632中的发布helper是首次尝试源；后续出版适配在研究工作区单独提交，不更换实验算法/原始源。当前helper已修标准命名/清单并在stage调用原有verify-host；最终push前必须显式 `git add -f` PCK，非site数据用 `git add --sparse`。旧失败与完整本地交付日志留存delivery/dynamic-v3。

本轮只接受有限研究物理与数据范围：8个真实区域正例、3个混合词不能签人类趣味或长期多样性；5条诊断候选REWORK，不准入批量成品池。Runtime/正式区域Bible/完整Map/Map Notes/手机与用户趣味均未验收。

公网17回放检查：全部通过，22条操作/回放记录，页面与引擎错误0；原生输入回放均无伤、HP5、稳定出口至少6帧。证据：delivery/dynamic-v3/browser-public/browser.json。
