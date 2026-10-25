# 20种新玩法 Module

本轮主交付20种不同因果关系；旧六家族不计入。全部为真实Godot技术候选，人工趣味/试玩/生产认可待评。通用接缝与整图UNKNOWN。

[观感离线包（约29 MB）](../creative20-review-v1.zip) · [全部原速节选](all.mp4) · [墙面跳跃](movement.mp4) · [钩索](grapple.mp4) · [人物与世界](world.mp4) · [动态空间](dynamic.mp4)

节选只在模块之间剪切，并截去稳定领取后的尾部等待；完整原生视频逐项保留。M12完整原片安全完成，但32处support_id差异使严格比较失败，标记review-only。其余19片完整严格比较通过。

|编号|玩法关系|完整录像|标准文档|独立留出|
|---|---|---|---|---|
|M01|保留二跳越低檐：低檐限制提前上升，保留二跳到开阔处再用。|[MP4](videos/M01.mp4)|[JSON](modules/M01.mapnote.json) / [SVG](modules/M01.svg)|23/25|
|M02|踏空贴墙反蹬：主动踏空获得墙面接触，再反蹬回高处；此样品没有普通跳跃。|[MP4](videos/M02.mp4)|[JSON](modules/M02.mapnote.json) / [SVG](modules/M02.svg)|25/25|
|M03|双壁绕刺越顶：利用对侧高墙换接触点，越过首墙的带刺段。|[MP4](videos/M03.mp4)|[JSON](modules/M03.mapnote.json) / [SVG](modules/M03.svg)|25/25|
|M04|空中挂停主动跃出：先挂停形成空中观察点，再主动选择离挂时机。|[MP4](videos/M04.mp4)|[JSON](modules/M04.mapnote.json) / [SVG](modules/M04.svg)|24/25|
|M05|触环恢复二跳：先花掉二跳够环，再靠真实接触恢复二跳，跨向高岸。|[MP4](videos/M05.mp4)|[JSON](modules/M05.mapnote.json) / [SVG](modules/M05.svg)|24/25|
|M06|自动弹钩后改轨：弹钩自动抛出角色，同一次接触收益制造必须处理的新飞行。|[MP4](videos/M06.mp4)|[JSON](modules/M06.mapnote.json) / [SVG](modules/M06.svg)|25/25|
|M07|借敌人真实发射开短门：维持视线诱使原生敌人发射，短门随攻击提交打开；随后避开真实弹丸。|[MP4](videos/M07.mp4)|[JSON](modules/M07.mapnote.json) / [SVG](modules/M07.svg)|36/36|
|M08|跟锯穿廊掉层：追随移动锯释放的空间，掉层离开它的返程轨道。|[MP4](videos/M08.mp4)|[JSON](modules/M08.mapnote.json) / [SVG](modules/M08.svg)|36/36|
|M09|清敌身露射铃：敌人身体吸收弹丸；清掉它才能露出真正的射铃通路。|[MP4](videos/M09.mp4)|[JSON](modules/M09.mapnote.json) / [SVG](modules/M09.svg)|36/36|
|M10|探身开锁再折返：从低处穿过遮挡，探身击中远铃，再折返进入原先关闭的左门。|[MP4](videos/M10.mp4)|[JSON](modules/M10.mapnote.json) / [SVG](modules/M10.svg)|25/25|
|M11|活敌压区维持门：击退活敌使其压住感应区，借持续占区维持门。|[MP4](videos/M11.mp4)|[JSON](modules/M11.mapnote.json) / [SVG](modules/M11.svg)|34/36|
|M12|撤桥自坠：射击打开脚下的桥，收益同时撤掉自身支撑并承诺下坠。|[MP4](videos/M12.mp4)|[JSON](modules/M12.mapnote.json) / [SVG](modules/M12.svg)|25/25|
|M13|击退腾出落位：敌人挤占真实身体落位间隙；击退或清除它才有安全着陆空间。|[MP4](videos/M13.mp4)|[JSON](modules/M13.mapnote.json) / [SVG](modules/M13.svg)|36/36|
|M14|反向击铃借墙折返：反向射铃将角色推向侧墙，再借墙折返穿门。|[MP4](videos/M14.mp4)|[JSON](modules/M14.mapnote.json) / [SVG](modules/M14.svg)|25/25|
|M15|周期危险择时离挂：挂点给观察机会，自主周期危险决定离挂与落点窗口。|[MP4](videos/M15.mp4)|[JSON](modules/M15.mapnote.json) / [SVG](modules/M15.svg)|35/36|
|M16|离台避险重接同台：载台驶向危险时先离台避难，再预测并重新截获同一载台。|[MP4](videos/M16.mp4)|[JSON](modules/M16.mapnote.json) / [SVG](modules/M16.svg)|36/36|
|M17|弹丸穿运动射线窗：角色不乘挡板，预测移动遮挡为弹丸留下的真实射线窗。|[MP4](videos/M17.mp4)|[JSON](modules/M17.mapnote.json) / [SVG](modules/M17.svg)|34/36|
|M18|缓降高度预算择窗：真实缓降不断损失发射高度，同时选择移动锯的通过窗口。|[MP4](videos/M18.mp4)|[JSON](modules/M18.mapnote.json) / [SVG](modules/M18.svg)|36/36|
|M19|可见双目标有序事务：两个目标同时可见可射，但原机关的操作顺序不可交换。|[MP4](videos/M19.mp4)|[JSON](modules/M19.mapnote.json) / [SVG](modules/M19.svg)|23/25|
|M20|先压门再取回载台：同一平台先占区作开门钥匙，再释放作运输支撑；两种用途不能同时保留。|[MP4](videos/M20.mp4)|[JSON](modules/M20.mapnote.json) / [SVG](modules/M20.svg)|35/36|

## 试玩与复现

在仓库根恢复运行时和本批原件，使用官方Godot4.7.2：

需要Python 3.11+、Node.js及官方Godot4.7.2。Linux首次检出先安装引擎（已有相同SHA则跳过下载）：

```sh
mkdir -p pcg/toolchain
curl --fail -L -o pcg/toolchain/godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
printf 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4  pcg/toolchain/godot.zip\n' | sha256sum -c -
python3 -m zipfile -e pcg/toolchain/godot.zip pcg/toolchain
chmod +x pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64
```

```sh
python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract
python3 pcg/tools/restore_archive.py content-workshop-creative20-v1 --extract
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 --headless --editor --path pcg/prototype/godot --quit
python3 -m pcg.prototype.creative_batches.catalog_v4 --list
python3 -m pcg.prototype.creative_batches.catalog_v4 --play 1
```

A/D移动、空格跳、左键射击、E/右键钩索；仅样品声明的能力生效。Retry重新开始，Replay播放实际见证。各自有Cell需要catalog指定的真实消费者场景。命令不会修改正式主游戏。

[完整报告](../../../docs/l4-mapgen/content-workshop-creative20-v1.md) · [模型创意skill](../../../.agents/skills/pcg-creative-producer/SKILL.md) · [完整索引](manifest.json)
