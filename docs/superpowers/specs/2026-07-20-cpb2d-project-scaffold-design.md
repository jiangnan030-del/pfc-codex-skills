# CPB2D UCS 项目脚手架设计

日期：2026-07-20  
状态：已由用户确认  
适用仓库：`pfc-codex-skills`

## 1. 背景与问题

当前 `pfc-workflow` 已具备完整的 PFC 生命周期路由能力，但主要面向熟悉 PFC 的用户。对于只有试件几何、裂隙信息和实验应力-应变数据的小白用户，当前流程仍存在以下断点：

1. `pfc-workflow` 会路由到不同子技能，但缺少强制、逐题进行的新项目问诊流程。
2. 现有 `templates/project-case/` 主要是某类历史项目的运行与后处理脚本，不是通用的新项目生成器。
3. AI 可以按描述生成 `.dat`，但参数、命名、阶段保存、数据导出和后处理接口经常不一致，生成结果未必可运行。
4. 不同脚本之间缺少统一项目 contract，导致调参、后处理、AE 和复现工作依赖临时约定。
5. 小白不知道应该先验证完整试件、再扩展裂隙试件，也不知道哪些初始参数只是用于跑通而不是最终标定参数。

工作区中的 `Reference intact` 和 `Reference crack` 提供了可用于抽象的黄金样例：两者均采用 `1model.dat`、`2bond.dat`、`3load.dat`、`4export.dat`、`fracture.p2fis` 的分阶段结构，并包含 `sample`、`parallel_bonded`、`stage_a` 至 `stage_d`、`peak`、`final` 等保存节点。这些案例适合作为模板来源，但其中的具体标定值、实验路径和生成结果不能直接发布或写死到通用脚手架中。

## 2. 目标

第一版提供一条可重复的 CPB/PFC2D UCS 黄金路径，使小白用户能够从自己的几何信息和实验数据出发，生成命名规范、文件齐全、可审计、可继续调参和后处理的项目骨架。

具体目标：

1. 将 `pfc-workflow` 从专家路由器扩展为“小白问诊向导 + 项目总控”。
2. 新增 `create_cpb2d_project.py`，确定性生成 CPB2D UCS 项目结构和每个 case 的 PFC 文件。
3. 默认使用 PFC2D 和 LPBM/`linearpbond`，先保证完整试件可运行。
4. 支持参数化直线裂隙，并预留非线性裂隙坐标文件接口。
5. 默认保留 `stage_a`、`stage_b`、`stage_c`、`stage_d`、`peak`、`final`，暂不强制运行重型 AE。
6. 支持每个 case 一个 Excel/CSV 实验文件，并为总 Excel 多 sheet 导入预留接口。
7. 强制后处理通过 `pfc-postprocessing` 的 script-first 工作流进入。
8. 把默认值、用户值和 AI 假设显式记录在配置和 runbook 中。

## 3. 非目标

第一版不包含：

- PFC3D 项目生成；
- flat-joint 或 GBM 的完整可运行模板；
- 非线性裂隙切割实现，仅预留 polyline CSV contract；
- 自动实验曲线清洗和识别；
- 全自动微参数反演闭环；
- 默认启用 heavy AE、moment tensor 或 Fig.9 A-F 专用流程；
- 自动执行 PFC 长时计算；
- 发布用户的 `.sav`、实验数据、生成图件或本机路径。

## 4. 总体架构

系统分为四层：

1. **问诊层**：`pfc-workflow` 一题一题收集项目、几何、实验、颗粒、接触和输出需求。
2. **配置层**：问诊结果落入 `cpb2d_intake.yaml`、`project_config.yaml` 和 `cases.csv`。
3. **生成层**：`create_cpb2d_project.py` 读取配置，校验参数并生成项目骨架和 case 脚本。
4. **执行与后处理层**：用户先运行 `intact/run_all.dat`，验证通过后再运行裂隙 case；输出由 `pfc-postprocessing` 的现有脚本处理。

数据流：

```text
用户几何/实验数据
  -> pfc-workflow 问诊
  -> cpb2d_intake.yaml
  -> create_cpb2d_project.py
  -> project_config.yaml + cases.csv + pfc_cases/*
  -> PFC2D 先运行 intact
  -> 再运行 straight-crack case
  -> 标准 CSV/sav 输出
  -> pfc-postprocessing script-first 路由
```

## 5. 项目目录结构

脚手架采用混合结构：根目录管理配置、实验、几何、标定、图表和报告；每个 case 目录保持 PFC 可独立运行。

```text
<project_slug>/
├── README_runbook.md
├── project_config.yaml
├── cases.csv
├── data/
│   └── experimental/
├── geometry/
│   └── cracks/
│       ├── README.md
│       └── <case_name>_polyline.csv
├── pfc_cases/
│   ├── intact/
│   │   ├── 1model.dat
│   │   ├── 2bond.dat
│   │   ├── 3load.dat
│   │   ├── 4export.dat
│   │   ├── fracture.p2fis
│   │   └── run_all.dat
│   └── b0_d20/
│       └── ...
├── calibration/
│   ├── targets.csv
│   ├── parameter_bounds.yaml
│   └── trials/
├── postprocess/
│   ├── run_postprocess.py
│   └── manifest.csv
├── figures/
├── tables/
└── reports/
    └── modeling_notes.md
```

## 6. 命名规范

### 6.1 项目名

项目 slug 只能使用小写英文字母、数字和下划线，例如 `cpb_2d_ucs_3day`。

### 6.2 Case 名

- 完整试件固定为 `intact`。
- 直线裂隙试件使用 `b{angle}_d{distance}`，例如 `b0_d20`、`b30_d14`。
- 非线性裂隙预留 `nl_{id}` 或 `b{angle}_d{distance}_nl{id}`，第一版不生成切割命令。

### 6.3 PFC 文件职责

- `1model.dat`：模型初始化、domain、墙体、颗粒生成、线性接触和初始平衡。
- `2bond.dat`：恢复 `sample`、裂隙几何处理、LPBM 成键、参数赋值和保存 `parallel_bonded`。
- `3load.dat`：UCS 加载、监测、history、阶段保存、峰值识别、终止条件和保存 `final`。
- `4export.dat`：导出应力-应变、裂纹数量和常规后处理数据。
- `fracture.p2fis`：裂纹跟踪与裂纹统计。
- `run_all.dat`：按 1 至 4 的顺序调用，作为新手唯一运行入口。

### 6.4 固定保存节点

```text
sample
parallel_bonded
stage_a
stage_b
stage_c
stage_d
peak
final
```

## 7. 输入配置

### 7.1 `project_config.yaml`

全局配置至少包含：

- 项目 slug、标题、PFC 版本、单位系统；
- 试件宽度、高度、粒径范围、孔隙率、密度和阻尼；
- 默认接触模型、初始刚度/强度参数；
- 加载方式、墙速、停止比例、history interval；
- stage 模式和峰值应变初值；
- 常规输出开关和 heavy AE 开关；
- 每个默认值的来源和是否属于假设。

第一版采用 SI 模型单位，在用户界面和配置中允许使用 mm、MPa，再由脚手架显式转换到 m、Pa。

### 7.2 `cases.csv`

每行表示一个 case，至少包含：

```text
case_name
family
enabled
experiment_file
crack_enabled
crack_type
angle_deg
distance_mm
length_mm
width_mm
center_x_mm
center_y_mm
```

所有 case 必须先登记，AI 不得绕过 `cases.csv` 临时创建目录或起名。

### 7.3 实验数据

默认每个 case 一个 Excel/CSV：

```text
data/experimental/intact.xlsx
data/experimental/b0_d20.xlsx
```

向导必须询问：

- 列名；
- 应力单位；
- 应变是小数、百分数，还是由力/位移换算；
- 试件尺寸是否与配置一致。

第一版只登记实验文件和生成 `calibration/targets.csv` 占位；文件缺失产生 warning，但不阻断骨架生成。

## 8. 几何设计

### 8.1 完整试件

`intact` 不执行颗粒删除或裂隙弱化。

### 8.2 参数化直线裂隙

输入：

- `angle_deg`
- `length_mm`
- `width_mm`
- `center_x_mm`
- `center_y_mm`
- 可选 `distance_mm`，用于 case 命名和论文变量登记

端点计算：

```text
half_length = length_mm / 2
dx = half_length * cos(angle_deg)
dy = half_length * sin(angle_deg)
end_1 = center - (dx, dy)
end_2 = center + (dx, dy)
radius = width_mm / 2
```

生成到 `2bond.dat`：

```text
ball delete range cylinder end-1 (...) end-2 (...) radius ...
```

脚手架应检查裂隙是否超出试件，以及裂隙宽度是否小于最大颗粒直径。后者默认 warning，因为用户可能有明确的几何意图。

### 8.3 非线性裂隙预留

目录预留：

```text
geometry/cracks/<case_name>_polyline.csv
```

建议列：

```text
point_id,x_mm,y_mm
```

第一版只登记 `crack_type=polyline_reserved` 并将 case 设为 disabled，避免生成声称可用但实际未实现的切割脚本。

## 9. 脚手架脚本设计

脚本位置：

```text
skills/pfc-workflow/scripts/create_cpb2d_project.py
```

### 9.1 推荐调用

```bash
python skills/pfc-workflow/scripts/create_cpb2d_project.py \
  --output-dir ./cpb_2d_ucs_3day \
  --project-slug cpb_2d_ucs_3day \
  --from-intake cpb2d_intake.yaml
```

最小 CLI：

```bash
python skills/pfc-workflow/scripts/create_cpb2d_project.py \
  --output-dir ./cpb_2d_ucs_3day \
  --project-slug cpb_2d_ucs_3day \
  --with-intact \
  --straight-crack b0_d20:0:20:20:3
```

### 9.2 职责

脚本负责：

1. 校验 intake 和 CLI 参数；
2. 创建混合项目结构；
3. 写入 `project_config.yaml` 和 `cases.csv`；
4. 为所有 enabled case 生成六个 PFC 文件；
5. 生成 runbook、标定目标/边界、后处理 manifest 和建模记录模板；
6. 执行静态自检；
7. 打印下一步运行顺序；
8. 默认拒绝覆盖已有项目，只有 `--force` 才允许覆盖脚手架管理的文件。

脚本不负责：

- 自动执行 PFC；
- 自动标定；
- 猜测最终参数；
- 自动启用 heavy AE；
- 实现非线性裂隙切割；
- 随意修改已有用户项目。

### 9.3 模板来源

模板从 `Reference intact` 和 `Reference crack` 抽象，但公开仓库只保留通用化后的文本模板和必要 FISH 源码：

- `1model.dat` 以完整试件建模流程为基准；
- intact/crack `2bond.dat` 分别提供不切割和直线裂隙切割分支；
- `3load.dat` 合并统一的 stage、peak、final 逻辑；
- `4export.dat` 提供应力-应变和裂纹计数基础导出；
- `fracture.p2fis` 保留必要裂纹跟踪逻辑；
- 不复制 `.sav`、结果 CSV、图片、Excel 或项目元数据。

## 10. `pfc-workflow` 小白问诊流程

### 10.1 触发条件

以下情况必须进入 CPB2D 向导：

- 从 0 创建 PFC 项目；
- 有几何/实验数据但没有可运行 case；
- 用户不知道如何命名或组织项目；
- 只有实验数据；
- 要求新建文件夹并先从完整试件标定；
- 需要后续批量运行完整和裂隙试件。

如果用户没有完整的 `1model.dat`、`2bond.dat`、`3load.dat` 和 `4export.dat`，不得直接进入调参、后处理或 AE。

### 10.2 提问顺序

问诊一次只问一个问题，优先多选或带默认值的问题。

1. **项目**：项目名、PFC 版本、2D UCS 确认、材料类型。
2. **试件**：宽度、高度、单位、颗粒粒径范围。
3. **几何**：intact 或裂隙；裂隙类型和参数。
4. **实验**：文件路径、列名、应力/应变定义和单位。
5. **初始参数**：用户参数或参考 seed 参数。
6. **输出**：常规曲线、裂纹、场、接触、stage 保存和可选 AE。

未知参数可使用默认值，但必须记录为 assumption，并明确它不是最终标定参数。

### 10.3 输出与执行

问诊结束后先形成 intake/config/cases，再调用脚手架。脚手架静态自检通过后，用户先运行 `intact`，再运行裂隙 case。

## 11. 技能与脚本衔接

### 11.1 `pfc-workflow` → 脚手架

- `pfc-workflow`：提问、决策、解释和总控。
- `create_cpb2d_project.py`：项目骨架的唯一生成器。
- AI 不得在新项目路径中绕过脚手架自由编写一套不受 contract 管理的 PFC 文件。

### 11.2 `pfc-standard-tests`

非 CPB2D 黄金路径的标准试验应先由 `pfc-standard-tests` 选择模板，不应强行套用本脚手架。

### 11.3 `pfc-postprocessing`

PFC 生成数据后必须：

1. 读取 `pfc-postprocessing/references/script-catalog.md`；
2. 读取匹配的实际脚本；
3. 使用或适配该脚本；
4. 不得根据技能描述随机绘图。

### 11.4 `pfc-ae-energy`

第一版默认关闭 heavy AE。启用前必须确认 `stress_strain.csv`、AE 事件文件和保存节点满足其输入 contract。

### 11.5 `pfc-mcp`

如果可用，应先对 intact 做语法和轻量试运行检查。intact 未通过时不得批量运行裂隙案例。

## 12. 错误处理

- 项目名非法：拒绝并给出规范示例。
- 输出目录已存在：默认拒绝；`--force` 前明确覆盖范围。
- 实验文件不存在：warning，targets 标记 `missing_experiment`。
- 裂隙参数不完整：只生成 intact，将该裂隙 case 设为 disabled。
- 非线性裂隙：生成登记和 CSV 示例，但 case 默认 disabled。
- 参数未知：使用 seed 参数并记录 assumption。
- PFC 运行失败：停在 intact，先修建模/成键/加载，不进入批量标定。
- stage 没有保存：报告缺失节点，不静默假定成功。

## 13. 测试设计

### 13.1 静态生成测试

使用 intact + `b0_d20` 生成 demo，断言：

- 项目结构和必需文件存在；
- `run_all.dat` 引用文件均存在；
- enabled case 和目录一一对应；
- intact 不含裂隙删除命令；
- `b0_d20` 包含正确端点和半宽计算结果；
- 无本机绝对路径；
- runbook 明确先 intact 后 crack；
- seed 参数被标记为非最终标定值。

### 13.2 参数校验测试

覆盖：

- 非法 slug/case 名；
- 非法尺寸、粒径、密度、孔隙率和墙速；
- 裂隙越界；
- 裂隙宽度过小 warning；
- 目录已存在且未使用 `--force`；
- 实验文件缺失 warning。

### 13.3 PFC 轻量运行测试

环境允许时：

1. 运行 `pfc_cases/intact/run_all.dat`；
2. 检查八个保存节点和 `stress_strain.csv`；
3. intact 通过后运行 `pfc_cases/b0_d20/run_all.dat`；
4. 记录 PFC 版本、随机种子和运行结果。

### 13.4 后处理衔接测试

使用脚手架导出的 `stress_strain.csv` 运行 `pfc-postprocessing/scripts/plot_curves.py`，确认数据契约和输出命名兼容。

## 14. 验收标准

实现完成必须满足：

1. `pfc-workflow` 有强制的新手问诊规则。
2. `templates/scope.md` 升级为 CPB2D intake 所需字段。
3. 脚手架生成 intact 和至少一个直线裂隙 case。
4. 项目/case/file/stage 命名统一。
5. 每个 enabled case 有完整六文件和单入口 `run_all.dat`。
6. 默认关闭 heavy AE，但保留 stage 和后续接口。
7. 新手运行顺序固定为 intact 后 crack。
8. 后处理遵守 script-first 规则。
9. 静态测试和发布校验通过。
10. 仓库不包含用户 `.sav`、生成图表、私有实验数据和本机路径。

## 15. 后续扩展

第二阶段可增加：

- polyline 非线性裂隙切割/弱化；
- Excel/CSV 实验曲线自动识别和标准化；
- intact 参数标定向裂隙 case 的继承规则；
- 自动参数扫描、LHS、代理模型和 Bayesian optimization；
- heavy AE 模块按需接入；
- flat-joint/GBM 路线；
- PFC3D 项目工厂；
- 更严格的 PFC 语法静态检查和 MCP smoke test。
