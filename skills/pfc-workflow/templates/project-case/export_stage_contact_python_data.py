import csv
import math
import os

import itasca


CASE_DIR = os.getcwd()
STAGES = [
    ("A", "stage_a"),
    ("B", "stage_b"),
    ("C", "stage_c"),
    ("D", "stage_d"),
]
X_MIN = -0.018
X_MAX = 0.018
Y_MIN = -0.018
Y_MAX = 0.018
NX = 15
NY = 15


def export_contacts(stage_label):
    rows = []
    for contact in itasca.contact.list():
        if contact.model() != "linearpbond":
            continue
        end1 = contact.end1()
        end2 = contact.end2()
        pos1 = end1.pos()
        pos2 = end2.pos()
        pos = contact.pos()
        force = contact.force_global()
        fx = float(force.x())
        fy = float(force.y())
        fmag = math.sqrt(fx * fx + fy * fy)
        rows.append(
            [
                contact.id(),
                float(pos.x()),
                float(pos.y()),
                float(pos1.x()),
                float(pos1.y()),
                float(pos2.x()),
                float(pos2.y()),
                fx,
                fy,
                fmag,
            ]
        )
    out_path = os.path.join(CASE_DIR, f"plotdata_contacts_stage_{stage_label}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "x", "y", "x1", "y1", "x2", "y2", "fx", "fy", "fmag"])
        writer.writerows(rows)
    print(stage_label, "contacts", len(rows), out_path)


def export_measures(stage_label):
    itasca.command("measure delete")
    dx = (X_MAX - X_MIN) / NX
    dy = (Y_MAX - Y_MIN) / NY
    radius = dx * 0.55
    measure_id = 0
    for j in range(NY):
        for i in range(NX):
            cx = X_MIN + (i + 0.5) * dx
            cy = Y_MIN + (j + 0.5) * dy
            measure_id += 1
            itasca.command(f"measure create id {measure_id} position {cx} {cy} radius {radius}")
    itasca.command("model clean")
    rows = []
    for measure in itasca.measure.list():
        pos = measure.pos()
        rows.append([float(pos.x()), float(pos.y()), float(measure.porosity()), float(measure.coordination())])
    out_path = os.path.join(CASE_DIR, f"plotdata_measures_stage_{stage_label}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "porosity", "coord_num"])
        writer.writerows(rows)
    print(stage_label, "measures", len(rows), out_path)


def restore_state(save_name, fallback_name="final"):
    primary = os.path.join(CASE_DIR, save_name + ".sav")
    fallback = os.path.join(CASE_DIR, fallback_name + ".sav")
    if os.path.exists(primary):
        target = save_name
    elif os.path.exists(fallback):
        target = fallback_name
    else:
        raise FileNotFoundError(f"Missing both {primary} and {fallback}")
    itasca.command(f"model restore '{target}'")
    print("restored", save_name, "->", target)


def main():
    os.chdir(CASE_DIR)
    for stage_label, save_name in STAGES:
        restore_state(save_name)
        export_contacts(stage_label)
        export_measures(stage_label)


main()
