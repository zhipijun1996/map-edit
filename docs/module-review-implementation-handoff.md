# 已确认设计的独立实现会话

当前设计会话持续处理图文与网页反馈。用户允许另开Codex会话，并行实现已确认保留的版本。这里的允许实现不等于技术通过或生产认可。

实现入口：`feedback/manual-review/implementation-handoff-v1.json`。当前为01–07、10、12、17、23、25、27、28及30，共15项。逐项核对设计文件SHA256、designVersion与人工保留记录，不能使用最新目录名推断批准，不能自动追随随后网页的设计变动。32/34/35仍在设计讨论；08、09、11、13、14、15、16、18、19、20、21、22、24、26、29、31、33设计废弃，均不属于本轮实现。

独立分支示例：

```sh
git fetch origin
git worktree add -b content/approved-designs-batch001 ../map-edit-approved-implementation origin/main
```

先读 `AGENTS.md`、`MAP_FOUNDATION.md`、`MAP_GENERATION_GUIDE.md`、`pcg/WORKSPACE.md`、`pcg/OUTPUT-CONTRACT.md`，再按工作内容读取现有迁移、物理合同与视频审阅skill。复用现有导出器、真实Godot Harness和质量门槛。设计JSON只描述目标，不能直接改schema/添加generationContract就宣称实现完成。已有源Module位置与内容版本在每项sourceModule中，先核实际代码与现存证据，再修改，不重复建物理系统。

逐项在清单outputDirectory隔离实现真实地貌、怪物、机关、奖励、端口及动作参数，保留失败和修订记录。01必须考虑四口12个不同端口间有向关系；04只因增加D口不自动获得全互通认证。全部遵守128px Block尺寸与真实外边中心Port，验证身体净空、稳定到岸、真实资源/恢复、反例、时机扰动、声明的回程与必要接缝。无法满足时记录具体设计冲突，不擅自添加冗余安全台或改变已确认玩法。

已有反馈001的归档及复现入口见 `pcg/manual_review/README.md`。旧版实测、截图、设计线条及本地未提交草稿都不能当作目标设计版的通过证据。实现源码、几何、参数和路线变化后重新绑定版本与证据。当前会话未提交的反馈002实现草稿不能假定在另一环境可用。

结果写入 `feedback/manual-review/implementation-results/<batch-id>/`：每项记录designVersion、implementationVersion、源码绑定、验证范围、PASS/FAIL/UNKNOWN、复现命令和可玩包/短视频。先完成一项即可报告，保持候选、技术认证、人工试玩和生产认可分开。需修改设计时回报本会话，不能覆盖设计稿来掩盖实现冲突。

实现PR只包含候选实现、参数与验证材料，不修改 `generation/manual-review/designs/`、审阅队列、网页或人工意见。正式库的更新按现有归档和合同流程提出可审阅变更；不将人工认可设计解释为人工已试玩或生产批准。Git合并由单一集成人串行完成，不能覆盖另一分支文件。

可给新Codex会话的提示词：

> 你负责已确认Module设计的实现。先读取最新main的AGENTS.md、docs/module-review-implementation-handoff.md和feedback/manual-review/implementation-handoff-v1.json。在独立分支/worktree仅实现清单中01–07、10、12、17、23、25、27、28及30的精确确认版本，补全真实参数，复用现有Godot Harness验证并提交可复现证据。不改图文设计网页，不处理清单外的Module，不恢复旧批量任务；发现设计冲突先记录反馈，不悄悄改玩法。
