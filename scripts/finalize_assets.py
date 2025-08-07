import json
import os
import shutil
import re
from collections import defaultdict

def create_final_structure():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_json_path = os.path.join(base_dir, "src", "lib", "items_reorganized.json")
    source_img_root = os.path.join(base_dir, "static", "img_reorganized")
    output_root = os.path.join(base_dir, "static", "final_assets")

    if not os.path.exists(source_json_path):
        print(f"Error: Source JSON not found at {source_json_path}")
        return

    if not os.path.exists(source_img_root):
        print(f"Error: Source image directory not found at {source_img_root}")
        return

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    with open(source_json_path, "r") as f:
        items = json.load(f)

    # Group items by menu/submenu path
    groups = defaultdict(list)
    for item in items:
        menu = item.get("menu", "uncategorized").lower().replace(" ", "_")
        submenu = item.get("submenu", "").lower().replace(" ", "_")
        
        # Special handling for numerals and alphabet - consolidate into symbols
        if menu in ["numerals", "alphabet"]:
            group_key = "symbols"
        elif submenu:
            group_key = f"{menu}/{submenu}"
        else:
            group_key = menu
            
        groups[group_key].append(item)

    # Process each group
    for group_path, group_items in groups.items():
        print(f"\nProcessing group: {group_path} ({len(group_items)} items)")
        
        # Check if all items in this group are "simple" (≤ 2 variants)
        # Special case: symbols should always be consolidated regardless of variant count
        all_simple = all(len(item["variants"]) <= 2 for item in group_items)
        force_consolidate = group_path == "symbols"
        
        group_dir = os.path.join(output_root, group_path)
        os.makedirs(group_dir, exist_ok=True)
        
        if (all_simple and len(group_items) > 1) or force_consolidate:
            # Create consolidated structure: one folder with items.json containing all items
            print(f"  → Consolidating {len(group_items)} simple items into single JSON")
            
            consolidated_items = []
            
            for item in group_items:
                item_data = {
                    "name": item["name"],
                    "item_type": item.get("item_type", "accessory"),
                    "variants": {}
                }
                
                # Copy images and update variant paths
                for variant, path in item["variants"].items():
                    old_path_abs = os.path.join(base_dir, "static", path)
                    
                    if not os.path.exists(old_path_abs):
                        print(f"    Warning: Image not found at {old_path_abs}. Skipping.")
                        continue

                    # Create unique filename: itemname_variant.ext
                    file_name = os.path.basename(path)
                    name_slug = item["name"].lower().replace(" ", "_").replace("/", "_")
                    base_name, ext = os.path.splitext(file_name)
                    
                    # Special handling for symbols - standardize variant naming
                    if group_path == "symbols":
                        # Determine if this is light or dark variant based on filename patterns
                        item_base = item["name"].lower()
                        
                        # For symbols, standardize variant names
                        if base_name.lower().endswith('x') or base_name.lower().endswith(item_base + item_base[-1:]):
                            # This is the light variant (AX, eight8, etc.)
                            standardized_variant = "light"
                        else:
                            # This is the dark variant (A, eight, etc.)
                            standardized_variant = "dark"
                        
                        file_name = f"{item_base}_{standardized_variant}{ext}"
                        item_data["variants"][standardized_variant] = file_name
                    else:
                        # If the filename doesn't already start with the item name, prepend it
                        if not base_name.lower().startswith(name_slug.lower()):
                            file_name = f"{name_slug}_{base_name}{ext}"
                        item_data["variants"][variant] = file_name
                    
                    new_path_abs = os.path.join(group_dir, file_name)
                    shutil.copy(old_path_abs, new_path_abs)

                consolidated_items.append(item_data)
            
            # Write consolidated items.json
            with open(os.path.join(group_dir, "items.json"), "w") as f:
                json.dump(consolidated_items, f, indent=4)
                
        else:
            # Handle complex items or single items differently
            if len(group_items) == 1:
                # Single item: place directly in group folder (no nested folder)
                print(f"  → Placing single item directly in group folder")
                item = group_items[0]
                
                new_item_data = {
                    "name": item["name"],
                    "item_type": item.get("item_type", "accessory"),
                    "variants": {}
                }

                for variant, path in item["variants"].items():
                    old_path_abs = os.path.join(base_dir, "static", path)
                    
                    if not os.path.exists(old_path_abs):
                        print(f"    Warning: Image not found at {old_path_abs}. Skipping.")
                        continue

                    file_name = os.path.basename(path)
                    new_path_abs = os.path.join(group_dir, file_name)

                    shutil.copy(old_path_abs, new_path_abs)
                    
                    new_item_data["variants"][variant] = file_name

                with open(os.path.join(group_dir, "item.json"), "w") as f:
                    json.dump(new_item_data, f, indent=4)
            else:
                # Multiple complex items: keep individual folders
                print(f"  → Creating individual folders for {len(group_items)} complex items")
                
                for item in group_items:
                    item_name_slug = item["name"].lower().replace(" ", "_").replace("/", "_")
                    item_dir = os.path.join(group_dir, item_name_slug)
                    os.makedirs(item_dir, exist_ok=True)

                    new_item_data = {
                        "name": item["name"],
                        "item_type": item.get("item_type", "accessory"),
                        "variants": {}
                    }

                    for variant, path in item["variants"].items():
                        old_path_abs = os.path.join(base_dir, "static", path)
                        
                        if not os.path.exists(old_path_abs):
                            print(f"    Warning: Image not found at {old_path_abs}. Skipping.")
                            continue

                        file_name = os.path.basename(path)
                        new_path_abs = os.path.join(item_dir, file_name)

                        shutil.copy(old_path_abs, new_path_abs)
                        
                        new_item_data["variants"][variant] = file_name

                    with open(os.path.join(item_dir, "item.json"), "w") as f:
                        json.dump(new_item_data, f, indent=4)

    print("\nFinal asset structure created successfully.")

if __name__ == "__main__":
    create_final_structure()
