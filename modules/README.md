# 当前 Module 库

这里只存放符合 MAP_FOUNDATION、真实技术验证通过的当前模板。
每个稳定 ID 仅一个当前版本；内容哈希是校验信息，不是另一个模板。
人工趣味审核与技术认证分开，`UNKNOWN` 不等于批准。

JSON 是可编辑原件，Godot 包是离线编译产物。`catalog.json` 由
`python3 -m pcg.migration build` 生成，不能通过手写目录条目绕过认证。
尚未认证的 Port 关系、封口组合、镜像或接缝不授予 Map 使用资格。

旧模板可以保留局部负坐标，实例放置时以矩形左上角对齐 Block：
`node.position = origin_block * blockSize + sceneOriginOffsetPixels`。
Port 世界点为 `origin_block * blockSize + sceneOriginOffsetPixels + port.position`。
该偏移来自原件 bounds，不缩放或修改内部地貌；碰撞接缝仍须按认证范围选用。
