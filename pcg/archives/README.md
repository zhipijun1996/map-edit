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

本轮迁移补充归档 `module-foundation-migration-v2` 使用内容去重与直接分片写入，
可用 `python3 pcg/tools/restore_archive.py module-foundation-migration-v2 --verify-parts-only`
逐项验证，不需在磁盘再拼一份完整 ZIP。当前 `modules/` 与 `modules-recycle/`
由 Git 直接保存；该归档保存迁移的真实 raw、失败、冻结源与暂存输入字节镜像。

本轮的31份 AVI 原始中间视频另以**无损 XZ 字节镜像**保留，包含在
`results/foundation-migration-capture-storage-v1/`；不是重新编码的视频。
从归档恢复该目录后，按索引原路径执行
`python3 -m pcg.migration.capture_storage --restore 'generation/原路径/movie.avi'`
可恢复原大小与 SHA 完全一致的文件。最终 MP4、轨迹和原物理证据未替换。
