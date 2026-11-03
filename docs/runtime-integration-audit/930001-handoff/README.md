# 930001 定向交接：机制覆盖、M35/M01、M24、1.1.1准备

从 PR78 head **`2ec243842567a56a49b84fc93ce4aa750b11ff5f`** 顺序追加，沿用 `audit/runtime-integration-readiness-20261103` 分支；main比较点仍是 `9b712fe814ef228b368c0eb9adf660e39de29e37`。不重做全面审计、不改 Module/玩家/经济、无新生成器/装载器、不合并PR77、不发包。审计附件只是冻结数据摘录，不进入 `modules/` 生产集合。

## 输入锁与差异边界

| 输入 | 精确提交 / 身份 |
|---|---|
| 消费的模块包 | **1.1.0**，ZIP SHA `5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723`，来源02b5cb53，不取main同名版本 |
| map-gen PR3 | head `93c5221a9708d079c2864f3c14b415e81bb5de07`；0.3.0算法交付源508b558e；使用提交内 success冻结输出和validation-930001实际结果 |
| Python冻结地图 | `reference_package/fixtures/success/map.json`，SHA `2c47b81e754e3500df1c5e9723b19b1bc99fcd20751d8ae05fd2af55a3ebc6c0`，map_id=`map-ffc781684ea67dc383a84203` |
| GDScript实际地图 | `validation/godot-candidate-0.3.0/replay-precision/validation-930001/actual.json.gz`内result，map_id=`map-9a5c671e93a6cbe2a11dde3e`，implementation=`mapgen/gdscript-candidate-0.3.0` |
| 主游戏PR127 | **`e7d703f47c97f09bd5c5d48e24f0a400c958ad40`**；其受证运行/导出源F=67da2f35，本轮不把旧切片证据签成下批适配证据 |
| 未来候选1.1.1 | 仅用于迁移差异检查，SHA `a806f8feb10e8a10f20014913afba49e9036be21d33c00618cfc86367ac993c6`；本图输入锁不变 |

完整43份只读输入的路径、Git blob、SHA和提交见 [frozen-input-lock.json](../../../evidence/runtime-integration-930001/frozen-input-lock.json)。GitHub连接器读取PR/交接资料；完整tree读取遇到连接中断后，批量原件用CLI/raw固定提交下载并核Git blob，未拉取/修改两个下游工作树。

**实际核对结果**：46实例、55连接、20个精确模块版本；Python冻结与0.3.0实际content_store全部相等，map除 `map_id/generator` 外全部相等，PR127携带的map字节也与Python冻结文件相同。身份差异按设计保留，不能沿用旧恢复hash。来源证明与完整版本在 [frozen-checks.json](../../../evidence/runtime-integration-930001/frozen-checks.json)。

## 交接入口

- [机制覆盖表](coverage.md)：17类机制逐项数据、关联对象、服务/原证据、20版本索引；另列40封口、9个未支持可穿接缝及Boss/出生绑定。只有M16/M18/M21受控宿主切片有既有执行证据，不由相似组件推断兼容。
- [M35与M01精确资料](priority-modules.md)：完整物化附件与源变换、两linear ferry/锯/危险区时钟伤害、风铃出生候选/封口/实际射铃与出口条件、下批新适配器所需证据。
- [M24规则输入与反例](m24-rules.md)：全领取区域被真实C封口阻塞的充分证据；相交但不全堵、领取区不全堵但站位仍堵、垂直分离三个反例。不能把必要条件当充分条件，不扩大禁区/禁整个模块。
- [1.1.1迁移条件](migration-1.1.1.md)：main/PR77/两包来源，五项版本和requiredRewards精确变化，协议/运行时未变，分别给两下游的升级回归。

## 本轮执行与未解决项

新检查只解决本次实际未知：冻结配置是否匹配PR78夹具、完整内容中哪些字段被目标Provider拒绝、M35源/物化对应、M24几何规则误拒/误放反例、1.1.1到底改了什么。`tools/runtime_audit/check_930001.py` 实际完成43输入SHA/Git blob、完整content_store/地图对照、三个焦点内容源变换及原字节、所有机制归类、两个已发布ZIP语义差异和4几何用例检查；另将M35物化平台y改1px的合成反例实际拒绝于输入SHA阶段（[结果](../../../evidence/runtime-integration-930001/focused-negative-check.json)），未输出派生数据；不运行求解器，不重建catalog，不新增认证。

已复用PR78的M01真实射铃/出口接岸、M24形状与领取对照、五项15个原始领取后出界见证，未在本轮重跑旧宿主。**本轮没有新增Godot宿主兼容实测**：PR127尚无M35/M01适配，新模块机制、真实邻接、整图、正式spawn、Boss/终端、资源/稀有度随机化、Web新运行时算法及新identity恢复仍依赖下游下一批精确commit。

## 重跑本次定向检查

在本审计分支根目录执行。外部工作目录不含生产源库；下载的是只读输入，不安装到主游戏：

```bash
AUDIT_930001=$(mktemp -d /tmp/map-edit-930001.XXXXXX)
python3 - "$AUDIT_930001" <<'PY'
import concurrent.futures,hashlib,json,pathlib,sys,urllib.request
root=pathlib.Path(sys.argv[1])
lock=json.loads(pathlib.Path('evidence/runtime-integration-930001/frozen-input-lock.json').read_text())
def fetch(row):
    data=urllib.request.urlopen('https://raw.githubusercontent.com/zhipijun1996/'+row['repository']+'/'+row['commit']+'/'+row['path'],timeout=60).read()
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['gitBlob']
    folder='game' if row['repository']=='gunman-rush' else 'mapgen'
    p=root/folder/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:list(pool.map(fetch,lock))
PY
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/47aefebe07f4f0e7471f3d1546214502a6b2aade/releases/map-edit-modules-1.1.0.zip' -o "$AUDIT_930001/1.1.0.zip"
curl -fL 'https://raw.githubusercontent.com/zhipijun1996/map-edit/ff235b997dbc3fdc0f7073912a97a1c4a8ac6bbc/releases/map-edit-modules-1.1.1.zip' -o "$AUDIT_930001/1.1.1.zip"
python3 tools/runtime_audit/check_930001.py \
  --inputs "$AUDIT_930001" \
  --zip110 "$AUDIT_930001/1.1.0.zip" --zip111 "$AUDIT_930001/1.1.1.zip" \
  --out "$AUDIT_930001/results"
```

脚本在读取每份ZIP之前核固定SHA；不需读取历史实验目录、运行旧演示宿主或下载引擎。输出目录仅为审计派生结果，发布/生产工具不读取它。
