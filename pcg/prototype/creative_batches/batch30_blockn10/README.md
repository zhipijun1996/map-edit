# N10 首周期：失败原件，未入库

原B31-N10使用原timed/permanent ShotLatch，实测近铃开门后接收器layer0，关门复位layer8。三组机制对照3/3通过；初次把固定实验的entry/exit设成同一点，被原Module定义0帧拒绝3例，新fixture只分离定义标记后重跑，失败原件没有覆盖。

2条Module生成规则合计63个Godot输入，其中60例实际跑帧，3例0帧拒绝。第一版clean2/2、20counter0反驳，但mild6/6、moderate2/6；第二版修改深腔、M接收与B下行地貌，clean2/2、新20counter0反驳，尚未跑该版本noise/full/held。

核心缺口是M侧真正闭门时，近门本身挡住了到主铃的弹丸：旧连续迟射3枪原件实际impact[962.97,673]在门上，没有重开Near或打开Far。不能因独立接收器机制正确或clean成功，就宣称完整恢复可用。首周期正式封为needs_design、0Module，见`cycle-seal-v1.json`。

根任务另行授权最后恢复修订 `../batch30_blockn10_repair/`，仅用原return_access扩展，保留本周期全部失败，且旧63+新17输入谱系封顶80。新源和全部证据重新绑定，不能以改名替代原失败，也不继承旧世界counter结果。

20个旧counter有限没有发现同目标反驳，不代表无绕法。旧late-M模板插在向左axis之后，实际边等边走，不能声称已经测到站M长等；新修订路径已修正模板供根full真实执行。新接口通过之前，不提供可入库生产内容。原件目录为`pcg/results/batch30-blockn10-*`，两份JS/Python0physics预检问题与原输入亦保留。
