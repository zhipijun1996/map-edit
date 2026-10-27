# N06 第二接口：东西低入口的真正四口选择

这是冻结 `batch30_blockn06_repair` 的**新四Port接口需求适配**，不重试旧 N06 的80次谱系，不计新玩法家族，也不把低D当安全出口。只验证同一套实体/同一原初态的 A/D→B/C 四个有向对，其余8对保持 UNKNOWN。

1280×1152，完整连通10×9 Block128所有权；所有Port在边界cell中心，内部人体dock另记：A W[0,704]→[24,718]，D E[1280,704]→[1256,718]，B W[0,64]→[24,78]，C E[1280,64]→[1256,78]。相应floor分别736/736/96/96。没有默认外框或接缝补台。

新世界只把M由[480,608,256,64]右扩64为[480,608,320,64]，并新增D岸[1024,736,256,64]。铃仍[800,560]；两桥、两小岸、全部原底岸和恢复阶都保留。原paired v3的弹丸、原子互斥交换、完整身体防夹、角色和回枪机制未改。四条路线共享左桥实体/右桥空的原初态，绝不依入口换phase。

A保留原selected c1，并按新几何重验。D从1256实走到1055，向左跳并向右下射空，真实落M回枪，再选保左桥往B或射铃换右桥往C。不是仅在图上添口。四条冻结clean均3枪4跳；D第一枪不瞄铃且实际首次M前无交换。之后真实落所选桥，再上原小岸和高出口，完整身体扫掠都在预冻结所有权内。

固定新周期2规则/80probe，目前只用1规则/70实际：6clean全通过（A固定c1，D每目标c0/c1），按预注册实际M+对应桥完整24px身体最小左右余量最大、同分小index选D c1：54.829px优于c0 51.462，A c1为54.833px。全部4×c1在noise前冻结。48noise中47通过：所有mild6/6，moderate只有A→C5/6，其余6/6；沿用原regular .85/.65，1次错过射铃失败原样保留。16强反例同世界0设计反驳；每精确route另有27个完整反例给原full管线。有限反例不证明不存在其他路。

冻结API和复现命令：

```sh
python3 -m pcg.prototype.creative_batches.batch30_runtime.produce_v3 --name NEW_IMMUTABLE_NAME --rules pcg.prototype.creative_batches.batch30_blockn06_fourport.api_v1 --index 19 --interfaces 0
```

原GD语法、最新Block-v2/显式route元数据、4×27 counter精确身份/几何/所有权绑定、原static以及Block JS标准导出全部0physics预检通过，导出1份四口标准文档。root已接手完整cal/held；**小筛不是入库，本文不预先宣称技术通过**。`handoff-v1.json`冻结实际执行依赖SHA；`readonly-causal-audit-v1.json`绑定4clean的真实进入/M/桥/出口资源、首枪与交换时序，0新物理。

标准图/Module文档、版本、库持久化由原producer/exporter/store生成。本需求为显式派生接口，未冒称消费了真实B整图请求；API对所有12对互通、高入口、资源/奖励变化和其他空间请求返回具体needs_design。没有新Cell/第二Harness/Mapgen。B尚需paired v3消费安装；原底岸保留不代表新D恢复、通用回程或边界穿越已经验证。

原件 `pcg/results/workshop-batch30-blockn06-four-{clean-v1,noise-v1,counters-v1,zero-preflight-v1}/`，含全部输入/源快照/真实gzip结果及SHA。旧D c0探针有一个复制label仍写.75而可执行计划实际.7；单独元数据澄清，原raw和选择不改，selected c1及full参数均准确。剩10probe未花，人工观感/真人试玩/生产批准 UNKNOWN。
