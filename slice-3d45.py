#!/usr/bin/env python3
"""Speed-Tower (Printables 22601) fuer den Dremel 3D45 aufbereiten.

1. 3mf kopieren, Objekt auf Bettmitte setzen (3D45 hat 0/0 in der Mitte).
2. Drucker-/Print-/Filamentprofil als flache INI schreiben.
3. Die Height-Range-Modifier des Originals bleiben unangetastet.
"""
import re
import shutil
import zipfile

SRC = "speed-tower.3mf"
DST = "speed-tower-3d45.3mf"
INI = "dremel3d45.ini"
CONFIG = "Metadata/Slic3r_PE.config"
MODEL = "3D/3dmodel.model"

START = (
    r"G28\n"
    r"M109 S215 ; Duese auf Temperatur, erst dann primen\n"
    r"G1 Z50.00 F400\n"
    r"G92 E0\n"
    r"G1 F200 E3\n"
    r"G92 E0\n"
    r"M132 X Y Z A\n"
    r"M907 X100 Y100 Z50 A100\n"
    r"; purge line an der linken Bettkante (Bett zentriert, -127.5..127.5)\n"
    r"G1 X-100 Y-75 Z0.3 F3000\n"
    r"G92 E0\n"
    r"G1 X-65 E8 F800\n"
    r"G92 E0\n"
    r"G1 Z2 F3000"
)
END = (
    r"M104 S0\n"
    r"M140 S0\n"
    r"G92 E1\n"
    r"G1 E-1 F300\n"
    r"G162 Z F600\n"
    r"G162 X Y F2000\n"
    r"M84"
)

OVERRIDES = {
    # --- Drucker: Dremel 3D45, Bett um 0/0 zentriert ---
    "bed_shape": "-127.5x-77.5,127.5x-77.5,127.5x77.5,-127.5x77.5",
    "bed_custom_model": "",
    "bed_custom_texture": "",
    "max_print_height": "170",
    "printer_model": "",
    "printer_notes": "",
    "printer_variant": "0.4",
    "printer_settings_id": "Dremel 3D45",
    "inherits_cummulative": "",
    "compatible_printers_condition_cummulative": "",
    "printer_technology": "FFF",
    "nozzle_diameter": "0.4",
    "host_type": "octoprint",
    "start_gcode": START,
    "end_gcode": END,
    "between_objects_gcode": "",
    "toolchange_gcode": "",
    "color_change_gcode": "M600",
    "thumbnails": "",
    "silent_mode": "0",
    "remaining_times": "0",
    "machine_max_feedrate_x": "500,200",
    "machine_max_feedrate_y": "500,200",
    "machine_max_feedrate_z": "12,12",
    "machine_max_feedrate_e": "120,120",
    "machine_max_acceleration_x": "1000,960",
    "machine_max_acceleration_y": "1000,960",
    "machine_max_acceleration_z": "500,200",
    "machine_max_acceleration_e": "5000,5000",
    "machine_limits_usage": "time_estimate_only",
    "gcode_flavor": "marlin",
    # --- Filament / Temperatur (PLA) ---
    "filament_settings_id": "PLA 3D45",
    "filament_type": "PLA",
    "extrusion_multiplier": "1",
    "filament_diameter": "1.75",
    "temperature": "215",
    "first_layer_temperature": "215",
    "bed_temperature": "60",
    "first_layer_bed_temperature": "60",
    "standby_temperature_delta": "-5",
    # --- Kuehlung: Vorgabe des Modells (1 s) bleibt ---
    "cooling": "1",
    "fan_always_on": "1",
    "disable_fan_first_layers": "1",
    "max_fan_speed": "100",
    "min_fan_speed": "100",
    "fan_below_layer_time": "100",
    "slowdown_below_layer_time": "1",
    "min_print_speed": "15",
    # --- Geschwindigkeiten: Grundniveau 3D45, Stufen kommen aus den Ranges ---
    "max_print_speed": "100",
    "max_volumetric_speed": "0",
    "filament_max_volumetric_speed": "15",
    "perimeter_speed": "45",
    "external_perimeter_speed": "35",
    "small_perimeter_speed": "35",
    "infill_speed": "80",
    "solid_infill_speed": "80",
    "top_solid_infill_speed": "50",
    "gap_fill_speed": "40",
    "bridge_speed": "30",
    "travel_speed": "130",
    "first_layer_speed": "20",
    "default_acceleration": "0",
    "perimeter_acceleration": "0",
    "infill_acceleration": "0",
    "bridge_acceleration": "0",
    "first_layer_acceleration": "0",
    # --- Geometrie ---
    "layer_height": "0.15",
    "first_layer_height": "0.25",
    "perimeters": "2",
    "fill_density": "0%",
    "top_solid_layers": "3",
    "bottom_solid_layers": "3",
    "elefant_foot_compensation": "0.1",
    "skirts": "4",
    "skirt_height": "1",
    "skirt_distance": "2",
    "min_skirt_length": "3",
    "extrusion_width": "0.45",
    "perimeter_extrusion_width": "0.45",
    "external_perimeter_extrusion_width": "0.45",
    "infill_extrusion_width": "0.45",
    "solid_infill_extrusion_width": "0.45",
    "top_infill_extrusion_width": "0.42",
    "first_layer_extrusion_width": "0.5",
    # --- Retract ---
    "retract_length": "1",
    "retract_speed": "40",
    "retract_before_travel": "2",
    "retract_lift": "0",
    "retract_lift_above": "0",
    "retract_lift_below": "0",
    "retract_layer_change": "0",
    "use_firmware_retraction": "0",
    "use_relative_e_distances": "0",
    "wipe": "0",
    # --- Sonstiges ---
    "gcode_comments": "1",
    "gcode_label_objects": "0",
    "output_filename_format": "speed-tower-3d45.gcode",
    "post_process": "",
    "start_filament_gcode": "",
    "end_filament_gcode": "",
    "layer_gcode": "",
    "before_layer_gcode": ";BEFORE_LAYER_CHANGE\\n;[layer_z]",
    "wipe_tower": "0",
    "support_material": "0",
}


def parse(text):
    out, order = {}, []
    for line in text.splitlines():
        m = re.match(r"^;\s*([A-Za-z0-9_]+)\s*=(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
            order.append(m.group(1))
    return out, order


def build_3mf():
    src_text = zipfile.ZipFile(SRC).read(CONFIG).decode("utf-8", "replace")
    cfg, order = parse(src_text)
    new_keys = [k for k in OVERRIDES if k not in cfg]
    order += new_keys
    cfg.update(OVERRIDES)

    # 1) 3mf: Config ersetzen, Objekt in die Bettmitte schieben
    with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == CONFIG:
                lines = ["; prusaslicer_config = begin"]
                lines += ["; %s = %s" % (k, cfg[k]) for k in order]
                lines.append("; prusaslicer_config = end")
                data = ("\n".join(lines) + "\n").encode("utf-8")
            elif item.filename == MODEL:
                txt = data.decode("utf-8")
                old = re.search(r'<item objectid="1" transform ="([^"]+)"', txt).group(1)
                nums = old.split()
                nums[-3:] = ["0", "0", nums[-1]]  # X/Y auf Bettmitte
                txt = txt.replace(old, " ".join(nums))
                data = txt.encode("utf-8")
            zout.writestr(item, data)

    # 2) flache INI fuer --load
    with open(INI, "w") as f:
        for k in order:
            f.write("%s = %s\n" % (k, cfg[k]))
    return new_keys, cfg


def main():
    new_keys, cfg = build_3mf()
    print("3mf:", DST)
    print("ini:", INI, "(%d Keys)" % len(cfg))
    print("neue Keys gegenueber Original:", new_keys)
    a = zipfile.ZipFile(SRC).read("Metadata/Prusa_Slicer_layer_config_ranges.xml")
    b = zipfile.ZipFile(DST).read("Metadata/Prusa_Slicer_layer_config_ranges.xml")
    print("Ranges unveraendert:", a == b)
    m = zipfile.ZipFile(DST).read(MODEL).decode()
    print("neue Transform:", re.search(r'transform ="([^"]+)"', m).group(1))


if __name__ == "__main__":
    main()
