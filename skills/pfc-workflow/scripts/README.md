# pfc-workflow scripts

## Script-first 规则

本目录的命令以**实际脚本源码**为准。选择、适配或运行任何命令前，先打开对应 `.py` 阅读 `argparse`、输入 contract、输出位置和副作用；不要仅凭本 README 或技能描述猜参数。

PFC 输出进入后处理前，先读 `pfc-postprocessing/references/script-catalog.md`，再读所选实际脚本（例如 `pfc-postprocessing/scripts/plot_curves.py`）。

## Route: Beginner scaffold

适用：从几何/实验数据开始的 **new project**，还没有可运行的四阶段 CPB2D case。

```text
references/cpb2d-project-wizard.md
-> templates/cpb2d_intake.yaml
-> scripts/create_cpb2d_project.py
-> pfc_cases/intact/run_all.dat
-> enabled straight-crack run_all.dat
-> pfc-postprocessing/references/script-catalog.md
```

1. 向导一次只问一个问题，确认 `assumptions` 和 intake 快照。
2. `--validate-only` 是针对 `--output-dir` 指定的**拟输出目录**做预检：加载 intake、显示 enabled case 顺序并计算该目录下缺失实验文件 warning；它不创建目录，也不执行 PFC。
3. 静态生成通过仅说明文件、manifest 和模板 contract 可验证，不代表 PFC runtime 通过。
4. 第一个 PFC 目标固定为 `pfc_cases/intact/run_all.dat`。intact 未在 PFC2D 6.0 实际运行并核对保存节点/CSV 前，不进行裂隙批跑、标定、后处理或 AE。
5. `templates/project-case/` **不是**新项目 scaffold source，不要把其历史项目逻辑复制到 beginner route。

本机可将 `PFC_PYTHON` 设置为用户选择的 Python 3.12 解释器。公开命令通过环境变量调用，不绑定固定盘符或用户私有路径：

```powershell
# PowerShell
& $env:PFC_PYTHON skills\pfc-workflow\scripts\create_cpb2d_project.py `
  --from-intake skills\pfc-workflow\templates\cpb2d_intake.yaml `
  --output-dir cpb2d_beginner_demo `
  --validate-only
```

```bash
# Git Bash/MSYS
"$PFC_PYTHON" skills/pfc-workflow/scripts/create_cpb2d_project.py \
  --from-intake skills/pfc-workflow/templates/cpb2d_intake.yaml \
  --output-dir cpb2d_beginner_demo \
  --validate-only
```

移除 `--validate-only` 才会生成。已有输出目录默认拒绝；`--force` 仅接受带有效 `scaffold_manifest.json` 的受管项目，并在覆盖前校验受管文件 hash。任何受管文件被手工修改时，`--force` 会拒绝覆盖；它不会把未知目录当作脚手架项目清空。

### Stage 与 peak 语义

- `stage_a`–`stage_d` 的正常语义是按 `target_peak_strain_guess * stage_fractions` 首次跨越阈值时保存。
- 若求解停止前某个阈值没有到达，脚本会按 A–D 顺序保存缺失节点为 **fallback final state**。这种 fallback 只满足文件 contract，不表示该状态真实达到对应阶段。
- `peak` 的正常语义是经连续下降确认的近峰值/峰后状态；若未确认峰值，最终 fallback 会保存当前状态以保证节点存在。fallback peak 不得当作经验证的真实峰值。
- runbook/结果报告必须区分正常 stage、fallback stage、confirmed peak 和 fallback peak。

## Route: Existing project-case

适用：**existing project-case**，即已有完整、项目专用的 case 文件夹及其配置/导出链。

入口是 `templates/project-case/run_case.py`。先读 `run_case.py` 和同目录 `config.py`、生成/导出/后处理脚本，再根据它们的实际 CLI 和环境依赖运行。该路线包含项目专用桥接、PFC console、原生导出与 ParaView/Python 后处理能力，不能当作通用 beginner scaffold 模板。

## Route: Automated calibration

适用：intact 已经 PFC runtime 通过、实验 contract 已确认、基础 case 可重复运行之后的 **automated calibration**。先读每个脚本和 `_campaign_common.py`，再按 campaign YAML 的真实 schema 执行：

```text
lhs_design.py -> run_campaign.py -> fit_surrogate.py -> optimize_targets.py
```

- `lhs_design.py`：从 calibration campaign YAML 生成 LHS 样本。
- `run_campaign.py`：评估候选点并维护 `runs.csv`，支持 `--resume` 和 `--limit`。
- `fit_surrogate.py`：从已完成 runs 拟合并保存代理模型/报告。
- `optimize_targets.py`：按 `bayes`、`rsm` 或 `de` 优化目标，并继续调用实际 case evaluator。

这条路线不是脚手架生成步骤。intact runtime 未通过、实验列与单位未确认或 seed 尚不能稳定复现时，不得启动自动标定。
