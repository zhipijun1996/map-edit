# 研究原件归档

各目录manifest.json记录分片、完整ZIP SHA、原件数与数据范围。`_work/`是本地重组ZIP缓存，未提交。每片最大10MiB，避免GitHub单文件与连接器请求体限制；没有删失败来压体积。

恢复示例：

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py research-results-v1 --extract --prefix results/factory-production-v1/
python3 pcg/tools/restore_archive.py guided-landing-v1 --extract
```

不加--extract会校验全部条目。恢复不会覆盖不同内容的现有文件。ZIP内PCG-ARCHIVE-INDEX.json是本次归档的逐文件账本。

旧物理基线和编辑器库版本不同，归档仅保存历史身份。原引擎/资产许可不因迁移改变，见pcg/prototype/godot中的来源与许可清单。原生AVI/Godot导入缓存可由输入与固定工具链重建，不作为主仓库资产重复上传；最终MP4、输入/输出及失败证据均保留。

实际形状空间搜索v1分三份：`shape-search-calibration-v1`保留所有校准/失败；`shape-search-source-v1`保留评估/旧布局/反例完整冻结源；`shape-search-results-v1`保留全部实际结果、PCK、发布记录与媒体。媒体恢复到`pcg/results/shape-search-review-payload-v1/shape-search-v1`，需要时复制到`generation/maps/shape-search-v1`；不覆盖不同内容。详见`docs/l4-mapgen/real-shape-search-v1.md`。
