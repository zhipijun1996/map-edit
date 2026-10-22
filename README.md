# 关卡手记 · Map Notes

一个零依赖的网页关卡草图编辑器，为 Gunman Rush 记录关卡想法。

在线入口：https://gunman-map-notes.silkyball18.chatgpt.site

打开就能摆地形、机关、敌人，画物体轨道和人物动作路线。手机和电脑共用同一个界面。无需安装、无需账户；不运行游戏物理。

- 「模块库」提供 177 份可编辑参考：72 个原始 `.tres` 模块、51 份森林代码模块 / 变体、36 个工坊组合片段、18 条工坊连续路线。
- 点击模块会生成自己的草稿副本；原版始终留在库中。
- 左侧点击添加，画布拖动摆放；选中对象后调整尺寸、旋转、文字、轨道和机关目标。
- 人物路线逐点绘制，填写每步动作。下方路线菜单可切换主路、支路、奖励和返回路线。
- 直线 / 折线轨道逐点绘制；弧轨拖出曲线，再拖黄色控制点调整弧度。起点靠近物体中心会绑定，也可手动选择。
- 时间条预览机关运动和人物预期路线，不代表真实物理通关。
- 「导出图片」生成 PNG，包含说明文字；「保存工程」下载可再次编辑的 `.mapnote.json`，通常无需手工接触 JSON。
- 本机自动保存不跨设备、不上传服务器。换设备或备份请保存工程文件。

## 开发

```sh
python3 -m http.server 8080
# http://localhost:8080
npm run check
```

无需 npm install。当前在线版本使用 Sites 托管；GitHub 连接没有开启 Pages 的管理权限，因此未声称仓库 Pages 已部署。若后续在仓库 Settings → Pages 将 Source 设为 GitHub Actions，运行 `Deploy editor` 工作流即可发布到 `https://zhipijun1996.github.io/map-edit/`。部署仅上传静态页面与模块库，不上传工具和原项目源码副本。

## 模块库来源与覆盖

绑定 `gunman-rush@74d8a06b42cb2bc2c5023f1bfe1a4fbc4b163074`。

原始资源与森林工厂由 Godot 4.7.2 Standard 实际加载和执行，随后转换成编辑器对象。保留平台几何、单双向平台、各方向刺面、锯轮与摆渡运动参数、端口和原始路线；平原风铃及门的额外布置来自 `config/plains_shot_latches.json`。

库中包括历史模块和未正式准入的森林候选，类别明确分开。导入不授予新的正式准入状态。没有完整动作记录的模块显示原始安全锚点，不伪造通关轨迹。根据 action_program 绘制的反冲点仅作示意，保留原动作程序和标记。模块外由整图消费者配置的敌人 / Boss 不臆造；无限 Seed 的大地图实例和现场生成的接缝不逐一枚举。只列目录但未实现的场所不补画成已存在模块。

每份工程包含来源提交、路径、原数据与编辑平移量，完整清单见 `library/coverage.json`。工程的 JSON 结构独立于游戏存档 / Manifest，不会被直接当作已验证关卡运行。

复建流程（需要项目指定的 Godot 二进制）：

```sh
python3 tools/fetch_library.py
python3 tools/prepare_extraction.py /tmp/map-notes-extract
godot --headless --editor --path /tmp/map-notes-extract --import
godot --headless --path /tmp/map-notes-extract --script extract_modules.gd
python3 tools/build_library.py /tmp/map-notes-extract/extracted.json
npm run check
```

`library/source/` 保留固定版本的只读源码与配置快照，便于审计 / 复建；不带游戏大体积美术。若更新游戏版本，须重新下载同一提交的索引与依赖，再重新提取，不只替换提交号。

## 后续接入真实项目

使用「保存工程」把文件交给 Codex 即可。`objects` 包含稳定 ID、类型、尺寸、位置、轨道绑定、控制目标和文字；`route.points[].action` 保存预期操作；`description` / `constraints` 保存设计说明与必须保留的关系。

后续转换器可把实体与平台映射到 `PlatformingModuleDefinition.platforms`，刺面映射到 `PlatformThornDefinition`，锯轮 / 直线摆渡映射到现有 Definition；钩索、复杂场所和动作步骤映射到森林模块工厂。弧形轨道等尚无通用运行消费者的对象保留为设计需求，不能默默降级。正式尺寸、人物资源、接口接缝和动态相位仍在游戏中验证。

快捷键：V 选择；R 地块；空格移动画布；滚轮 / 双指缩放；Ctrl/Cmd Z 撤销；Shift Ctrl/Cmd Z 重做；Ctrl/Cmd D 复制；Delete 删除；Ctrl/Cmd S 保存工程。
