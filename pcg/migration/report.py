"""Current migration dashboard, derived from durable records rather than targets.

Historical physics reports and failed runs remain immutable. Audited/prepared
counts never contribute to the count of technically admitted Modules.
"""
from collections import Counter, defaultdict
from . import core


def _optional(path, default):
    return core.read(path) if path.is_file() else default


def run():
    catalog = core.read(core.ACTIVE/'catalog.json')
    journal = core.ledger()
    generated = {path: entry for path, entry in journal['entries'].items()
                 if path.startswith('pcg/map_directed/library/candidates/')
                 and entry.get('sourceType') != 'original_game'}
    original_game = {path: entry for path, entry in journal['entries'].items()
                     if entry.get('sourceType') == 'original_game'
                     and entry.get('sourceRole') != 'shared_reference_artifact'}
    done = {'active', 'recycled', 'exact_duplicate'}
    pending = {path: entry for path, entry in generated.items()
               if entry.get('migrationStatus') not in done}
    imported = _optional(core.STATE/'game-source-import.json', {})
    inventory = _optional(core.STATE/'inventory-generated-v1.json', {})
    dispositions = _optional(core.STATE/'source-disposition-v2.json', {})
    fixed_game = [row for row in dispositions.get('rows', []) if row['sourceType'] == 'original_game']
    game_statuses = Counter(journal['entries'].get(row['sourceKey'], {}).get('migrationStatus', 'not_yet_fulltested') for row in fixed_game)
    remaining_game = sum(value for key, value in game_statuses.items() if key not in done)
    pending_stages = Counter(entry.get('pendingStage', 'not_reconciled') for entry in pending.values())
    corner_inventory = _optional(core.STATE/'corner-port-inventory-v1.json', {'rows': []})
    rows = []; routes = probes = frames = 0
    reports = {}; geometry_changed = 0; current_game = 0
    corner_counts = Counter(); corner_by_position = {corner: Counter() for corner in
        ('TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_LEFT', 'BOTTOM_RIGHT')}
    configuration_count = 0
    current_human_reviews = Counter()
    physical_port_counts = Counter(); coincident_logical_ports = []
    from .query import HOLDS
    for entry in catalog['modules']:
        folder = core.ACTIVE/entry['id']
        doc = core.read(folder/'module.mapnote.json'); gc = doc['generationContract']
        meta = core.read(folder/'migration.json')
        current_human_reviews[meta.get('humanReview', 'UNKNOWN')] += 1
        physical = defaultdict(list)
        for port in gc['ports']:
            physical[(tuple(port['position']), port['face'], port['surface'], port['permission'])].append(port['id'])
        physical_port_counts[len(physical)] += 1
        for (position, face, surface, permission), names in physical.items():
            if len(names) > 1:
                coincident_logical_ports.append(dict(moduleId=entry['id'], position=list(position),
                    face=face, surface=surface, permission=permission, logicalNames=names,
                    scope='One physical anchor retained under multiple source names; no extra fork or alias-normalized certificate inferred.'))
        proof = meta.get('physicsReport')
        if proof:
            report = core.read(core.resolve_artifact(proof['path']))
            reports[proof['path']] = report
            probes += len(core.read(core.resolve_artifact(report['probes']['path'])))
        routes += len(gc['routes'])
        index = _optional(folder/'load-evidence/index.json', {'executions': []})
        for execution in index['executions']:
            receipt = core.read(folder/execution['artifacts']['receipt']['path'])
            frames += receipt['actual_frames']
        geometry_changed += bool(meta.get('internalGeometryChanged'))
        game = meta.get('sourceType') == 'original_game' or meta['sourcePath'] in original_game
        current_game += game
        assessment = next((r for r in corner_inventory['rows'] if r.get('scope') == 'current'
            and r.get('documentSha256') == entry['contentSha256']
            and r.get('contentVersion') == gc['contentVersion']), None)
        from .corners import verified_receipts, options as corner_options
        certified_relocations = set()
        for ref in verified_receipts(entry['id'], entry['contentSha256'], gc['contentVersion']):
            receipt = core.read(core.REPO/ref['path']); configuration_count += 1
            certified_relocations.update((r['portId'], r['corner']) for r in receipt['relocations'])
        for port in gc['ports']:
            options = port.get('cornerRelocations')
            if options is None and assessment:
                options = next((p['cornerRelocations'] for p in assessment['ports'] if p['portId'] == port['id']), {})
            if options is None: options = corner_options(doc, port)
            for corner, option in (options or {}).items():
                if not option.get('applicable'): continue
                # External inventory is assessment only; do not promote its booleans.
                allowed = option['allowed'] if port.get('cornerRelocations') is not None else 'UNKNOWN'
                if (port['id'], corner) in certified_relocations: allowed = True
                key = 'verified' if allowed is True else 'rejected' if allowed is False else 'unknown'
                corner_counts[key] += 1; corner_by_position[corner][key] += 1
        f = gc['foundation']
        title = entry['title'].replace('|', '\\|').replace('\n', ' ')
        rows.append(f"| [{title}](../../../modules/{entry['id']}/module.mapnote.json) | {'原游戏' if game else '本仓库'} | {f['widthBlocks']}×{f['heightBlocks']} | {entry['portCount']} | {len(gc['routes'])} |")
    counts = Counter(entry.get('migrationStatus', 'UNKNOWN') for entry in pending.values())
    attempts = sum(report['actualAttempts'] for report in reports.values())
    summary = dict(schema='pcg/foundation-migration-current-summary/v1',
        initialGeneratedVersions=inventory.get('counts', {}).get('candidate_versions', len(generated)),
        currentTemplates=len(catalog['modules']), generatedCurrentTemplates=len(catalog['modules'])-current_game,
        declaredVerifiedRoutePrograms=routes,
        portCounts=dict(Counter(entry['portCount'] for entry in catalog['modules'])),
        portCountsInterpretation='Logical source names; aliases at one physical anchor are not extra branches.',
        physicalPortCounts=dict(physical_port_counts), coincidentLogicalPortContracts=coincident_logical_ports,
        generatedOriginalsRemaining=len(pending), pendingStatuses=dict(counts),
        generatedRecycled=sum(e.get('migrationStatus') == 'recycled' for e in generated.values()),
        importedOriginalGameResources=imported.get('moduleResourceCount', len(original_game)),
        originalGameRegisteredReferences=len(fixed_game) if dispositions else 177,
        originalGameCertifiedModules=current_game,
        currentHumanReviewCounts=dict(current_human_reviews),
        defaultEligibleCurrentTemplates=sum(value for key, value in current_human_reviews.items() if key not in HOLDS),
        defaultEligibilityScope='Passes default human-hold exclusion only; demand, abilities, native profile, ports and allow_scoped still required. Unrestricted Map eligibility is zero.',
        currentHumanHeldTemplates=sum(value for key, value in current_human_reviews.items() if key in HOLDS),
        pendingSourceHumanHolds=dispositions.get('pendingHumanHoldsPreserved'),
        originalGameSourceStatuses=dict(game_statuses) if dispositions else dict(Counter(e.get('migrationStatus', 'UNKNOWN') for e in original_game.values())),
        originalGameReferencesRemaining=remaining_game if dispositions else None,
        generatedPendingStages=dict(pending_stages),
        sharedOriginalResourcesPreserved=dispositions.get('sharedDependencies', {}).get('count'),
        exactDuplicateSourceAliases=dispositions.get('exactDuplicateReferences'),
        sourceDispositionReport='pcg/migration/foundation-v1/source-disposition-v2.json' if dispositions else None,
        sourceDispositionSnapshotUtc=dispositions.get('createdUtc'),
        migrationHarnessAttempts=attempts, attemptsScope='distinct physics reports of current Modules only; failed/development runs are separate',
        boundaryAndContinuousExitFixtures=probes, internallyAdaptedCurrentTemplates=geometry_changed,
        finalPortablePackageCanonicalLoads=routes, finalPortablePackageReplayFrames=frames,
        cornerRelocations=dict(corner_counts), cornerRelocationsByPosition={k: dict(v) for k, v in corner_by_position.items()},
        certifiedPortConfigurations=configuration_count,
        prototypeHumanReview='SEPARATELY_RECORDED', unrestrictedMapCertification=False,
        newGameplayFamilies=0, onlinePublication='NOT_PERFORMED')
    core.write(core.STATE/'summary.json', summary)
    status = _optional(core.STATE/'status.json', {})
    status.update(active_step='本轮全量迁移处理完成；真实失败与人工 hold 原处保留，下一轮按证据修复',
        new_foundation_certifications=len(catalog['modules']), foundation_base_template_count=len(catalog['modules']),
        remaining_generated_versions=len(pending), imported_original_game_resources=summary['importedOriginalGameResources'],
        original_game_new_foundation_certifications=current_game, current_contract_version=2,
        unrestricted_map_ready=False, corner_port_relocations=dict(corner_counts))
    complete_step='Full fixed inventory processed: 134 generated versions + 177 original-game references; actual admitted, exact alias, failed and held dispositions reconciled separately.'
    if complete_step not in status.setdefault('completed_steps', []): status['completed_steps'].append(complete_step)
    # Keep the completed-step history, including earlier pilot work.
    core.write(core.STATE/'status.json', status)
    text = f'''# Module 地基迁移：当前结果

正式目录有 **{len(catalog['modules'])} 个当前模板**：本仓库 {summary['generatedCurrentTemplates']} 个，原游戏 {current_game} 个。
每个模板只保留一个当前内容版本；迁移、镜像及换边配置不计为新玩法。
技术、人工观感、试玩及生产认可独立记录。未人工审核不等于已经认可。
当前人工状态：{dict(current_human_reviews)}；其中 {summary['currentHumanHeldTemplates']} 个当前归档带设计 hold，默认检索排除。其余 {summary['defaultEligibleCurrentTemplates']} 个通过人工 hold 过滤，仍须满足需求、能力、原生档案、Port 和有限集成条件；不代表获得人工批准或整图资格。
源待处理层另保留 {summary['pendingSourceHumanHolds']} 个人工 hold，不能与当前归档的设计 hold 混算。

| Module | 来源 | Block 尺寸 | Port 逻辑名 | 已验路线程序 |
| --- | --- | --- | --- | --- |
''' + '\n'.join(rows) + f'''

当前模板对应的独立物理报告共 {attempts} 次 Harness 实验，包含 {probes} 个边界及连续出口试件。
这些数字仅覆盖当前模板的证据，不包含被保留的开发失败或重复播放，不代表迁移完成数量。
最终可玩包另实际重放 {routes} 条冻结程序、{frames} 帧；重放不是新增独立校准样本。
{geometry_changed} 个当前模板记录了内部地貌修改，具体差异和证据见各自 migration.json。
当前 {len(coincident_logical_ports)} 处接口保留了同一物理锚点的多个源逻辑名；编辑器将其合并显示，不能算作额外分叉。正式契约的别名归一化仍需另行重绑证据，当前文档和认证不静默改写。
具体为 game-route-junction 和 game-forest-playful-module-variants-thorn-side-outlet。检索按选中的物理口计数；同时选择重合逻辑名会返回 coincident_logical_ports_need_alias_normalization 及完整名字/坐标。只选一个别名仍保留原 Route、能力及封口认证门槛，不自动授予联合连接或封口资格。

## 来源去向

- 本仓库原地待处理 **{len(pending)} 个版本**，状态：{dict(counts)}。
- 待处理的真实阶段：{dict(pending_stages)}；原始格式缺口与后续实验失败分开保存。
- 已明确回收的本仓库源版本：{summary['generatedRecycled']}；成功迁移的原件另由 ledger 关联至回收目录。
- 原游戏固定登记 **{summary['originalGameRegisteredReferences']} 个引用**，当前技术入库 {current_game} 个；其余去向及实际失败见 [全量去向账本](source-disposition-v2.json)。资源、Foundry 参数样品和引用数不等于玩法家族数。
- 原游戏 {summary['importedOriginalGameResources']} 份共享资源定义保留为依赖，不作为另一批待迁移 Module，也不搬走或删除。
- 尺寸、Port 修正或工具映射缺失属于需继续完成的工作，不能仅审计后视为迁移完成。
- 完全重复归并保留来源和 alias；近似重复、冗余平台疑点保留待审，不自动删除。
- 311 是 **134 个本仓库历史版本 + 177 个原游戏登记引用**；当前工件、版本、参数样品与引用数量均不等于独立玩法家族数。
- 本轮已逐项适配和处理固定清单；实际失败和人工 hold 保留原处及其证据，留待下一轮修复，不能从清单中删去制造完成。

## 四角 Port 换边

当前正式内容的适用选项：认证通过 {corner_counts['verified']}，明确拒绝 {corner_counts['rejected']}，未验证 {corner_counts['unknown']}。
四角覆盖 LEFT↔TOP、RIGHT↔TOP、LEFT↔BOTTOM、RIGHT↔BOTTOM，目标为同一角落 Block 的相邻外边中心。
允许必要的局部接口适配，但同一逻辑 Port 的原位置与迁移位置互斥；多个换边不能默认组合。
外部 assessment 只记录适用性，不能授予可用权限。UNKNOWN 不提供给 Map 匹配。

详见 [corner-port-inventory-v1.json](corner-port-inventory-v1.json) 和各模板 cornerRelocations/portConfigurations。
编辑器显示来源版本的换边状态；修改后的草稿需重新认证。

## 复现与证据

```bash
npm run check
npm run check:migration
python3 -m pcg.migration.corners
python3 -m pcg.migration.migration_status
python3 -m pcg.migration.report
python3 -m pcg.migration.query pcg/migration/foundation-v1/example-demand.json --allow-scoped
```

[ledger.json](ledger.json)记录每个源版本去向，[summary.json](summary.json)记录当前统计。
[source-disposition-v2.json](source-disposition-v2.json)逐项覆盖本仓库134份来源和原游戏177个登记引用；尺寸/Port适配通过、clean通过、完整物理通过和正式入库分开计数。待处理候选的冻结文档、输入和修改回执保存在该账本的 evidence_snapshot 中，不计为另一套库。
真实批次、修正差异、冻结源、失败及未验证范围保留在各自证据中；实际实验命令以批次回执为准。
历史浏览器检查仅证明其当时对应的目录，不能替代最新库存验收。网页与新增库尚未发布线上。
本轮不运行旧 Map 生成器，不宣称整图通过；未认证镜像、封口组合、换边或进入状态均不可推断有效。
'''
    (core.STATE/'REPORT.md').write_text(text)
    return summary


if __name__ == '__main__':
    import json
    print(json.dumps(run(), ensure_ascii=False, indent=2))
