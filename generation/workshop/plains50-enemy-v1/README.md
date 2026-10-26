# Plains50：敌人与世界关系的8个平原候选

4个已有动作关系 × 2个新空间需求。仅移动、普通单跳、反冲；不计新玩法家族。全部为双端口entry→exit技术候选，反向/通用进场/连续失败恢复/接缝仍UNKNOWN。

原Godot共972例（28小试、190廉价反例、其余原小筛/校准/留出）。校准280/288、独立留出284/288目的通过，8版本均过原regular门槛；不是总体通关率。4段原生1×60Hz影片共558帧严格全字段一致。

|编号|配方与空间接口|标准JSON|代表影片|
|---|---|---|---|
|E01|引敌开门 · 近接口|[JSON](modules/generated-cbfbd55d9941d468f7123b864943a40700c5ffe0afbcb4e0d3749a1339a1c2e3.mapnote.json)|[MP4](videos/enemy-attack-relay.mp4)|
|E02|引敌开门 · 远/低接口|[JSON](modules/generated-011d0a163822daaeea61e2280dbe4b26f7f48fa38d57ac30d06110da0634723b.mapnote.json)|同组影片只解释关系，非本精确版本录像|
|E03|清除吸弹射界 · 近接口|[JSON](modules/generated-b31dfc309d80b084183d671e23510cc44e67e5c8994c5b409bc4a5642efc0b4b.mapnote.json)|[MP4](videos/enemy-clear-sightline.mp4)|
|E04|清除吸弹射界 · 远/低接口|[JSON](modules/generated-374a556611974c992e90736527f13474d8a2249a7f828073f50a87d864a383af.mapnote.json)|同组影片只解释关系，非本精确版本录像|
|E05|保留活体供电 · 近接口|[JSON](modules/generated-446733d0de7e584a952fdafe38b916bd8d170cf45df9175b541779dd8dfdee2a.mapnote.json)|[MP4](videos/enemy-sensor-hold.mp4)|
|E06|保留活体供电 · 远/低接口|[JSON](modules/generated-f199f9078442c65e15a486b175f9aa04a8c3dc14af0249485ad42d37e99620f3.mapnote.json)|同组影片只解释关系，非本精确版本录像|
|E07|击退腾出落位 · 近接口|[JSON](modules/generated-cb0cb5e82792a77296d01c80f912b096af3572338347db4ad998bf123623af9a.mapnote.json)|[MP4](videos/enemy-displace-landing.mp4)|
|E08|击退腾出落位 · 远/低接口|[JSON](modules/generated-e69e0223a2511f52732f1744945bfff3e8f426fe6203804ac01fbe19b6e04808.mapnote.json)|同组影片只解释关系，非本精确版本录像|

人工观感、实际试玩、生产认可均未进行。模型只抽查每段一帧，没有宣称完整视频观感审核。

可玩入口（先恢复本轮原始case和原Godot运行环境，从仓库根执行）：

```sh
python3 -m pcg.prototype.creative_batches.plains50_enemy.play_v1 --recipe attack-relay --interface 0
python3 -m pcg.prototype.creative_batches.plains50_enemy.play_v1 --recipe clear-sightline --interface 1
```

其余配方名：`live-enemy-sensor`、`displace-landing`。原生消费者安装原AttackRelay/Occupancy薄组件，不使用替代物理。

[完整版本/来源/复用清单](manifest.json) · [新进程8次精确检索与8个错误出口请求拒绝](retrieval.json) · [配方源码说明](../../../pcg/prototype/creative_batches/plains50_enemy/README.md)
