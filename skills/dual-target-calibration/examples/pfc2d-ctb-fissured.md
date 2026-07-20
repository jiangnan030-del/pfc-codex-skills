# 项目实例：PFC2D 裂隙 CTB（v1 实测先验，199 试算 / 13 模型）

> ⚠️ 新项目不要直接套用数值，只复用方法。

## 适配器参考实现
| 通用接口 | 原实现 |
| --- | --- |
| submit(params) | `_submit_pfc.py`（websocket 提交 run_calib.py；参数在 `pfc_models/fissured/aXX_wX/2bond.dat`） |
| check(trial) | `_chk.py`（读 trial CSV，对比 targets 字典） |
| target() | `_tgt.py`（读项目根目录实验 Excel，如 `45-6-7.xlsx`） |
| 回归脚本 | `_reg.py`（按模型重写）；归档 `fissured_calibration_parameters.md` / `calibration_experience.md` |

## 外推先验（S2 项目系数）
- 固定：`pb_coh = 2×pb_ten`，`pb_fa = 27.0`，`krat = 1.5`，`gap = 3.5e-5`，`dp_nratio = 0.5`
- 角度趋势：30° emod ≈ 0.82 × 同宽度 0°；45° w3 ≈ 1.17 × 0°，w4–w6 每档 ×0.85 链式递推
- pb_fa 仅 0° 系列有效；30°/45° 斜裂隙零效应；krat=2.0 是 a30_w6 的破局手段

## 角度-宽度先验图（已标定 emod，单位 1e6）
| 角度 | w3 | w4 | w5 | w6 | 趋势 |
| --- | --- | --- | --- | --- | --- |
| 0° | 9.4 | 12.5 | 11.0 | 4.3 | w4 峰值，w6 断崖 |
| 30° | 7.7 | 7.1 | 3.9 | 1.86 | 单调下降，两处断崖 |
| 45° | 10.98 | 9.34 | 5.64 | 4.32 | 单调下降，w5 断崖 |

- 45° 刚度最高（w3 处 E=11.92）——剪切主导破坏反而更强（反直觉）
- w5–w6 段所有角度 emod 均塌到 < 6e6，多盆地现象集中出现

## 实测盆地边界样本
- a45_w6：安全区 emod ∈ [4.20, 4.21]（pb=0.96）；4.19 或 4.23 即触发应变跳变 > 5%
- a30_w6：emod < 1.77e6 后应变响应不连续；a30 系 w5–w6 两处 dS/demod 变号断崖
- a45_w3：emod=10.8 时 pb_ten 1.65→1.64 即使应变误差 −1.26% → −6.18%
- 盆地恢复成功例（a45_w6）：T4/T5 + T8/T12 → 5 点最小二乘 → emod=4.318, pb=0.977 → T14 PASS

## 实测敏感度比值样本
- emod：dUCS:dS 从 6.5:1（a45_w5）到 1:1（a45_w6 窄盆地）
- pb_ten：低 emod 区高达 37:1（a45_w6 T1, emod=3.9），中 emod 区 2.6:1
- pb_coh 单独调到 2.06× 使应变恶化 2.6%；dp_nratio 0.5→0.4 零效应
