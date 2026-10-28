# 第一批人工审批

每批5个；按编号反馈“保留 / 修改 / 废弃”。原件和技术认证保持原范围，人工意见仅绑定本批sourceSha256/contentVersion。

- 01 [中庭双翼换桥](01.png)：射铃交换两块紫桥的实体状态，从低入口 A / D 选择上方 B / C。
- 02 [折返回廊](02.png)：去程取上层宝箱；从返回侧再击铃，换出下层回程桥。
- 03 [一空中资源，两种落岸](03.png)：从 A 进入，选择上方取奖线 B，或通向更低远岸的 C。
- 04 [越铃回身选路](04.png)：越过风铃后回身射击，选择左侧 B 或右侧 C；门开启 1 秒。
- 05 [斜射开高门](05.png)：从低口 A 上跳，斜射低处风铃开门，再到高口 B 取奖。

手机审阅入口：index.html。意见仅存于本浏览器 localStorage，使用“复制整批评价”粘回聊天；未收到用户原话前不更新批准状态。

示意图重绘：`python3 generation/manual-review/batch-001/render_diagrams.py`（Python Playwright 与 `/usr/bin/chromium`；重绘前检查源 SHA256，不生成新 Module，不运行物理实验）。
