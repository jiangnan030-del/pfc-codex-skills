# pfc-code 深度分析与知识库集成方案

## 结论

`pfc-code` 可以提炼出一套高价值的 PFC 建模规范，但不能把任一示例文件直接当作“官方规范”或跨版本模板。最稳妥的集成方式是：

1. 把重复出现的工程模式提炼为 `MUST / SHOULD / MAY` 规范；
2. 用固定 commit 的目录/文件/哈希目录做可检索知识库；
3. 让 `pfc-workflow` 在生成代码前先检索证据，再由目标版本文档或 `pfc-mcp` 确认语法；
4. 不直接把上游源码并入 MIT 仓库，因为当前固定 commit 的仓库根目录未发现许可证文件。

本次分析固定到：

- 仓库：<https://github.com/jiangnan030-del/pfc-code>
- commit：[`af774eb322e6c6bef18a56a0a69770e0e82c9bdf`](https://github.com/jiangnan030-del/pfc-code/commit/af774eb322e6c6bef18a56a0a69770e0e82c9bdf)

## 1. 语料结构

`pfc-code` 不是一篇线性教程，而是分层案例语料：

| 目录 | 主要价值 | 在 workflow 中的位置 |
|---|---|---|
| `datafiles2d/examples` | 二维完整案例、驱动文件、FISH 工具 | P2-P5 工程模式 |
| `datafiles2d/tutorials` | CMAT、断裂岩体、节理滑移等特性语义 | P2/P3 语法与顺序证据 |
| `datafiles2d/verifications` | 测量、波传播、接触模型等验证 | P6 Verification |
| `datafiles2d/python` | Python 驱动入口 | P4/P5 自动化 |
| `datafiles2d/thermal` | 二维热学扩展 | P2/P4/P6 |
| `datafiles3d/examples` | 岩石试验、DFN、破碎、柔性三轴等 | P2-P5 工程模式 |
| `datafiles3d/tutorials` | 胶结装配、回调、clump、级配等 | P2/P4 特性语义 |
| `datafiles3d/verifications` | Hertz、恢复系数、波、测量等 | P6 Verification |
| `datafiles3d/python` | `itasca`、array、UCS、SciPy | P4/P5 自动化 |
| `datafiles3d/thermal` | 自由/约束膨胀 | P4/P6 热-力验证 |
| `datafiles3d/ccfd` | CFD/网格/辅助输入 | 耦合输入契约 |

因此，知识库检索不应只搜关键词，还要带上：维度、证据层级、生命周期阶段和专题标签。

## 2. 可高置信提炼的建模规范

### 2.1 薄驱动 + 分阶段文件

二维颗粒案例的 `Doall.p2dat` 只设置参数、调用 `MakeSpecimen` / `CompactSpecimen` / `BiaxialTest`，并在每阶段保存；岩石试验驱动则从同一胶结态分别分叉 UCS 与拉伸。这说明：

- driver 应负责“编排”，不负责所有细节；
- 生成、平衡、胶结、加载、测量工具应拆开；
- 派生试验必须从同一个已验证 baseline restore，避免初始状态漂移。

证据：

- [2D granular driver](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/Doall.p2dat)
- [2D rock-test driver](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/rocktest/doall_parallel.p2dat)

### 2.2 初始化顺序必须显式

重复模式是：`model new` → domain → CMAT → walls/objects → seed → particles → attributes → relaxation/solve。它不是美观问题，而是接触生成、边界和可复现性的前提。

- 固定 seed 是回归和标定 baseline 的必要条件；
- domain/condition 必须显式；
- CMAT 应在依赖它的接触产生前定义；
- `ball distribute` 产生重叠初态，必须 calm/cycle/solve。

证据：

- [2D specimen build](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/MakeSpecimen.p2dat)
- [3D rock specimen](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles3d/examples/rocktest/make_sample.p3dat)

### 2.3 “达到循环数”不等于“达到平衡”

案例通常先用若干 cycle/calm 消重叠，再用 force-ratio solve。密度缩放仅用于准静态准备阶段，随后恢复自动时步。可提炼为 gate：

- 必须记录收敛量与阈值；
- 如使用 density scaling，加载前恢复物理/自动时步；
- 标定试样应识别 floaters，并说明是否排除或保留。

### 2.4 CMAT 与当前 contact 必须分清

`cmat5` 明确展示：修改 CMAT 影响未来接触；更新当前接触还需要 `contact cmat apply` 或接触命令。`cmat6` 进一步说明：正 bond gap 只有在对应 inactive contacts 已被 proximity/contact detection 建立后才有效。

这是最值得写进 `pfc-workflow` 的防错规范之一：

- 每次赋参都要声明作用于“未来接触 / 当前接触 / 两者”；
- 更换模型后验证 contact model、数量、range/group 覆盖；
- bond gap 失效时先查 proximity/clean/apply，不要盲目增大 gap。

证据：

- [CMAT apply/current contacts](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/tutorials/using_cmat/cmat5.p2dat)
- [CMAT proximity/bond gap](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/tutorials/using_cmat/cmat6.p2dat)

### 2.5 胶结是独立的状态转换

2D/3D rocktest 都把胶结安装放在独立阶段，并在胶结后：

- 重置 displacement；
- 明确处理 linear force / contact force / moment；
- cycle 一步并重新 solve；
- 保存 bonded baseline。

这说明“胶结后直接加载”是反模式。必须先区分预应力是物理目标还是数值遗留，再执行 reset gate。

证据：

- [2D bond stage](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/rocktest/parallel_bonded.p2dat)
- [3D bond stage](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles3d/examples/rocktest/parallel_bonded.p3dat)
- [bonded assembly comparison](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles3d/tutorials/bonded_assembly/cmlinearpbond_simple.p3dat)

### 2.6 边界控制必须有“控制模式 + 动态面积 + 停机契约”

servo compaction 用当前尺寸更新目标力，并同时检查横纵应力误差和平均力比；biaxial loading 则关闭部分 servo、切换到速度/应变控制。这可提炼为：

- 每个方向显式声明 stress/force/velocity/strain/fixed/free；
- 应力转力使用当前有效面积；
- halt 必须是目标状态与稳定性条件的组合；
- preparation 和 loading 的阻尼、时步、速度不能混为一谈。

证据：

- [2D servo compaction](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/CompactSpecimen.p2dat)
- [2D biaxial loading](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/BiaxialTest.p2dat)

### 2.7 测量应交叉验证

`StressUtilities` 同时提供边界反力、全试样 Love-Weber、局部圆域应力；`StrainUtilities` 同时提供 measure strain 与 gauge-ball strain。`MeasureLogic` 则把 measure porosity 与解析值比较。

因此，报告关键宏观量时应优先使用两种独立估计；差异本身就是边界效应、代表体积或实现错误的诊断量。

证据：

- [stress utilities](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/StressUtilities.p2fis)
- [strain utilities](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles2d/examples/granular/StrainUtilities.p2fis)
- [3D measure verification](https://github.com/jiangnan030-del/pfc-code/blob/af774eb322e6c6bef18a56a0a69770e0e82c9bdf/datafiles3d/verifications/measure_logic/MeasureLogic.p3dat)

### 2.8 事件与 callback 有生命周期

fracture 工具把 bond break 事件分成 tension/shear，并批量更新 fragment；callbacks tutorial 明确不同 cycle point 的合法操作和先后顺序。规范应要求：

- 初始化/restore 时防重复注册；
- 记录事件时间、位置、方向、源对象；
- 昂贵 fragment 计算批处理；
- 阶段结束移除 callback，防止状态泄漏。

### 2.9 P6 必须复用 verification 语料

知识库不能只服务“找代码”，还应把 `verifications` 路由到 P6：

- measure/porosity → 测量逻辑验证；
- wave propagation → 动力/波传播验证；
- bonded assembly comparison → 状态重置验证；
- thermal free expansion → 热-力基本验证。

应用模型前先过对应 feature-level verification，比直接跑工程大模型更可靠。

## 3. 不能直接规范化的内容

以下内容只能作为案例起点，不能直接进入通用默认值：

- seed 的具体数字；
- `ratio-average` 的具体阈值；
- damping、加载速度、servo gain；
- bond gap、proximity；
- 粒径、孔隙率、材料刚度和强度；
- post-peak fraction；
- 旧式命令缩写/别名。

原因：这些值受版本、维度、粒径、单位、材料、目标惯性水平和边界条件共同影响。

## 4. 对原 pfc-workflow 的差距判断

原技能已经有 P1-P7、版本确认、固定 seed、阶段保存、标定路由和后处理路由，方向正确。主要缺口是：

| 缺口 | 风险 | 本次优化 |
|---|---|---|
| 没有来源证据层级 | Agent 容易凭记忆生成命令 | 引入 tutorial/example/verification 分层目录 |
| 没有检索协议 | 代码案例存在但无法稳定复用 | 增加离线 catalog 查询器 |
| CMAT/current contact 未升级为硬 gate | 未来接触与当前接触错配 | 写入 MUST 规范 |
| bond gap/proximity/clean 顺序不突出 | “胶结装不上”时盲目扩大 gap | 增加 bond installation gate |
| 胶结后 reset 不是强制状态转换 | 初始力污染加载曲线 | 增加 reset + re-equilibrate gate |
| 测量交叉验证不强 | 单一 estimator 误导结论 | 增加两方法交叉检查 |
| verification 未与案例检索绑定 | P6 容易变成报告口号 | 把 verification 目录显式路由到 P6 |
| 上游许可状态未隔离 | 直接复制可能污染 MIT 包 | 使用 external pinned catalog，不 vendor 源码 |

## 5. 集成架构

```text
pfc-codex-skills/
├── knowledge/pfc-code/
│   ├── source-lock.json       # 固定仓库/commit/许可策略
│   ├── catalog.json           # 维度×层级×阶段×主题目录
│   └── README.md              # 使用与更新协议
├── scripts/query_pfc_code_kb.py
├── skills/pfc-workflow/
│   ├── SKILL.md               # 先检索证据，再走 P1-P7 gates
│   └── references/
│       └── pfc-code-modeling-standard.md
└── docs/pfc-code-integration-analysis.md
```

这是一种“知识库适配层”，不是 subtree/submodule：

- 可固定版本、可审计、可离线搜索元数据；
- 不把上游未知许可内容并入 MIT 仓库；
- 单个技能仍可通过标准文档工作，完整仓库则获得目录检索能力；
- 未来确认许可后，可再评估只读 submodule 或生成式索引。

## 6. 后续建议

1. 给 `pfc-code` 补 README、来源说明和明确许可证。
2. 自动生成完整 tree manifest，并在 PR 中展示新增/删除/变更案例。
3. 为 catalog 增加 `pfc_version_verified` 字段；未验证保持 `unknown`。
4. 给关键规范建立最小回归案例：CMAT apply、positive bond gap、bond reset、servo halt、measure error。
5. 在有 PFC 运行环境时执行 smoke test；当前静态集成不等同于 PFC runtime 验证。
