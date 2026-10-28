# Block创意v3：先补真实A4/A5接口，再扩判断关系

推荐下一项 **N11 A4同侧折返：W/W与真实镜像E/E**。原有效A4两版已核原文件SHA；两岸修改都<=32，仍必须新物理。N12 A5原高N口不能贴成grounded侧口，多岸对齐、薄台高度和完整身体外邻都有实际缺口。五案均proposal，0新物理/候选/新族。完整JSON与源SHA见[结构化卡](block-next-ideas-v3.json)。

最新实际Map来源`862b736c491502ae9934265bc7415805b4c122b9`：128与端口公式不变；自有边界门与自有共面支撑并集不等于Map补地形或借外来/动态平台支撑。25活跃/11审阅组不代表11新家族。

| 卡 | 玩家判断 | 当前状态 |
| --- | --- | --- |
| B31-N11 A4反冲入檐袋：同侧折返的Block适配 | 何时放弃上岸支撑、向外开枪刹横移并反向落袋；读身体顶缘净空，而不是只看中心点。 | proposal_existing_rule_adaptation |
| B31-N12 A5一枪两去向：水平侧口与真正第二入向 | 一空中枪选择陡上投资或稍晚平射，落哪处地貌决定后续去向。第四口必须是新输入的真正两向选择，不是旧跌底安全路。 | proposal_body_and_multiport_alignment_gaps |
| B31-N13 停车会推你下船：先留甲板后退余量 | 先走到长甲板前半给后退留空间，再射铃停车、稳住真实相对位置，随后离台。跳离重接的更贵方案也可接受。 | proposal_existing_dock_mount_binding_needed |
| B31-N14 先越过铃，再回身开所选通路 | 选哪个出口、站目标哪一侧发枪；可为更容易路线多花地面预开枪，按真实成本比较。 | proposal_static_vantage_rule_missing |
| B31-N15 先发请求，再穿过将关闭的第一门 | 在A之前就射击起动自己，先完整穿过A，再迎接稍后开放的B；不是站着等门。 | proposal_MISSING_delayed_pair_Cell |

## B31-N11 A4反冲入檐袋：同侧折返的Block适配

同一上岸岩唇伸到凹袋上方，袋内宝箱可见。需要先走到外侧，完整身体低于檐底后才能折回。

一枪刹车再转向，固定岩体上下两面构成折返；不造新桥或新墙。

资源：主见证1枪0跳可以保留；更贵的落底跳射同目标可接受，不用零跳词序强制。

地貌：W/W与真正水平镜像E/E两种来向；岩唇底面和全部底岸保留，端口在真实边缘中心。

奖励：10币留袋内；W奖x可保持35、dock24，collection region不伸入外邻；镜像-35/-24。更新真实岸高与宝箱y并取奖。

恢复：底到袋约228px可研究付费跳射恢复；底到上岸超过单次最大升高，不能假定回A。无需新增资源或Map补台，未验回A仍UNKNOWN。

方向：每接口先A→B。B→A、任意输入状态、真正边界穿越UNKNOWN。镜像新版本必须重新验。

廉价解：
- 不射击直接掉进袋
- 檐上预逆射
- 中心过檐而身体擦岩
- 自然把下袋标E导致入袋轨迹借其外邻
- 安全底面直接走到同奖（N03教训）
- 碰袋底/壁冒充顶面落脚
- 裁袋后只能单帧落脚

具体旧库区别：补旧A4的Map库存与两方向，不增加基础家族。和C07不同在固定檐下的净空/反冲转向，而不是闭新墙接自己。

两个接口需求（均concept_only）：

- N11/W_to_W，bounded_shore_adapter_new_control，bounds [-384, 0, 1408, 768]。
  - A W anchor[-256, 192] / body[-232, 206] / floor224。
  - B W anchor[0, 448] / body[24, 462] / floor480。
  - rules.brake(0), DX=-70 DY28. Upperleft-230→-256 extend26; pocketleft-25→0 trim25.
  - Upper180+28→224 +16; pocket438+28→480 +14. Keep upperbottom308.
  - Real walk dock[-232,206]→translated originalstart[110,206]. Actual B24 vs old35 requiresnewstop, notteleport.

- N11/E_to_E_mirror，bounded_mirror_requires_fresh_physics，bounds [-1024, 0, 1408, 768]。
  - A E anchor[256, 192] / body[232, 206] / floor224。
  - B E anchor[0, 448] / body[-24, 462] / floor480。
  - True mirror rules.brake(1), then DX70 DY28. Upperright230→256 extend26; pocketright25→0 trim25.
  - Upperfloor+16; pocket468+28→480 -16. Mirror aim/axis/actor_x comparisons and all actualsolids, notgravity.
  - Realstart[-110,206], A dock232; B dock-24 vs old-35 shift11.

首测：W先4控制，核完整身体低于原檐底308、实际袋支撑和奖；省枪/早射/落底付费恢复对照。成立后镜像E独立重验。

预算/停止：另注册新2rule/80probe；旧成功与新镜像不共用物理资格。

## B31-N12 A5一枪两去向：水平侧口与真正第二入向

共同起跳处可见近高岸和远下岸；原高口是N标记，不能直接当现Map的grounded dock。

世界不变，真实空中资源与反冲方向/时机的投资决定先落哪岸。额外落地回充方案按实际代价接受。

资源：一原空中枪，无隐形补给；rejoin需新实际跃过上口外邻的策略，不继承旧走落空间保证。

地貌：先真实3侧口；4口另作Block-native把高/中/低层组合成D低东入向到B/C，不能只贴marker。

奖励：上岸12币可见；低路仍有实际后续职责。无奖请求需另外编译，不强制所有路线拿上奖。

恢复：保留底岸。旧reward-rejoin若借外邻则明确拒绝该需求或另验新跳跃策略，不悄悄当作已经返回。

方向：3port A→B/A→C；4port另D→B/D→C必须一起验。未知出D不能编造no_path，若D只有A走落则不算本次4port。

廉价解：
- 原N口假当ground64
- 薄台top下移保bottom得到负高度
- 只算目标中心不查body/outwardcells
- 高口改E后low借其外邻
- oldrejoin出界仍号称继承
- D只是底面走路出口
- 新回充step让基本普通跳同成本代替投资
- 按仰角动作词拒绝同功能有效方案

具体旧库区别：补已有一枪投资家族的Map接口，不增基础家族。和N06互斥实桥不同：本案选择来自人物运动资源。

两个接口需求（均concept_only）：

- N12/three_horizontal，bounded_shore_position_but_body_UNRESOLVED，bounds [-384, 0, 1536, 1024]。
  - A W anchor[-256, 448] / body[-232, 462] / floor480。
  - B E anchor[384, 320] / body[360, 334] / floor352。
  - C E anchor[896, 576] / body[872, 590] / floor608。
  - Use validP50 threeport bc83b6; DX-70 DY72. X editsA26/upper24/lower26; Y-30/+30/-14.
  - Thinupper originalheight24: move wholeledge down30 preservingheight, nottop-onlynegativeheight.
  - HighN→realE opening. Oldhigh/low shiftedtrace0upperEoutside, but oldrejoin16framesoutside. A newfloor-30 roughshift makesoldlow12framesoutside; newcontrols required.

- N12/four_native_low_entry，NEW_BLOCK_NATIVE_REQUIRED，bounds [-256, -128, 1536, 1152]。
  - A W anchor[-128, 448] / body[-104, 462] / floor480。
  - B E anchor[512, 192] / body[488, 206] / floor224。
  - C E anchor[1024, 576] / body[1000, 590] / floor608。
  - D E anchor[1152, 704] / body[1128, 718] / floor736。
  - From validP50 fourport106e4, DY13 gives Y edits+29/-29/+25/-27.
  - AtDX0 X editsA32/upper62/middle64/lower52 exceed32: NEW_BLOCK_NATIVE rule, notbounded.
  - D only counts when actual incomingD→B/C meaningfulchoices are verified on sameworld. OldA→Dwalk/drop not reused as newchallenge.
  - If needC→Breturnstation use real originaloneway primitive, explicitlychangedgeometry. Prove not cheaply bypassingA branches.

首测：优先P50三口新high/low和同一mask；low更晚/更低平射避上口外邻。做不到时explicit needs_design或另注册native高岸，不事后放宽32。

预算/停止：新2rule/80probe且full每精确方向原>=18counter。四口任一入向缺口不静默回三口。

## B31-N13 停车会推你下船：先留甲板后退余量

前方挂铃使停车枪把人物向后推；停住平台并压住门钥匙区是收益，跌出台后缘是运动代价。

同一枪停下世界落点，却将人物相对它推后；玩家读台内剩余裕量而非精确世界x时刻。

资源：按真实ground/airshot、cooldown、接地恢复；不能把groundgun假设为不影响身体。

地貌：长甲板停在可见dock维持出口及返回门；底面不能一路走到奖。需实际同世界返回证明停车状态用途，不是任意requiredpark字段。

奖励：门后奖励可见，真实门状态与回程职责使停台有用途；无该用途就归旧移台练习而非强迫射击。

恢复：后退落底时P保留停位，从原控制位再登台。若安全地面预停同成本到奖，按A2/D02/N03失败反馈拒绝或折叠。

方向：首A→B及必要同世界B→A；镜像第二输入方向重验。不可将dynamiccarrier/外来地面放入静态ownsupportunion伪造承载。

廉价解：
- 岸上预停后不用乘台
- 不停车趁Area短窗过门且回来同样可用
- 字段park代替有用世界后果
- 只看末帧支持掩盖中段跌台
- 把ground平路避掉原运动代价

具体旧库区别：具体判断是停车收益附带的甲板相对后退预算；不同当前C01/C07/N04/N06/N10。仍可能是A2/G13有用组合，不因大台或新字段增家族。

两个接口需求（均concept_only）：

- N13/east_boat，newrule_existingCells，bounds [0, 0, 1664, 1152]。
  - A W anchor[0, 576] / body[24, 590] / floor608。
  - B E anchor[1664, 448] / body[1640, 462] / floor480。
  - P[320,618]→[960,618], size320×20; mountedreceiver offset[200,-80]. DockArea uses actual wholebody overlap, not inventedcentrecondition.
  - Gate/park necessity remains a counterquestion; firstbodydeceleration may not require uniquejumpsequence.

- N13/west_mirror，newmirror_rule，bounds [0, 0, 1664, 1152]。
  - A E anchor[1664, 576] / body[1640, 590] / floor608。
  - B W anchor[0, 448] / body[24, 462] / floor480。
  - P[1344,618]→[704,618], receiveroffset[-200,-80]. Freshphysics includingrealbodycarry.

首测：同一停位前/中/后台真实差异，记录supporttimeline；再预停/不停台强counter。没有更丰富后果则不硬判必须空中。

预算/停止：独立新2rule/80probe；旧dockconsumer薄接mount，不重写载人/物理。

## B31-N14 先越过铃，再回身开所选通路

M正面看目标在出口那边，直接向它开枪会把自己推向反侧。先掠过铃位置再回头射，同枪才能开路并继续朝所选出口走。

主动取得有利射位把世界开路与身体前进合并。不是从同一起点改瞄准词，先经过目标再反身的空间过程可见。

资源：M真实回充后一枚空中枪；groundpreopen+freeairshot若可行是额外枪策略，不以必须air命中白名单排除。

地貌：M两侧铃在台外下方，低入口先到共同M。侧向观察能看清铃与对应门，高出口不同地域；不新增双台相位。

奖励：左右均真实高向，等额货币或无奖需另编；去掉奖仍有路线差异。

恢复：不利侧早射落回原M/内部回收，timer保留；可再准备，不把错误枪变软锁。

方向：3port A→B/A→C；4port加D→B/D→C同初态另验，余向UNKNOWN。

廉价解：
- 不用越铃同一枪轻易去所选口则观察冗余
- 未开门可直越顶/底
- groundpreopen同时更省枪跳时间支配名义
- 只有门铃连线装饰无真实关联
- 为另一个入口换新初态冒充共同选择

具体旧库区别：判断是先把自己移到目标有利一侧，让反身射同时开路和前进；不是支撑交换/新墙刹车/同门回收/靶串联。可归G09fork组合，独立新族UNKNOWN。

两个接口需求（均concept_only）：

- N14/three，newstaticvantage_rule，bounds [0, 0, 1024, 1024]。
  - A W anchor[0, 704] / body[24, 718] / floor736。
  - B W anchor[0, 320] / body[24, 334] / floor352。
  - C E anchor[1024, 320] / body[1000, 334] / floor352。
  - Lbell[384,640], Rbell[640,640]; independenttimeddoors. Favourableair positions around[352,500]/[672,500]conceptonly.

- N14/four，fourport_only_after_secondinput_evidence，bounds [0, 0, 1024, 1024]。
  - A W anchor[0, 704] / body[24, 718] / floor736。
  - B W anchor[0, 320] / body[24, 334] / floor352。
  - C E anchor[1024, 320] / body[1000, 334] / floor352。
  - D E anchor[1024, 704] / body[1000, 718] / floor736。
  - Bothincomingactors must actuallyreachsameM, sameinitialdoors/targets, thenbothchoices.

首测：M单侧比较铃前/后真实枪向与body+门通过。短距100–180px靶利于6deg容错；有效后才另一出口/另一个输入。

预算/停止：独立新2rule/80probe；若只剩D01基本位移，承认冗余，不加刺补趣味。

## B31-N15 先发请求，再穿过将关闭的第一门

近A开/远B闭，命中近身铃后先有可读预响，再延迟一关一开。未来的世界变化允许身体先行。

射击立即作用人物，真实命中受生命期约束的请求稍后原子作用世界；比C02先过A后发射改变行动顺序。

资源：延迟不返枪，不重复commit；实际原消耗/落地恢复。

地貌：门距和反冲廊给A身体清空到B到达的宽时间区间。不要以远小靶延迟代替Cell：6deg瞄准会失稳。

奖励：B后奖励可见，pending预响必须清楚；没有反馈不放在盲试主路。

恢复：起迟被A挡或先到B时落原底岸回枪；提交时身体夹在任何将关门内仍整笔拒绝，不强关。

方向：首A→B；回程初态/pending/资源不同全UNKNOWN。第二空间升高128，不能只换timer标题。

廉价解：
- 等delay后普通越两门
- 安全底面平走到奖（N03）
- 其实先过A才射退化C02
- 无Cell静默换成shortdoor/远铃
- 多请求/死亡后旧pending仍提交
- 只查中心夹人

具体旧库区别：判断未来响应与身体先行，动作在首门前发起；确实缺新Cell，不从字段名字宣称已实现。

两个接口需求（均concept_only）：

- N15/flat，NEW_DELAY_CELL_REQUIRED，bounds [0, 0, 1024, 896]。
  - A W anchor[0, 448] / body[24, 462] / floor480。
  - B E anchor[1024, 448] / body[1000, 462] / floor480。
  - Bell[160,512], missingdelay candidate .15/.25/.35s; allactualflight/body clear timings unresolved.

- N15/staggered，NEW_DELAY_CELL_REQUIRED，bounds [0, 0, 1152, 1024]。
  - A W anchor[0, 576] / body[24, 590] / floor608。
  - B E anchor[1152, 448] / body[1128, 462] / floor480。
  - Bell[224,640]; missingdelay .2/.3/.4s domain. Pendingmustbind health/session/lifetime epoch; repeatedshots notunlimitedqueue; commit originalfullbody atomicgate test.

首测：先Cell重复请求/取消/死亡/session/epoch/原防夹，证明delay连续一致；Module需actual Aclear<commit<Bentry多帧窗口。

预算/停止：Cell和Module独立预注册，不借旧pair117或N03 Cell8例签新行为。

## 对齐与身体审计

A4 W：DX-70/DY28，上岸180→208→224(+16)，袋438→466→480(+14)；左边扩26/裁25。镜像v1右边扩26/裁25，袋顶-16。上岸底保持308。W入袋不贴E出口，防止身体从外邻进入；镜像不是旧反向证据。

原A5 fork0三岸Y可DY72对齐，fork1仅DY26对齐，但水平W/E组合最优最大岸改动仍超过32，具体表在JSON。P50三口扩岸可把X调整控制26内，然而24高薄台向下30必须整块移，不准保持旧底而变负高度。

旧完整24×36轨迹刚性平移预筛：upperW使high26帧碰外邻；upperE使旧high/low0，但rejoin16帧出界。粗略把A新岸上移30后low12帧借upperE外邻。这不是新物理通过：低路需新控制或明确新native上岸，不准继承旧rejoin。旧四口D只有走落底，必须真实D入两路线后才算四口。

其余三卡有各自不同判断：甲板后退余量、取得有利反身射位、身体先行/延迟世界。N15明确缺Cell，不能替换成普通shortdoor假称实现。所有新scope先独立注册有限预算，旧失败保留；不是延长N02/N03旧上限。
