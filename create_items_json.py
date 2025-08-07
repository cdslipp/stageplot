import json
import os
import glob

def create_items_json():
    items = []
    file_paths = glob.glob("static/final_assets/**/item.json", recursive=True)

    for path in file_paths:
        with open(path, 'r') as f:
            data = json.load(f)

        category = os.path.basename(os.path.dirname(os.path.dirname(path)))
        item_type = os.path.basename(os.path.dirname(path))

        variants = []
        for name, file in data.get('variants', {}).items():
            variant_path = os.path.join(os.path.dirname(path), file)
            variants.append({
                "name": name,
                "file": os.path.relpath(variant_path, 'static')
            })

        item = {
            "name": data['name'],
            "type": item_type,
            "category": category,
            "variants": variants,
            "inputs": data.get('inputs', [])
        }
        items.append(item)

    with open('src/lib/items.json', 'w') as f:
        json.dump(items, f, indent=2)

    print("items.json created successfully.")

if __name__ == "__main__":
    create_items_json()