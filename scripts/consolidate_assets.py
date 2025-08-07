
import json
import os

def consolidate_assets():
    final_assets_dir = os.path.join('static', 'final_assets')
    output_file = os.path.join(final_assets_dir, 'items.json')
    all_items = []

    for root, _, files in os.walk(final_assets_dir):
        for file in files:
            if file == 'item.json':
                item_json_path = os.path.join(root, file)
                try:
                    with open(item_json_path, 'r') as f:
                        item_data = json.load(f)
                    
                    # Add the relative path to the item data
                    relative_path = os.path.relpath(root, final_assets_dir)
                    item_data['path'] = relative_path
                    
                    all_items.append(item_data)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {item_json_path}")
                except Exception as e:
                    print(f"An error occurred with {item_json_path}: {e}")

    with open(output_file, 'w') as f:
        json.dump(all_items, f, indent=2)

    print(f"Consolidated {len(all_items)} items into {output_file}")

if __name__ == '__main__':
    consolidate_assets()
