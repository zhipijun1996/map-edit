# 离线 Module Factory

这是独立研究生产器，不修改正式游戏模块池。完整说明见仓库根 `FACTORY-REPORT.md`。

核心入口：

```sh
python3 -m prototype.factory.core.producer --name fresh-run --tier regular
python3 -m prototype.factory.build_review --run fresh-run --out delivery/fresh-review
python3 -m unittest discover -s prototype/factory/tests -v
```

结果目录必须不存在，失败输入/完整输出/源快照均保留。Godot输出逐批gzip归档，`batches.json`记录未压缩原字节SHA与长度。650余份实际文本运行源另存；素材与引擎按受保护清单/固定版本恢复。

`catalog.json`是技术质量档案，`review_cases.json`是待评真实输入见证，`archive_history.json`是可行/不可行档案插入和更新史。当前无需LLM/API或神经网络训练。

人评导入/返工见 `feedback_cli.py --help` 和根报告。提交不自动上传、不自动批准。生产器拒绝合成返工任务；`test_feedback_loop.py`仅可在明确test_only诊断下检查合成链路，不能晋升候选。

重新生成前先选择regular或precision_review。最低12扰动样本门槛不随pilot预算降低；少测只会得到证据不足。已通过单模块不表示已通过Macro/Map、正式游戏或设备准入。
