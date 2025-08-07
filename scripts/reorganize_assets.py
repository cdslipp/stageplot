import json
import os
import re
import shutil
import argparse

# This script reorganizes the assets of the Stage Plot Creator application.
# It reads a JSON file of items, cleans up their names, and based on a
# predefined menu structure, it reorganizes the associated image files into
# a new directory structure.
#
# The script can be run in two modes:
# 1. Dry Run Mode (`--dry-run`): In this mode, the script only simulates the
#    reorganization. It identifies which files would be moved and where,
#    and generates a report of the proposed changes without actually
#    touching any files. This is useful for verifying the script's logic
#    before making any permanent changes.
#
# 2. Reorganization Mode (default): In this mode, the script performs the
#    actual reorganization. It moves the image files to their new
#    directories and generates a new JSON file with the updated paths.
#
# The script is designed to be idempotent, meaning it can be run multiple
# times without changing the result after the initial run. It checks if a
# file has already been moved to avoid errors on subsequent runs.
#
# The script also handles items that cannot be automatically categorized.
# These items are logged to a separate file for manual review. This
# ensures that no items are lost during the reorganization process.
#
# Usage:
#   Dry Run: python reorganize_assets.py --dry-run
#   Reorganize: python reorganize_assets.py

MENU_STRUCTURE = {
    "Mics": {
        "Straight": [],
        "Boom": [],
        "Hand Held": ["Wired", "Wireless"],
        "Recording": [],
        "Clip-On": [],
        "Headset": [],
        "Stand-No Mic": [],
    },
    "Guitars": {
        "Acoustic": [],
        "Electric": [],
        "Electric Bass": [],
        "12 String": [],
        "Guitarron": [],
        "Guitar Stand": [],
        "Guitar on Stand": [],
        "Pedal Steel": [],
        "Lap Steel": [],
        "National": [],
        "Banjo": [],
        "Mandolin": [],
        "Ukulele": [],
        "Guitar Synth": [],
        "Boss Pedal": [],
        "Pedal Board": [],
        "Lute": [],
        "Sitar": [],
        "Bouzouki": [],
        "Oud": [],
        "Charango": [],
        "Cuatro": [],
        "Tiple": [],
        "Tumbi": [],
        "Zinfonia": [],
        "Balalaika": [],
        "Azerisaz": [],
    },
    "Amps": {"Guitar": [], "Bass": [], "Steel": [], "Keyboard": []},
    "Keys": {
        "Piano/Synth": ["Singlet", "No Stand", "Double Tier"],
        "Key Stand": [],
        "Upright Piano": [],
        "Accordion": [],
        "Keytar": [],
        "Roland Fantom": [],
        "Novation MKII": [],
        "Korg SV1": [],
        "Nord Stage 88": [],
        "YamahaCP70": [],
        "YamahaGT2": [],
        "Grand Piano": [],
        "Baby Grand": [],
        "Celesta": [],
        "Harpsichord": [],
        "Fender Rhodes": [],
        "Hammond C": [],
        "Hammond SK-1": [],
        "Hammond B3": [],
        "Wurlitzer 200A": [],
        "Clavinet": [],
        "Moog Voyager": [],
        "Mellotron": [],
        "Piano Bench": [],
        "Leslie": [],
    },
    "Strings": {"Violin": [], "Viola": [], "Cello": [], "Bass": [], "Harp": []},
    "Winds": {
        "Trumpet": [],
        "Cornet": [],
        "Trombone": [],
        "Saxophone": [],
        "Clarinet": [],
        "Flute": [],
        "French Horn": [],
        "English Horn": [],
        "Oboe": [],
        "Piccolo": [],
        "Recorder": [],
        "Bassoon": [],
        "Contra Bassoon": [],
        "Euphonium": [],
        "Tuba": [],
        "Harmonica": [],
        "Ocarina": [],
        "Bagpipes": [],
        "Gajda": [],
        "Kaval": [],
    },
    "Drums": {
        "Drum Kits": [],
        "Individual Drums": [],
        "Cymbals": [],
        "Hardware": [],
        "Drummer": [],
    },
    "People": {"Acoustic": [], "Electric": [], "Male": [], "Female": []},
    "Percussion": {
        "Bongo": [],
        "Conga": [],
        "Djembe": [],
        "Cajon": [],
        "Tambourine": [],
        "Claves": [],
        "Cowbell": [],
        "Timpani": [],
        "Gong": [],
        "Chimes": [],
        "Xylophone": [],
        "Marimba": [],
        "Vibraphone": [],
        "Tabla": [],
        "Dholak": [],
        "Steelpan": [],
        "Tenorpan": [],
        "Daf": [],
        "Dhumbuk": [],
    },
    "Stagecraft": {
        "Stage": [],
        "Curtain": [],
        "Truss": [],
        "Riser": [],
        "Stairs": [],
        "Floor Box": [],
        "Bose L1": [],
        "Bose B2": [],
        "Speaker": [],
        "Line Array": [],
        "Subwoofer": [],
        "Smaller Mains": [],
    },
    "More": {
        "Monitors": [],
        "Cables": [],
        "Direct Box": [],
        "Video": [],
        "Electric Drop": [],
        "Stage Box": [],
        "Music Stand": [],
        "Podium": ["With Mic", "Without"],
        "Gobo": [],
        "Drum Shield": [],
        "DJ Gear": [],
        "Mixer": [],
        "Rack": [],
        "Sampler": [],
        "Graphic EQ": [],
        "Compressor": [],
        "Noise Gates": [],
        "CD Player": [],
        "Laptop": [],
        "iPad": [],
        "Flight Case": [],
        "Sandbag": [],
        "Fan": [],
        "Stool": [],
        "Bar Stool": [],
        "Chair": [],
        "Sofa": [],
        "Barricade": [],
        "Table": [],
    },
    "Players": {},
    "AC": {},
    "Alphabet": {},
    "Numerals": {},
}

DRUM_KITS = [
    "FourToms.png",
    "TwoToms.png",
    "ThreeToms.png",
    "edrums.png",
    "rototomset.png",
    "doublekick.png",
]

PLAYERS = [
    "acubassist",
    "bassist",
    "Beguitarist",
    "eguitarist",
    "femguitarist",
    "Guitarist",
    "keyboardist",
    "drummer",
    "DrummerAfrican",
    "femacoustic",
]

def normalize_name(name):
    s = re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", name)).strip()
    return " ".join(s.split())

def get_item_type(item, menu, submenu):
    name = item["name"]
    if menu == "Drums" and submenu == "Drum Kits":
        return "drumset"
    if menu in ["Mics", "Guitars", "Keys", "Strings", "Winds", "Percussion", "Players"] or "DI" in name or "Direct Box" in name:
        if menu == "Drums" and submenu == "Individual Drums":
            return "input"
        if menu == "Drums" and submenu == "Cymbals":
            return "input"
    if menu == "Amps" or submenu in ["Monitors", "Speaker", "Line Array", "Subwoofer"]:
        return "output"
    if "Stand" in name or submenu == "Music Stand":
        return "stand"
    if menu in ["Alphabet", "Numerals", "People"] or any(s in name for s in ["Curtain", "Stage", "Riser", "Stairs"]):
        return "symbol"
    return "accessory"

def get_category_from_name(item, menu_structure):
    name = item["name"]
    category = item.get("category")
    variants = item.get("variants", {})
    
    if name in PLAYERS:
        return "Players", None

    if category == "power":
        return "AC", None

    if "dj" in name.lower() or "djsetup" in name.lower():
        return "More", "DJ Gear"

    if name.lower().startswith("woman"):
        return "People", "Female"
    if name.lower().startswith("man"):
        return "People", "Male"

    if any(kit in path for path in variants.values() for kit in DRUM_KITS):
        return "Drums", "Drum Kits"

    if category == "drum":
        if "cymbal" in name.lower():
            return "Drums", "Cymbals"
        if any(k in name.lower() for k in ["tom", "snare", "kick"]):
            return "Drums", "Individual Drums"
        if "drummer" in name.lower():
            return "Drums", "Drummer"
        return "Drums", "Hardware"

    if category == "numerical":
        return "Numerals", None
    if category == "alphabet":
        return "Alphabet", None

    if "amp" in name.lower() or any(brand in name.lower() for brand in ["marshall", "fender", "vox"]) or category == "egt":
        if "bass" in name.lower():
            return "Amps", "Bass"
        if "keyboard" in name.lower():
            return "Amps", "Keyboard"
        return "Amps", "Guitar"

    for menu, submenus in menu_structure.items():
        if menu.lower() in name.lower():
            return menu, None
        for submenu, items in submenus.items():
            if submenu.lower() in name.lower():
                return menu, submenu
            for item_name in items:
                if item_name.lower() in name.lower():
                    return menu, submenu
    return None, None

def reorganize_assets(dry_run):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_json_path = os.path.join(base_dir, "src", "lib", "items_reorganized.json")
    if not os.path.exists(source_json_path):
        source_json_path = os.path.join(base_dir, "src", "lib", "items.json")
    
    source_img_root = os.path.join(base_dir, "static", "img")
    output_json_path = os.path.join(base_dir, "src", "lib", "items_reorganized.json")
    output_img_root = os.path.join(base_dir, "static", "img_reorganized")
    reports_dir = os.path.join(base_dir, "scripts", "reorg_reports")

    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    if not dry_run:
        if not os.path.exists(output_img_root):
            os.makedirs(output_img_root)
        for menu in MENU_STRUCTURE:
            menu_path = os.path.join(output_img_root, menu.lower().replace(" ", "_"))
            if not os.path.exists(menu_path):
                os.makedirs(menu_path)

    with open(source_json_path, "r") as f:
        items = json.load(f)

    new_items = []
    unmapped_items = []
    dry_run_report = []

    for item in items:
        normalized_name = normalize_name(item["name"])
        menu, submenu = get_category_from_name(item, MENU_STRUCTURE)

        if not menu:
            unmapped_items.append(item)
            continue

        new_item = item.copy()
        new_item["name"] = normalized_name
        new_item["menu"] = menu
        if submenu:
            new_item["submenu"] = submenu
        
        new_item["item_type"] = get_item_type(new_item, menu, submenu)

        for variant, path in item["variants"].items():
            old_path = os.path.join(base_dir, "static", path)
            if "reorganized" not in old_path:
                 old_path = old_path.replace("img", "img_reorganized", 1)

            new_dir = os.path.join(output_img_root, menu.lower().replace(" ", "_"))
            if submenu:
                new_dir = os.path.join(new_dir, submenu.lower().replace(" ", "_"))
            
            if not dry_run and not os.path.exists(new_dir):
                os.makedirs(new_dir)

            new_path = os.path.join(new_dir, os.path.basename(path))
            new_item["variants"][variant] = os.path.relpath(new_path, os.path.join(base_dir, "static")).replace("\\\\", "/")

            if dry_run:
                dry_run_report.append({"from": old_path, "to": new_path})
            else:
                if os.path.exists(old_path) and old_path != new_path:
                    shutil.move(old_path, new_path)

        new_items.append(new_item)

    if dry_run:
        with open(os.path.join(reports_dir, "dry_run_report.json"), "w") as f:
            json.dump(dry_run_report, f, indent=4)
    else:
        with open(output_json_path, "w") as f:
            json.dump(new_items, f, indent=4)

    with open(os.path.join(reports_dir, "unmapped_items.txt"), "w") as f:
        for item in unmapped_items:
            f.write(f"{item['name']}\n")

    with open(os.path.join(reports_dir, "summary.txt"), "w") as f:
        f.write(f"Total items processed: {len(items)}\n")
        f.write(f"Mapped items: {len(new_items)}\n")
        f.write(f"Unmapped items: {len(unmapped_items)}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorganize assets for Stage Plot Creator.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the reorganization without moving files.")
    args = parser.parse_args()
    reorganize_assets(args.dry_run)
