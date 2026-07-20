# CPB2D 新项目逐题向导

本向导面向从几何、实验数据或初始参数开始、尚无可运行四阶段 case 的用户。仅支持 **PFC2D 6.0（PFC6 only）**，接触模型默认且当前仅支持 **LPBM**，配置值写为 `contact_model.family: linearpbond`。

## 对话规则

- 严格一次只问一个问题：收到并复述当前答案后，才进入下一题；不要一次抛出整张表。
- 每题都说明 **默认**、**答案形状**、**配置目标**、**阻断性**。用户采用默认值时，也要写入 intake。
- 不确定、推定或暂用 seed 的内容必须加入顶层 `assumptions`，并在第 7 阶段逐项复核。
- 实验文件必须登记为 `data/experimental/...`；文件暂不存在只产生 warning，不阻断静态生成。
- `polyline_reserved` 必须 `enabled: false`；v1 只生成 `point_id,x_mm,y_mm` schema，不执行颗粒切割，也不声称可运行。
- 每个阶段可按 case 重复必要问题，但仍然一次只问一个问题。

## 阶段 1：项目、版本与材料

### 问题 1.1：项目标识是什么？

- **默认**：`cpb2d_beginner_demo`。
- **答案形状**：`project.slug` 为小写字母、数字、下划线组成的安全 slug；`project.title` 为单行标题。
- **配置目标**：`project.slug`、`project.title`。
- **阻断性**：阻断；非法 slug 或空标题不能继续生成。

### 问题 1.2：是否确认使用 PFC2D 6.0 做 CPB 单轴压缩？

- **默认**：确认，材料描述为 `cemented paste backfill`。
- **答案形状**：确认/不确认，加一条单行材料描述。
- **配置目标**：`project.pfc_version: "6.0"`；材料描述记录到 `assumptions`，因为当前 schema 没有独立材料字段。
- **阻断性**：阻断；PFC3D、PFC7 或其他版本不进入本 v1 脚手架。

### 问题 1.3：随机种子基值是什么？

- **默认**：`31000`。
- **答案形状**：正整数；case 使用 `random_seed_base + case_index`。
- **配置目标**：`project.random_seed_base`。
- **阻断性**：阻断；缺失或非正整数不能加载。

## 阶段 2：试件尺寸与单位

### 问题 2.1：试件宽度和高度是多少？

- **默认**：`40.0 mm × 40.0 mm`。
- **答案形状**：两个正数，并明确单位；向导统一换算后以 mm 写入。
- **配置目标**：`specimen.width_mm`、`specimen.height_mm`。
- **阻断性**：阻断；尺寸和单位不明确不能生成。

### 问题 2.2：颗粒半径范围是多少？

- **默认**：`0.30–0.50 mm`。
- **答案形状**：两个正数，且最小值不大于最大值。
- **配置目标**：`specimen.particle_radius_min_mm`、`specimen.particle_radius_max_mm`。
- **阻断性**：阻断；未知时可采用默认，但必须加入 `assumptions`，注明是 seed。

### 问题 2.3：孔隙率、密度和阻尼是多少？

- **默认**：`0.15`、`1900.0 kg/m^3`、`0.70`。
- **答案形状**：`0 < target_porosity < 1`、正密度、`0 <= damping <= 1`。
- **配置目标**：`specimen.target_porosity`、`specimen.density_kg_m3`、`specimen.damping`。
- **阻断性**：阻断；可使用默认 seed，但必须加入 `assumptions`。

## 阶段 3：case 与裂隙几何

### 问题 3.1：是否保留第一个启用 case 为完整试件 `intact`？

- **默认**：是。
- **答案形状**：确认；固定状态为 `family: intact`、`enabled: true`、`crack_enabled: false`。
- **配置目标**：`cases[0].case_name`、`cases[0].family`、`cases[0].enabled`、`cases[0].crack_enabled`。
- **阻断性**：阻断；当前验证要求第一个 enabled case 是 `intact`。

### 问题 3.2：要登记哪一种裂隙 case？

- **默认**：登记一个 disabled 的 `straight_crack` 示例 `b0_d20`。
- **答案形状**：`none`、`straight_crack` 或 `polyline_reserved`；给出安全 `case_name`。
- **配置目标**：`cases[].case_name`、`cases[].family`、`cases[].enabled`、`cases[].crack_enabled`、`cases[].crack_type`。
- **阻断性**：非阻断；可只生成 intact。`polyline_reserved` 必须 `family: polyline_reserved`、`crack_type: polyline_reserved`、`crack_enabled: true`、`enabled: false`，只生成 schema，不切割。

### 问题 3.3：直线裂隙的几何参数是什么？

- **默认**：`angle_deg: 0.0`、`distance_mm: 20.0`、`length_mm: 20.0`、`width_mm: 3.0`、中心 `(0.0, 0.0) mm`。
- **答案形状**：角度、可选边界距离、正长度、正宽度、中心 x/y；长度和坐标统一为 mm。
- **配置目标**：`cases[].angle_deg`、`cases[].distance_mm`、`cases[].length_mm`、`cases[].width_mm`、`cases[].center_x_mm`、`cases[].center_y_mm`。
- **字段语义**：`distance_mm` 只登记 case 命名和论文自变量，不会隐式移动裂隙；实际位置由 `center_x_mm`、`center_y_mm` 明确控制。若论文中的边界距离需要换算为裂隙中心，必须先确认距离定义和方向，再把换算结果写入中心坐标，不能让 AI 猜测。
- **阻断性**：对 `straight_crack` 阻断；几何不全或越界不能作为有效配置。裂隙 case 在 intact runtime 通过前保持 disabled。

## 阶段 4：实验数据登记

### 问题 4.1：每个 case 的实验文件相对路径是什么？

- **默认**：`data/experimental/intact.xlsx`；裂隙例为 `data/experimental/b0_d20.xlsx`。
- **答案形状**：安全的项目相对路径，必须位于 `data/experimental/`，可为 `.xlsx` 或 `.csv`。
- **配置目标**：`cases[].experiment_file`。
- **阻断性**：路径格式阻断；文件当前不存在仅 warning，不阻断静态生成。

### 问题 4.2：实验列名、应力单位和应变定义是什么？

- **默认**：列名待确认；应力 `MPa`；应变为无量纲小数。
- **答案形状**：应力列名、应变列名（或力/位移列及换算说明）、各自单位、sheet 名（如适用）。
- **配置目标**：当前 `load_intake` 无对应独立字段，完整原文逐项写入 `assumptions`；不要杜撰同义配置字段。
- **阻断性**：对脚手架静态生成非阻断；对后续标定阻断。

## 阶段 5：颗粒与接触 seed 参数

### 问题 5.1：是否采用 LPBM 初始参数？

- **默认**：采用公开 intake 的 trial seed；`family: linearpbond`。
- **答案形状**：确认默认，或给出 `linear_emod_pa`、`bond_emod_pa`、`kratio`、`pb_ten_pa`、`pb_coh_pa`、`pb_fa_deg`、`friction` 的数值和来源。
- **配置目标**：`contact_model.family`、`contact_model.linear_emod_pa`、`contact_model.bond_emod_pa`、`contact_model.kratio`、`contact_model.pb_ten_pa`、`contact_model.pb_coh_pa`、`contact_model.pb_fa_deg`、`contact_model.friction`。
- **阻断性**：阻断；未知可用默认，但必须在 `assumptions` 中标为“trial seed，非最终标定值”。

### 问题 5.2：加载和峰后停止 seed 是什么？

- **默认**：`wall_velocity_m_s: 0.10`、`peak_drop_fraction: 0.75`、`target_peak_strain_guess: 0.08`、`history_interval: 10`。
- **答案形状**：正墙速、`(0,1)` 内峰后比例、正峰值应变猜测、正整数 history 间隔。
- **配置目标**：`loading.wall_velocity_m_s`、`loading.peak_drop_fraction`、`loading.target_peak_strain_guess`、`loading.history_interval`。
- **阻断性**：阻断；默认值属于假设时写入 `assumptions`。

## 阶段 6：输出与四阶段 contract

### 问题 6.1：是否采用标准输出和四个 stage？

- **默认**：`stress_strain: true`、`crack_counts: true`、`heavy_ae: false`，`stage_fractions: [0.25, 0.50, 0.75, 0.90]`。
- **答案形状**：三个布尔值，加恰好四个处于 `(0,1)` 且严格递增的比例。
- **配置目标**：`outputs.stress_strain`、`outputs.crack_counts`、`outputs.heavy_ae`、`loading.stage_fractions`。
- **阻断性**：标准输出和合法四 stage 阻断；v1 必须保持 `heavy_ae: false`，AE 不在首轮运行范围。

## 阶段 7：assumptions 审查

### 问题 7.1：以下假设是否完整、准确，并同意逐条写入？

- **默认**：汇总前 1–6 阶段所有默认 seed、单位换算、材料描述、实验列/单位、缺失文件、暂缓裂隙和未标定声明。
- **答案形状**：逐条“确认 / 修改 / 删除”，以及需要补充的单行文本。
- **配置目标**：顶层 `assumptions`（字符串列表）。
- **阻断性**：阻断；不得把未确认的 AI 推测静默写入，也不得遗漏已采用的假设。

## 阶段 8：显式确认与生成

### 问题 8.1：是否确认 intake 快照并允许执行静态预检和生成？

- **默认**：不自动确认。
- **答案形状**：明确的“确认生成”，同时确认输出目录；任何含糊回答都按未确认处理。
- **配置目标**：确认后的 `cpb2d_intake.yaml` 全量快照；输出目录是 CLI 参数 `--output-dir`，不是 YAML 字段。
- **阻断性**：阻断；未显式确认不得运行生成命令。

## 生成、验证与运行硬门槛

1. 先执行 `create_cpb2d_project.py --validate-only`，它是针对**拟输出目录**的预检；随后才静态生成项目。
2. **静态校验通过**只表示 intake、目录、manifest、模板占位符和文件 contract 可验证；不表示 PFC 语法或求解已运行成功。
3. 静态生成成功后，第一个且唯一允许的 PFC 运行目标是 `pfc_cases/intact/run_all.dat`。
4. **PFC runtime 通过**必须来自实际 PFC2D 6.0 执行，并核对 `sample`、`parallel_bonded`、`stage_a`–`stage_d`、`peak`、`final` 及 `stress_strain.csv`。未实际执行时必须写“runtime 未验证”，不得宣传脚手架已在 PFC 运行通过。
5. intact runtime 未通过前：**不运行裂隙批跑、不开始标定、不做后处理、不启用 AE**。
6. intact runtime 通过后，才可显式启用并运行 `straight_crack` case；`polyline_reserved` 仍保持 disabled，仅有 schema，不执行切割。
7. 后处理开始前先读 `pfc-postprocessing/references/script-catalog.md`，再读选中的实际脚本并按其真实接口执行。

## 已验证的 PFC6 runtime 基线

2026-07-20 使用本仓库公开 intake 生成的 `intact` case 完成真实运行验收：

- **程序版本**：PFC2D Version 6.00 Release 013，Build 0，Common 128。
- **运行入口**：仅运行 `pfc_cases/intact/run_all.dat`；未运行裂隙 case、标定、后处理或 AE。
- **运行结果**：通过；`sample.sav`、`parallel_bonded.sav`、`stage_a.sav`–`stage_d.sav`、`peak.sav` 和 `final.sav` 均生成且非空。
- **曲线输出**：`stress_strain.csv` 的表头为 `strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num`，包含数值数据行。
- **步级输出**：`stress_strain_step.csv` 的表头为 `step,strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num`，包含数值数据行。
- **裂纹输出**：`plotdata_fracture_orientations.csv` 的表头为 `angle_deg,type`，包含数值角度和裂纹类型。
- **Windows 注意事项**：通过 PFC 命令设置工作目录时使用正斜杠路径；反斜杠可能被 PFC 命令解析器吞掉。该注意事项只影响运行器传入的目录写法，不要求修改生成的项目源文件。

同一公开 intake 的 `b0_d20` 直线裂隙 case 也完成真实运行验收：

- **运行入口**：仅运行 `pfc_cases/b0_d20/run_all.dat`，任务 `8b0c9f` 完成；未运行其他案例、标定、后处理或 AE。
- **保存节点**：`sample.sav`、`parallel_bonded.sav`、`stage_a.sav`–`stage_d.sav`、`peak.sav` 和 `final.sav` 均生成且非空。
- **输出契约**：三个标准 CSV 均生成且包含数值数据；`stress_strain.csv` 536 行，`stress_strain_step.csv` 536 行，`plotdata_fracture_orientations.csv` 781 行。
- **实际裂隙几何**：水平裂隙中心为 `(0, 0) mm`，端点为 `(-10, 0) mm` 和 `(10, 0) mm`，法向半宽 `1.5 mm`，与生成的 `ball delete range cylinder` 命令一致。
- **删球证据**：`sample.sav` 有 2652 个球，`parallel_bonded.sav` 有 2549 个球；理论有限圆柱区域内的球心由 103 个降为 0，等面积上下邻带保持 200 个，PFC 日志同时报告 `103 balls deleted.`。这证明裂隙由真实删球形成，而不是换色或分组。
- **离散尺度**：实际球半径约 `0.300009–0.499963 mm`，因此可视空隙边缘相对理论边界允许约 `0.3–0.5 mm` 的颗粒离散偏差。
- **PFC6 范围语义**：该 build 下二维 `range cylinder` 表现为端平面截断的有限圆柱投影，即矩形带，而不是带半圆端帽的胶囊区。

上述结果只证明公开基线的 `intact` 和 `b0_d20` case 与该 PFC6 build 兼容；新项目仍须按本向导独立执行 runtime gate，不能直接据此跳过验证。
