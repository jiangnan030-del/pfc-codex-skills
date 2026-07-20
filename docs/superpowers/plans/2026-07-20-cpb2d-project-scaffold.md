# CPB2D Project Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `pfc-workflow` 增加面向小白的 CPB/PFC2D UCS 问诊流程和确定性项目脚手架，使用户能从完整试件、参数化直线裂隙及实验数据登记出发，生成命名规范、静态可验证、可进入 PFC2D 试运行和现有后处理流程的项目。

**Architecture:** `pfc-workflow` 负责逐题问诊和路由；`create_cpb2d_project.py` 仅负责 CLI 与文件系统事务；`cpb2d_scaffold.py` 负责配置解析、单位转换、case 校验、裂隙端点计算、模板渲染和 manifest 自检。PFC 源文件保存在独立模板目录，用 Python `string.Template` 渲染，避免 AI 临时拼写和新增 Jinja 依赖；生成后的 CSV 契约与 `pfc-postprocessing` 保持一致。

**Tech Stack:** Python 3.12、标准库 `argparse/csv/dataclasses/json/pathlib/string`、PyYAML 6.x、pytest 9.x、PFC2D 6.0 `.dat/.p2fis` 模板、现有 `validate_skills.py`。

---

## File Map

**Create**

- `skills/pfc-workflow/scripts/cpb2d_scaffold.py`：配置模型、校验、单位换算、裂隙端点、模板渲染、目录事务和 manifest。
- `skills/pfc-workflow/scripts/create_cpb2d_project.py`：稳定 CLI，不包含 PFC 模板正文。
- `skills/pfc-workflow/scripts/README.md`：脚本入口、依赖、调用顺序和 script-first 规则。
- `skills/pfc-workflow/templates/cpb2d_intake.yaml`：可复制的问诊输出样例。
- `skills/pfc-workflow/templates/cpb2d-scaffold/1model.dat.tpl`：成样模板。
- `skills/pfc-workflow/templates/cpb2d-scaffold/2bond.dat.tpl`：成键和可选裂隙模板。
- `skills/pfc-workflow/templates/cpb2d-scaffold/3load.dat.tpl`：UCS、A-D/peak/final 保存模板。
- `skills/pfc-workflow/templates/cpb2d-scaffold/4export.dat.tpl`：应力-应变和裂纹统计导出模板。
- `skills/pfc-workflow/templates/cpb2d-scaffold/fracture.p2fis`：非 heavy-AE 裂纹追踪模板。
- `skills/pfc-workflow/templates/cpb2d-scaffold/run_all.dat.tpl`：单一运行入口。
- `skills/pfc-workflow/references/cpb2d-project-wizard.md`：逐题问诊、默认值、假设记录和技能路由。
- `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`：领域逻辑与生成集成测试。
- `skills/pfc-workflow/tests/fixtures/intake_minimal.yaml`：intact + `b0_d20` 固定测试输入。

**Modify**

- `skills/pfc-workflow/SKILL.md:173`：在 Default workflow 前加入新项目触发门和小白问诊规则。
- `skills/pfc-workflow/SKILL.md:366`：在 Bundled scripts 中登记脚手架及读取顺序。
- `skills/pfc-workflow/SKILL.md:379`：区分“从零 scaffold route”和“已有 case complete route”。
- `skills/pfc-workflow/SKILL.md:475`：登记新 reference、template、script 和 tests。
- `skills/pfc-workflow/templates/scope.md:1`：从空白清单升级为 CPB2D intake contract，同时保留非 CPB 项目通用字段。
- `skills/pfc-postprocessing/references/data-contract.md:5`：确认脚手架导出的 `stress_strain.csv` 兼容 required/optional 列。
- `references/skill-index.md:1`：通过验证脚本重新生成。

**Do Not Modify**

- `templates/project-case/`：它服务“已有完整 case 的专家运行器”，不得与新项目脚手架混合。
- `pfc-ae-energy/`：第一版不生成 heavy AE。
- 工作区的 `Reference intact/`、`Reference crack/`：只作为设计依据，不复制 `.sav`、结果数据或私有项目文件。

---

### Task 1: Establish Config Models and Validation

**Files:**
- Create: `skills/pfc-workflow/scripts/cpb2d_scaffold.py`
- Create: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`
- Create: `skills/pfc-workflow/tests/fixtures/intake_minimal.yaml`

- [x] **Step 1: Write failing tests for slug, specimen, case, and unit validation**

```python
# skills/pfc-workflow/tests/test_cpb2d_scaffold.py
from pathlib import Path
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from cpb2d_scaffold import ConfigError, load_intake


def test_load_minimal_intake_normalizes_si_values():
    cfg = load_intake(Path(__file__).parent / "fixtures" / "intake_minimal.yaml")
    assert cfg.project.slug == "cpb_2d_ucs_demo"
    assert cfg.specimen.width_m == pytest.approx(0.04)
    assert cfg.specimen.radius_min_m == pytest.approx(0.0003)
    assert [case.name for case in cfg.cases] == ["intact", "b0_d20"]


@pytest.mark.parametrize("slug", ["我的项目", "CPB Demo", "cpb-demo", "../cpb"])
def test_project_slug_rejects_unsafe_names(tmp_path, slug):
    intake = tmp_path / "bad.yaml"
    intake.write_text(f"project:\n  slug: {slug!r}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="project.slug"):
        load_intake(intake)


def test_non_positive_particle_radius_is_rejected(tmp_path):
    intake = tmp_path / "bad.yaml"
    intake.write_text(
        "project:\n  slug: cpb_demo\n"
        "specimen:\n  particle_radius_min_mm: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="particle_radius_min_mm"):
        load_intake(intake)
```

- [x] **Step 2: Add the deterministic fixture**

```yaml
# skills/pfc-workflow/tests/fixtures/intake_minimal.yaml
project:
  slug: cpb_2d_ucs_demo
  title: CPB 2D UCS demo
  pfc_version: "6.0"
  random_seed_base: 31000
specimen:
  width_mm: 40.0
  height_mm: 40.0
  particle_radius_min_mm: 0.30
  particle_radius_max_mm: 0.50
  target_porosity: 0.15
  density_kg_m3: 1900.0
  damping: 0.70
contact_model:
  family: linearpbond
  linear_emod_pa: 2200000.0
  bond_emod_pa: 1000000.0
  kratio: 1.5
  pb_ten_pa: 50000.0
  pb_coh_pa: 80000.0
  pb_fa_deg: 27.0
  friction: 0.8
loading:
  wall_velocity_m_s: 0.10
  peak_drop_fraction: 0.75
  target_peak_strain_guess: 0.08
  stage_fractions: [0.25, 0.50, 0.75, 0.90]
  history_interval: 10
outputs:
  stress_strain: true
  crack_counts: true
  heavy_ae: false
cases:
  - case_name: intact
    family: intact
    enabled: true
    experiment_file: data/experimental/intact.xlsx
    crack_enabled: false
  - case_name: b0_d20
    family: straight_crack
    enabled: true
    experiment_file: data/experimental/b0_d20.xlsx
    crack_enabled: true
    crack_type: straight
    angle_deg: 0.0
    distance_mm: 20.0
    length_mm: 20.0
    width_mm: 3.0
    center_x_mm: 0.0
    center_y_mm: 0.0
```

- [x] **Step 3: Run tests and verify they fail**

Run:

```bash
cd pfc-codex-skills
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -v
```

Expected: collection fails with `ModuleNotFoundError: No module named 'cpb2d_scaffold'`.

- [x] **Step 4: Implement typed config loading and validation**

Implement these public types and signatures in `cpb2d_scaffold.py`:

```python
class ConfigError(ValueError):
    pass

@dataclass(frozen=True)
class ProjectConfig:
    slug: str
    title: str
    pfc_version: str
    random_seed_base: int

@dataclass(frozen=True)
class SpecimenConfig:
    width_mm: float
    height_mm: float
    radius_min_mm: float
    radius_max_mm: float
    porosity: float
    density_kg_m3: float
    damping: float

    @property
    def width_m(self) -> float: return self.width_mm / 1000.0
    @property
    def height_m(self) -> float: return self.height_mm / 1000.0
    @property
    def radius_min_m(self) -> float: return self.radius_min_mm / 1000.0
    @property
    def radius_max_m(self) -> float: return self.radius_max_mm / 1000.0

@dataclass(frozen=True)
class ContactConfig: ...
@dataclass(frozen=True)
class LoadingConfig: ...
@dataclass(frozen=True)
class OutputConfig: ...
@dataclass(frozen=True)
class CaseConfig: ...
@dataclass(frozen=True)
class ScaffoldConfig: ...

def load_intake(path: Path) -> ScaffoldConfig: ...
def validate_config(config: ScaffoldConfig) -> list[str]: ...
```

Validation rules must be exact:

- `project.slug`: `^[a-z0-9]+(?:_[a-z0-9]+)*$`.
- `pfc_version`: first release accepts only string `"6.0"`.
- width/height/radii/density/wall velocity must be positive.
- `0 < porosity < 1`, `0 <= damping <= 1`, `0 < peak_drop_fraction < 1`.
- `radius_min_mm <= radius_max_mm`.
- `stage_fractions` must contain exactly four strictly increasing values in `(0, 1)`.
- first enabled case must be `intact`; duplicate names are errors.
- `intact` may not enable a crack.
- straight crack requires angle, length, width, center coordinates.
- `polyline_reserved` is allowed only with `enabled: false`.
- missing experimental files are not checked in `load_intake`; they become generation warnings.

Use `yaml.safe_load`; do not add a second YAML library.

- [x] **Step 5: Run tests and verify they pass**

Run the Step 3 command.

Expected: all Task 1 tests pass.

- [x] **Step 6: Commit**

```bash
git add skills/pfc-workflow/scripts/cpb2d_scaffold.py \
  skills/pfc-workflow/tests/test_cpb2d_scaffold.py \
  skills/pfc-workflow/tests/fixtures/intake_minimal.yaml
git commit -m "feat: add CPB2D scaffold configuration contract"
```

---

### Task 2: Implement Straight-Crack Geometry and Render Context

**Files:**
- Modify: `skills/pfc-workflow/scripts/cpb2d_scaffold.py`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`

- [x] **Step 1: Write failing geometry tests**

```python
from cpb2d_scaffold import crack_geometry, render_context


def test_horizontal_crack_endpoints_are_in_metres():
    cfg = load_intake(FIXTURE)
    crack = crack_geometry(cfg.cases[1], cfg.specimen)
    assert crack.end1_m == pytest.approx((-0.01, 0.0))
    assert crack.end2_m == pytest.approx((0.01, 0.0))
    assert crack.radius_m == pytest.approx(0.0015)


def test_crack_outside_specimen_is_rejected():
    cfg = load_intake(FIXTURE)
    bad = replace(cfg.cases[1], center_x_mm=19.0, length_mm=20.0)
    with pytest.raises(ConfigError, match="outside specimen"):
        crack_geometry(bad, cfg.specimen)


def test_case_seed_is_deterministic_and_distinct():
    cfg = load_intake(FIXTURE)
    intact = render_context(cfg, cfg.cases[0], 0)
    crack = render_context(cfg, cfg.cases[1], 1)
    assert intact["random_seed"] == 31000
    assert crack["random_seed"] == 31001
```

Define `FIXTURE = Path(__file__).parent / "fixtures" / "intake_minimal.yaml"` once at module scope.

- [x] **Step 2: Run focused tests and verify failure**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -k "crack or seed" -v
```

Expected: import failure for `crack_geometry` or `render_context`.

- [x] **Step 3: Implement geometry and render context**

Add:

```python
@dataclass(frozen=True)
class CrackGeometry:
    end1_m: tuple[float, float]
    end2_m: tuple[float, float]
    radius_m: float


def crack_geometry(case: CaseConfig, specimen: SpecimenConfig) -> CrackGeometry:
    half = case.length_mm / 2000.0
    angle = math.radians(case.angle_deg)
    cx, cy = case.center_x_mm / 1000.0, case.center_y_mm / 1000.0
    dx, dy = half * math.cos(angle), half * math.sin(angle)
    result = CrackGeometry((cx - dx, cy - dy), (cx + dx, cy + dy), case.width_mm / 2000.0)
    # Reject when an endpoint leaves +/- width/2 or +/- height/2.
    ...
    return result


def render_context(config: ScaffoldConfig, case: CaseConfig, case_index: int) -> dict[str, str | int | float]:
    ...
```

`render_context` must expose SI values with stable scientific notation left to the templates, stage strains calculated as `target_peak_strain_guess * fraction`, and `crack_command` equal to an empty comment for intact or one complete `ball delete range cylinder ...` line for straight cracks.

Emit a warning string when `width_mm < 2 * particle_radius_max_mm`; do not reject it.

- [x] **Step 4: Run tests and verify pass**

Run Step 2 command, then the full Task 1 suite.

- [x] **Step 5: Commit**

```bash
git add skills/pfc-workflow/scripts/cpb2d_scaffold.py skills/pfc-workflow/tests/test_cpb2d_scaffold.py
git commit -m "feat: add deterministic CPB2D crack geometry"
```

---

### Task 3: Add PFC2D Source Templates

**Files:**
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/1model.dat.tpl`
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/2bond.dat.tpl`
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/3load.dat.tpl`
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/4export.dat.tpl`
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/fracture.p2fis`
- Create: `skills/pfc-workflow/templates/cpb2d-scaffold/run_all.dat.tpl`
- Modify: `skills/pfc-workflow/scripts/cpb2d_scaffold.py`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`

- [x] **Step 1: Write failing template contract tests**

```python
from cpb2d_scaffold import render_case_files

REQUIRED_CASE_FILES = {
    "1model.dat", "2bond.dat", "3load.dat", "4export.dat",
    "fracture.p2fis", "run_all.dat",
}


def test_rendered_intact_has_complete_stage_and_export_contract():
    cfg = load_intake(FIXTURE)
    files = render_case_files(cfg, cfg.cases[0], 0)
    assert set(files) == REQUIRED_CASE_FILES
    assert "model save 'sample'" in files["1model.dat"]
    assert "ball delete range cylinder" not in files["2bond.dat"]
    assert all(f"model save '{name}'" in files["3load.dat"] for name in [
        "stage_a", "stage_b", "stage_c", "stage_d", "peak", "final"
    ])
    assert "strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num" in files["4export.dat"]


def test_rendered_crack_uses_linearpbond_and_parameterized_cylinder():
    cfg = load_intake(FIXTURE)
    files = render_case_files(cfg, cfg.cases[1], 1)
    assert "contact model linearpbond" in files["2bond.dat"]
    assert "ball delete range cylinder" in files["2bond.dat"]
    assert "-1.000000e-02" in files["2bond.dat"]
    assert "1.500000e-03" in files["2bond.dat"]


def test_run_all_is_single_ordered_entrypoint():
    cfg = load_intake(FIXTURE)
    text = render_case_files(cfg, cfg.cases[0], 0)["run_all.dat"]
    assert text.splitlines() == [
        "program call '1model.dat'",
        "program call '2bond.dat'",
        "program call '3load.dat'",
        "program call '4export.dat'",
    ]
```

- [x] **Step 2: Run focused tests and verify failure**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -k rendered -v
```

Expected: import failure for `render_case_files`.

- [x] **Step 3: Add minimal PFC templates derived from public/canonical sources**

Use `string.Template` placeholders only. Required PFC behavior:

- `1model.dat.tpl`: `model new`, title, domain, fixed random seed, 40×40 mm-style box, ball distribution, linear CMAT, density/damping, calm/solve, save `sample`.
- `2bond.dat.tpl`: restore `sample`, insert `${crack_command}`, assign `linearpbond`, bond gap/deformability/strength/friction, delete side walls IDs 2 and 4, settle, save `parallel_bonded`.
- `3load.dat.tpl`: restore bonded state; define stress/strain monitor; load walls IDs 1/3; call `fracture.p2fis`; register histories; save A-D in ascending threshold order; save peak only after stress decline; halt at `peak_drop_fraction`; ensure peak exists; save final.
- `4export.dat.tpl`: export `stress_strain.csv` with exactly the postprocessing-required `strain,stress_mpa` plus crack columns; export `stress_strain_step.csv`; export `plotdata_fracture_orientations.csv` only if the fracture template provides records.
- `fracture.p2fis`: use the non-heavy-AE PFC6 UCS callback pattern from `pfc-standard-tests/scripts/canonical/ucs/fracture.p2fis`, extend only tension/shear counters and orientation records required by `4export.dat`; do not include moment tensors or AE arrays.
- `run_all.dat.tpl`: exactly four ordered `program call` lines.

No template may contain a Windows drive path, user case name outside placeholders, or heavy-AE symbols.

- [x] **Step 4: Implement renderer with strict placeholder checking**

```python
def render_template(name: str, context: Mapping[str, object]) -> str:
    template_path = TEMPLATE_ROOT / name
    return Template(template_path.read_text(encoding="utf-8-sig")).substitute(context)


def render_case_files(config: ScaffoldConfig, case: CaseConfig, case_index: int) -> dict[str, str]:
    context = render_context(config, case, case_index)
    return {
        "1model.dat": render_template("1model.dat.tpl", context),
        "2bond.dat": render_template("2bond.dat.tpl", context),
        "3load.dat": render_template("3load.dat.tpl", context),
        "4export.dat": render_template("4export.dat.tpl", context),
        "fracture.p2fis": (TEMPLATE_ROOT / "fracture.p2fis").read_text(encoding="utf-8-sig"),
        "run_all.dat": render_template("run_all.dat.tpl", context),
    }
```

`Template.substitute`, not `safe_substitute`, is required so missing placeholders fail tests.

- [x] **Step 5: Run tests and inspect generated source snippets**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -v
```

Expected: all tests pass. Also assert in tests that rendered files contain no `${...}` and no `ghp_`, `C:\`, `D:\`, or `E:\`.

- [x] **Step 6: Commit**

```bash
git add skills/pfc-workflow/templates/cpb2d-scaffold \
  skills/pfc-workflow/scripts/cpb2d_scaffold.py \
  skills/pfc-workflow/tests/test_cpb2d_scaffold.py
git commit -m "feat: add reusable CPB2D PFC source templates"
```

---

### Task 4: Implement Transactional Project Generation and CLI

**Files:**
- Create: `skills/pfc-workflow/scripts/create_cpb2d_project.py`
- Modify: `skills/pfc-workflow/scripts/cpb2d_scaffold.py`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`

- [x] **Step 1: Write failing integration tests for the generated tree**

```python
from cpb2d_scaffold import create_project


def test_create_project_writes_mixed_tree_and_manifest(tmp_path):
    result = create_project(FIXTURE, tmp_path / "cpb_2d_ucs_demo")
    root = result.root
    assert (root / "README_runbook.md").exists()
    assert (root / "project_config.yaml").exists()
    assert (root / "cases.csv").exists()
    for case in ["intact", "b0_d20"]:
        assert {p.name for p in (root / "pfc_cases" / case).iterdir()} == REQUIRED_CASE_FILES
    assert result.warnings == [
        "missing experiment file: data/experimental/intact.xlsx",
        "missing experiment file: data/experimental/b0_d20.xlsx",
    ]
    manifest = json.loads((root / "scaffold_manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_order"] == ["intact", "b0_d20"]


def test_existing_output_is_rejected_without_force(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        create_project(FIXTURE, output)


def test_force_replaces_only_scaffold_managed_tree(tmp_path):
    output = tmp_path / "project"
    create_project(FIXTURE, output)
    user_file = output / "reports" / "user_notes.md"
    user_file.write_text("keep", encoding="utf-8")
    create_project(FIXTURE, output, force=True)
    assert user_file.read_text(encoding="utf-8") == "keep"
```

- [x] **Step 2: Run focused tests and verify failure**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -k create_project -v
```

Expected: import failure for `create_project`.

- [x] **Step 3: Implement managed-file generation**

Add:

```python
@dataclass(frozen=True)
class CreateResult:
    root: Path
    warnings: list[str]
    managed_files: list[str]


def create_project(intake_path: Path, output_dir: Path, *, force: bool = False) -> CreateResult: ...
def validate_generated_project(root: Path) -> list[str]: ...
```

Generation must write:

- root config and normalized `cases.csv`;
- `data/experimental/`, `geometry/cracks/`, `pfc_cases/`, `calibration/trials/`, `postprocess/`, `figures/`, `tables/`, `reports/`;
- `calibration/targets.csv` with status `missing_experiment` or `registered`;
- `calibration/parameter_bounds.yaml` with explicit seed ranges and “not final calibrated values” note;
- `postprocess/manifest.csv` mapping `stress_strain.csv` to `pfc-postprocessing/scripts/plot_curves.py` and later optional files to their owning scripts;
- `README_runbook.md` with exact intact-first commands and expected artifacts;
- `reports/modeling_notes.md` with assumptions copied from intake;
- `geometry/cracks/README.md` and polyline CSV schema;
- `scaffold_manifest.json` containing schema version, managed files, warnings, cases and run order.

Write into a sibling temporary directory and rename only after all static checks pass. Under `force=True`, delete/replace only paths listed in the prior `scaffold_manifest.json`; refuse force if no manifest exists. This prevents deleting an unrelated user project.

- [x] **Step 4: Implement CLI wrapper**

```python
# create_cpb2d_project.py
from cpb2d_scaffold import ConfigError, create_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a reproducible CPB2D UCS project scaffold")
    parser.add_argument("--from-intake", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    return parser
```

`--validate-only` loads the intake, prints normalized case order and warnings, and does not create directories. Exit codes: `0` success, `2` config/user error, `1` unexpected failure.

Do not implement the colon-packed `--straight-crack` shortcut in v1; the approved intake YAML is the single source of truth and avoids duplicate parsers.

- [x] **Step 5: Run integration tests and CLI smoke test**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -v
rm -rf .tmp_cpb2d_scaffold
/e/Python312/python.exe skills/pfc-workflow/scripts/create_cpb2d_project.py \
  --from-intake skills/pfc-workflow/tests/fixtures/intake_minimal.yaml \
  --output-dir .tmp_cpb2d_scaffold
find .tmp_cpb2d_scaffold -maxdepth 3 -type f | sort
rm -rf .tmp_cpb2d_scaffold
```

Expected: tests pass; CLI reports two missing experiment warnings; generated tree includes both cases; cleanup leaves no tracked output.

- [x] **Step 6: Commit**

```bash
git add skills/pfc-workflow/scripts/create_cpb2d_project.py \
  skills/pfc-workflow/scripts/cpb2d_scaffold.py \
  skills/pfc-workflow/tests/test_cpb2d_scaffold.py
git commit -m "feat: generate transactional CPB2D projects"
```

---

### Task 5: Add Beginner Intake, Runbook Contract, and Script Documentation

**Files:**
- Create: `skills/pfc-workflow/templates/cpb2d_intake.yaml`
- Create: `skills/pfc-workflow/references/cpb2d-project-wizard.md`
- Create: `skills/pfc-workflow/scripts/README.md`
- Modify: `skills/pfc-workflow/templates/scope.md`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`

- [x] **Step 1: Write failing documentation/fixture parity test**

```python
def test_public_intake_example_is_loadable_and_matches_fixture_contract():
    public = Path(__file__).resolve().parents[1] / "templates" / "cpb2d_intake.yaml"
    cfg = load_intake(public)
    assert cfg.cases[0].name == "intact"
    assert cfg.outputs.heavy_ae is False
    assert cfg.loading.stage_fractions == (0.25, 0.50, 0.75, 0.90)
```

- [x] **Step 2: Run test and verify failure**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -k public_intake -v
```

Expected: `FileNotFoundError` for `templates/cpb2d_intake.yaml`.

- [x] **Step 3: Create public intake and wizard guide**

`cpb2d_intake.yaml` must be a valid, loadable intact + disabled straight-crack example, with comments explaining units and seed parameters.

`cpb2d-project-wizard.md` must define one-question-at-a-time order:

1. project/PFC version/material;
2. specimen dimensions and units;
3. intact/straight/polyline-reserved geometry;
4. experiment path/columns/units;
5. seed particle/contact parameters;
6. output contract;
7. assumption review;
8. explicit confirmation before generation.

For every question, include default, accepted answer shape, config destination, and blocking/non-blocking behavior. Include the hard gate: no calibration, postprocessing or AE until `intact/run_all.dat` exists and static validation passes.

- [x] **Step 4: Rewrite `templates/scope.md` as an intake worksheet**

Retain generic problem/loading/observables headings, then add exact CPB2D fields matching `load_intake`. Do not create alternative names such as `particle_min`; documentation must use `particle_radius_min_mm` exactly.

- [x] **Step 5: Add workflow script README**

Document:

```text
Beginner new project:
  cpb2d-project-wizard.md
  -> cpb2d_intake.yaml
  -> create_cpb2d_project.py
  -> intact/run_all.dat
  -> b*_d*/run_all.dat
  -> pfc-postprocessing script catalog

Existing calibrated project:
  templates/project-case/run_case.py

Automated calibration:
  lhs_design.py -> run_campaign.py -> fit_surrogate.py -> optimize_targets.py
```

Explicitly state that `templates/project-case/` is not a scaffold source and that scripts must be read before adaptation.

- [x] **Step 6: Run tests and publication validation**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -v
/e/Python312/python.exe scripts/validate_skills.py
```

Expected: tests pass and `Validation summary: 0 error(s), 0 warning(s)`.

- [x] **Step 7: Commit**

```bash
git add skills/pfc-workflow/templates/cpb2d_intake.yaml \
  skills/pfc-workflow/templates/scope.md \
  skills/pfc-workflow/references/cpb2d-project-wizard.md \
  skills/pfc-workflow/scripts/README.md \
  skills/pfc-workflow/tests/test_cpb2d_scaffold.py
git commit -m "docs: add CPB2D beginner project wizard"
```

---

### Task 6: Wire the Scaffold into `pfc-workflow`

**Files:**
- Modify: `skills/pfc-workflow/SKILL.md:74-205`
- Modify: `skills/pfc-workflow/SKILL.md:366-480`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`

- [ ] **Step 1: Write failing skill-wiring test**

```python
def test_workflow_skill_enforces_beginner_scaffold_gate():
    skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")
    required = [
        "CPB2D Beginner Project Gate",
        "references/cpb2d-project-wizard.md",
        "scripts/create_cpb2d_project.py",
        "intact",
        "pfc-postprocessing/references/script-catalog.md",
    ]
    for marker in required:
        assert marker in skill
    assert "Do not start calibration, post-processing, or AE" in skill
```

- [ ] **Step 2: Run test and verify failure**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests/test_cpb2d_scaffold.py -k workflow_skill -v
```

Expected: fails because the gate heading/markers are absent.

- [ ] **Step 3: Add the beginner project gate to `SKILL.md`**

Insert after `When to use` and before general `First rules`:

```markdown
## CPB2D Beginner Project Gate

Use this gate when the user starts from geometry/experimental data and does not already have a runnable four-stage PFC case. Read `references/cpb2d-project-wizard.md`, ask one question at a time, write/confirm the intake, validate it, then use `scripts/create_cpb2d_project.py`.

Do not start calibration, post-processing, or AE until the scaffold exists, static validation passes, and `pfc_cases/intact/run_all.dat` is the declared first run target.
```

Also distinguish routes:

- new CPB2D UCS project → scaffold route;
- existing case folders → current complete case route;
- non-CPB standard test → `pfc-standard-tests`;
- fields/figures → `pfc-postprocessing` script-first;
- heavy AE → only after standard files and stages exist.

Update Bundled scripts and Local Contents with exact new paths.

- [ ] **Step 4: Run wiring test and all workflow tests**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/pfc-workflow/SKILL.md skills/pfc-workflow/tests/test_cpb2d_scaffold.py
git commit -m "feat: route beginners through CPB2D project scaffold"
```

---

### Task 7: Verify Postprocessing Compatibility and Repository Hygiene

**Files:**
- Modify: `skills/pfc-postprocessing/references/data-contract.md:5-18`
- Modify: `skills/pfc-workflow/tests/test_cpb2d_scaffold.py`
- Modify: `references/skill-index.md`

- [ ] **Step 1: Add generated CSV contract and static-source tests**

```python
def test_export_contract_matches_postprocessing_required_columns():
    cfg = load_intake(FIXTURE)
    export = render_case_files(cfg, cfg.cases[0], 0)["4export.dat"]
    assert "strain,stress_mpa" in export
    contract = (
        Path(__file__).resolve().parents[2]
        / "pfc-postprocessing" / "references" / "data-contract.md"
    ).read_text(encoding="utf-8")
    assert "`strain`" in contract and "`stress_mpa`" in contract


def test_rendered_sources_have_no_private_paths_or_unresolved_placeholders():
    cfg = load_intake(FIXTURE)
    for index, case in enumerate(cfg.cases):
        for name, text in render_case_files(cfg, case, index).items():
            assert "${" not in text, name
            assert not re.search(r"[A-Za-z]:\\\\", text), name
            assert "ghp_" not in text, name
            assert "fig9_" not in text, name
            assert "moment_tensor" not in text.lower(), name
```

- [ ] **Step 2: Clarify the postprocessing contract**

Add a short “CPB2D scaffold producer” note to `data-contract.md`:

- producer: `pfc-workflow/scripts/create_cpb2d_project.py` generated `4export.dat`;
- guaranteed required columns: `strain`, `stress_mpa`;
- optional crack columns: `crack_num`, `crack_tension_num`, `crack_shear_num`;
- consumer: `pfc-postprocessing/scripts/plot_curves.py` after reading its actual source.

Do not change `plot_curves.py` unless the generated demo exposes a real incompatibility.

- [ ] **Step 3: Run complete automated checks**

```bash
/e/Python312/python.exe -m pytest skills/pfc-workflow/tests -v
/e/Python312/python.exe scripts/validate_skills.py --write-index
/e/Python312/python.exe scripts/validate_skills.py
```

Expected: all tests pass; publication validation reports zero errors and zero warnings.

- [ ] **Step 4: Run a generated-project smoke test**

```bash
rm -rf .tmp_cpb2d_acceptance
/e/Python312/python.exe skills/pfc-workflow/scripts/create_cpb2d_project.py \
  --from-intake skills/pfc-workflow/tests/fixtures/intake_minimal.yaml \
  --output-dir .tmp_cpb2d_acceptance
/e/Python312/python.exe - <<'PY'
from pathlib import Path
root = Path('.tmp_cpb2d_acceptance')
expected = ['sample', 'parallel_bonded', 'stage_a', 'stage_b', 'stage_c', 'stage_d', 'peak', 'final']
load = (root / 'pfc_cases/intact/3load.dat').read_text(encoding='utf-8')
for name in expected[2:]:
    assert f"model save '{name}'" in load
assert (root / 'pfc_cases/intact/run_all.dat').exists()
assert (root / 'pfc_cases/b0_d20/run_all.dat').exists()
print('static acceptance passed')
PY
rm -rf .tmp_cpb2d_acceptance
```

Expected: `static acceptance passed`.

- [ ] **Step 5: Perform optional PFC6/pfc-mcp smoke test**

Only when a licensed PFC6 runtime or `pfc-mcp` is available:

1. run only `pfc_cases/intact/run_all.dat`;
2. verify `sample.sav`, `parallel_bonded.sav`, A-D, peak, final and `stress_strain.csv`;
3. inspect the CSV header and at least one numeric row;
4. only then run `b0_d20/run_all.dat`;
5. record exact PFC build and any syntax correction in `references/cpb2d-project-wizard.md`.

If runtime is unavailable, do not claim PFC execution passed; report static verification separately.

- [ ] **Step 6: Check the final diff and commit**

```bash
git status --short
git diff --check
git diff --stat
git add skills/pfc-postprocessing/references/data-contract.md \
  skills/pfc-workflow/tests/test_cpb2d_scaffold.py \
  references/skill-index.md
git commit -m "test: verify CPB2D scaffold integration"
```

---

## Final Acceptance Checklist

- [ ] A beginner path is explicit and asks one question at a time.
- [ ] Intake field names exactly match Python config names.
- [ ] `intact` is generated and ordered before crack cases.
- [ ] Straight-crack endpoints are deterministic and unit-tested.
- [ ] `polyline_reserved` cannot masquerade as an enabled runnable case.
- [ ] Every enabled case gets exactly six source files and `run_all.dat`.
- [ ] Stage A-D, peak and final are present; heavy AE/Fig.9 is absent.
- [ ] Missing experiment data is a visible warning, not silent success or a hard blocker.
- [ ] `--force` cannot erase an unrelated user directory.
- [ ] Generated `stress_strain.csv` contract matches `pfc-postprocessing`.
- [ ] No private paths, secrets, `.sav`, generated plots or unresolved placeholders are committed.
- [ ] Pytest passes under `E:/Python312/python.exe`.
- [ ] `validate_skills.py` reports `0 error(s), 0 warning(s)`.
- [ ] PFC runtime verification is reported honestly as passed, failed, or unavailable.
