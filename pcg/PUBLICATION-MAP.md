# Map Notes 生成工作区公开交付

- 实际迁移/部署源：`b3ec6ceb1bbf869b89bf6d12847dd574a22a84e2`，原父提交ccbb21e。完整上传tree与本地已验Git index逐字节身份相同，非force更新main。
- [生成与视频入口](https://zhipijun1996.github.io/map-edit/generation/)。[合集A：23.88秒](https://zhipijun1996.github.io/map-edit/generation/videos/factory05/all-samples.mp4)，[合集B：29.30秒](https://zhipijun1996.github.io/map-edit/generation/videos/guided-landing-v2/all-samples.mp4)。两组各有完整单段下载。
- [Pages run39996843819](https://github.com/zhipijun1996/map-edit/actions/runs/39996843819) success。原编辑器检查、26项生成规则测试、37归档分片与9个视频检查在CI通过；静态站仅部署编辑器与generation目录。
- 公网重新下载验证41项归档/manifest，共368067428字节，全部SHA/长度相同。另校验15项站点与视频文件，共3867308字节，无失败。数据在本仓库，未只留外链。
- 公网Chromium实际解码并播放两组合集，下载合集A核对完整SHA，页面错误0。来源在evidence/migration下；自动化不是用户观感反馈。
- 原游戏870份保护原件无漂移。当前观感反馈0、手动试玩0、批准0；新实验的3个技术候选等待观感反馈。

本回执和公网收据作为后续纯资料提交追加，使用skip ci；已部署页面仍绑定上述b3ec6ce字节。原编辑器、旧研究发布、旧失败和源快照保留。CLI不具备可用写凭据时使用已连接GitHub接口，分片/树均核对哈希，没有要求用户重新认证。

方法和下一步见[MIGRATION-AND-NEXT.md](MIGRATION-AND-NEXT.md)。用户按A/B组编号直接聊天反馈即可，不强制操作或填网页。

平原本轮：`generation/videos/plains-v1/`为正常速度原生录像；`results/plains-review-v1/`为3个代表的跨批证据绑定；`archives/plains-generation-v1`包含原始成功/失败及阶段源快照、录像日志和追加原敌人资产。报告`PLAINS-REPORT.md`。原A/B和旧归档保持原样。
