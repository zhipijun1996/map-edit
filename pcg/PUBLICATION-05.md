# PCG-FACTORY-05 发布回执

- [盲评试玩](https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/b69a52727616/) · [生产报告](https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/b69a52727616/report.html) · [版本绑定的网页质量档案](https://zhipijun1996.github.io/gunman-rush-previews/previews/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/b69a52727616/catalog.json)。
- 研究源 `7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6`；原游戏基线 `12f6cb006d7119598e3235f4ca4f7323e4c9d092`，Godot4.7.2。
- 试玩PCK216772字节，SHA256 `b69a52727616d877b776baf808cfac5ed604b51e8d3ca9d44421e9a42d39d315`。原68MB base/官方JS-WASM继续按不可变URL和完整SHA复用。
- 网页catalog SHA256 `89c6b3a34478b7efcf271ba4225b6cc6249562d68d14744e94cb02b0fe405e90`，另绑定表现源，反馈导入用这个catalog；技术目录与原物理证据未改。
- 数据commit `ea11a1844225bd91ec66ee4e354a43aeb2c992ed`；[完整数据清单](https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/ea11a1844225bd91ec66ee4e354a43aeb2c992ed/artifacts/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/manifest.json)。合并ZIP28872993字节，SHA256 `632c7c40f708bd26b0c9387b32e4df69777273a74d4e2de550c66506d8bf4435`。已从公网重新下载3分片，逐片/整体SHA、ZIP CRC和4111文件SHA全过，重复路径0。运行源/所有本轮原始失败保留；游戏素材与官方引擎按固定依赖恢复。
- 部署commit `182cf0b1d62e8750fed998daa7dc77340dc672a5`，[Pages run39987039629](https://github.com/zhipijun1996/gunman-rush-previews/actions/runs/39987039629) success。原验证器在本地及CI均过，site940794105字节，未提高900MiB guard；1046份旧site文件哈希未改，仅首页追加链接。
- 公网22项完整字节校验全过，共108338517字节，含新版本文件和3个复用运行依赖。工程测试21项通过，870原件无漂移，原游戏工作区clean。

## 下载与归档

连接器的请求体上限16MiB，完整数据用3个10MiB以内分片保存在仓库 `artifacts/`，不占Pages站点预算。下载[合并脚本](https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/ea11a1844225bd91ec66ee4e354a43aeb2c992ed/artifacts/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/download.py)，执行：

```sh
python3 download.py --revision ea11a1844225bd91ec66ee4e354a43aeb2c992ed \
  --manifest-path artifacts/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/manifest.json
```

新的完整账本是 `FACTORY-ARCHIVE-FILES.json`，研究源标识为 `FACTORY-SOURCE-COMMIT.txt`。包内沿用的根ARCHIVE-FILES.json为旧轮历史账本，不应拿来解释新包；当前新账本逐项已复算。首次本地单文件打包尝试/传输失败仍留在delivery，未作为最终数据发布。

CLI凭据返回401，改用已连接GitHub接口上传，未要求重新认证。逐blob SHA及整棵tree与本地Git index一致，最后使用expected_sha及非force更新main；旧历史未删。API创建的commit按原始author/committer时区恢复到本地对象并核对相同SHA，托管工作区clean。

## 验收范围

1002次生产物理运行、独立父代对照36次及隔离反馈诊断1次的证据在数据包内。v2为同批6候选的严格regular派生：4待真人、2返工，人评0，批准0。网页与软件反馈通道可用，不代表已有真实人评或好玩成品库。诊断子代1/1不是完整留出准入。

最终本地和公网均通过5次真实输入回放（覆盖4模块，0号重复一次）、实际键盘操作、仅Replay不能评分、合成反馈导出/正常导入拒绝/测试store隔离、重载保留草稿，页面与引擎错误0。公网证据为 `delivery/factory-v1/browser-public-v3/browser.json`；真人0、批准0。

首次公网测试已实际加载、回放、操作并导出，随后测试工具的独立Node请求客户端选用不可达IPv6而失败；第二次使用浏览器解析对象回传Python，使JSON浮点整数类型变化而触发catalog校验。原失败均保留。最终改为页面内同源fetch原始文本、在Python解析，和产品相同网络路径且保留原文件类型，不改网页/PCK/物理/门槛。完整数据清单的原始字节此前已经逐SHA通过；这两项为测试工具修复，修订源码与失败/成功收据另外归档。

[补充公网收据与修订测试源码](https://raw.githubusercontent.com/zhipijun1996/gunman-rush-previews/af4e015e0cbf02f4caad00cb001f2979c009c6bc/artifacts/PCG-FACTORY-05/7c26d7193ad1eef1fc4d56cd44ff3d8c8d6eb1c6/post-publication/public-receipts.zip)：1505918字节，SHA256 `ef4830ea4efaf357bb68b45b45f58ae4fe1a260f220ed63e55dbe95f289d7544`，公网重新下载后26文件SHA及CRC通过。仅向非site目录追加收据，commit `af4e015e0cbf02f4caad00cb001f2979c009c6bc` 使用skip ci，原Pages部署仍为上述182cf0b；页面字节没有变化。重跑公网检查请用补充包内的测试工具，生产代码与物理源仍以主包冻结版本为准。
