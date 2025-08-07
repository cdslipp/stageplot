
import os
import shutil
import json

def reorganize_players(players_dir):
    print(f"Starting reorganization in: {players_dir}")

    # Get all files in the players directory
    all_files = [f for f in os.listdir(players_dir) if os.path.isfile(os.path.join(players_dir, f))]

    # Filter out the existing item.json if it's there (it's a global one we'll remove)
    if 'item.json' in all_files:
        all_files.remove('item.json')
        os.remove(os.path.join(players_dir, 'item.json'))
        print("Removed global item.json from players directory.")

    # Group files by player prefix
    player_files = {}
    for filename in all_files:
        # Determine player prefix (e.g., 'AcuBassist', 'bassist', 'violinist')
        # This logic needs to be robust for different naming conventions
        # For now, assume prefix is everything before the first capital letter (if any) or the whole name if no variants
        # Or, more simply, just use the base name without extension for single files like violinist.png
        # For files like 'AcuBassistB.png', the prefix is 'AcuBassist'
        # For 'violinist.png', the prefix is 'violinist'

        base_name = os.path.splitext(filename)[0]
        player_prefix = ''

        # Heuristic to find the player prefix based on common variant naming (e.g., 'NameA.png', 'NameB.png')
        # This might need adjustment if naming conventions are very inconsistent
        if base_name.endswith(('B', 'L', 'LA', 'LB', 'R', 'RA', 'RB')) and len(base_name) > 1:
            # Try to find the base name without the variant suffix
            # This is a bit tricky, let's try to match common patterns
            if base_name.endswith('LA') or base_name.endswith('LB') or base_name.endswith('RA') or base_name.endswith('RB'):
                player_prefix = base_name[:-2]
            elif base_name.endswith('B') or base_name.endswith('L') or base_name.endswith('R'):
                player_prefix = base_name[:-1]
            else:
                player_prefix = base_name # Fallback
        else:
            player_prefix = base_name # For default or single files like violinist.png

        # A more robust way might be to have a predefined list of player names
        # For this specific set, we can hardcode or use a more specific regex
        # Let's refine the prefix extraction for the known players:
        known_players = ['AcuBassist', 'bassist', 'ebassist', 'eguitarist', 'femguitarist', 'keyboardist', 'violinist']
        found_prefix = False
        for kp in known_players:
            if filename.lower().startswith(kp.lower()):
                player_prefix = kp
                found_prefix = True
                break
        if not found_prefix:
            # Fallback if not in known_players, might need manual review
            player_prefix = base_name.split('.')[0] # Take everything before the first dot

        if player_prefix not in player_files:
            player_files[player_prefix] = []
        player_files[player_prefix].append(filename)

    for player_name, files in player_files.items():
        player_folder = os.path.join(players_dir, player_name)
        os.makedirs(player_folder, exist_ok=True)
        print(f"Created directory: {player_folder}")

        variants = {}
        for filename in files:
            src_path = os.path.join(players_dir, filename)
            dest_path = os.path.join(player_folder, filename)
            shutil.move(src_path, dest_path)
            print(f"Moved {filename} to {player_folder}")

            # Determine variant name
            base_filename = os.path.splitext(filename)[0]
            if base_filename == player_name:
                variants["default"] = filename
            elif base_filename.startswith(player_name):
                variant_key = base_filename[len(player_name):]
                variants[variant_key] = filename
            else:
                # Fallback for unexpected naming, might need manual correction
                variants[base_filename] = filename

        # Create item.json
        item_data = {
            "name": player_name.replace('_', ' ').title(), # Capitalize and replace underscores for display name
            "item_type": "output", # Assuming 'output' for players
            "variants": variants
        }
        item_json_path = os.path.join(player_folder, "item.json")
        with open(item_json_path, 'w') as f:
            json.dump(item_data, f, indent=4)
        print(f"Created item.json for {player_name} in {player_folder}")

    print("Reorganization complete.")

if __name__ == "__main__":
    players_directory = "/Users/cdslipp/Code/sherwood/web-apps/input-list/stage-plot-creator/static/final_assets/people/players/"
    reorganize_players(players_directory)
