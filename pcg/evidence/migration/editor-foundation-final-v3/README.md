# 新版专用编辑器验收

225 个当前 Module，128px Block 与真实 Port 位置/朝向/surface/权限；200 双口、19 三口、6 四口，按物理口计数。2 个模块具有同一物理口的逻辑别名，界面合并字形但不改合同身份。

本目录保存真实 Chromium 与静态构建验收，无网络 mock，不授予新物理资格或人工批准。226 个基础/替代配置文档原 SHA 均未变化。检查了角口整配置、标签可见性、缩放、开关、PNG/JSON 下载，以及远端目录未发布时保留 225 条本地列表和草稿。推送后远端真实更新的成功记录另存。

复现（输出路径需为新目录）：

```sh
npm run check
python3 tools/build_editor_site.py --out /tmp/module-editor-site-new
python3 tools/browser_current_archive_check.py --site-root /tmp/module-editor-site-new --out /tmp/module-editor-browser-new --module plains50-ports-brake-branch-0 --configuration c-bottom-right-v1 --exercise-files
```

GitHub Pages 环境当前仅允许 main。工作分支代码已实现，但本验收没有部署公网，线上网址需合并 PR 后更新。
