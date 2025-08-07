
import os
import shutil

def delete_duplicate_subfolders(root_dir):
    """
    Identifies and deletes duplicate subfolders where an inner folder has the same name
    as its parent and contains the same files.

    Example: If 'path/to/folderX/' contains 'folderX/' (a directory) and 'file1.png', 'file2.png',
    and 'path/to/folderX/folderX/' contains 'file1.png', 'file2.png',
    then 'path/to/folderX/folderX/' will be deleted.
    """
    print(f"Starting scan for duplicate subfolders in: {root_dir}")
    deleted_count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        current_dir_name = os.path.basename(dirpath)

        # Check if a subfolder exists with the same name as the current directory
        if current_dir_name in dirnames:
            duplicate_subdir_path = os.path.join(dirpath, current_dir_name)

            # Ensure the duplicate path is indeed a directory
            if not os.path.isdir(duplicate_subdir_path):
                continue

            # Get the set of filenames directly in the current directory
            # These are the files that should match the contents of the duplicate subfolder
            current_dir_files = set(filenames)

            # Get the set of filenames directly in the potential duplicate subfolder
            try:
                duplicate_subdir_files = set(os.listdir(duplicate_subdir_path))
                # Filter out any subdirectories within the duplicate, only compare files
                duplicate_subdir_files = set(f for f in duplicate_subdir_files if os.path.isfile(os.path.join(duplicate_subdir_path, f)))
            except FileNotFoundError:
                print(f"Warning: Duplicate subfolder path not found: {duplicate_subdir_path}. Skipping.")
                continue

            # Compare the file sets
            if current_dir_files == duplicate_subdir_files:
                print(f"Found duplicate subfolder: {duplicate_subdir_path}")
                print(f"  Parent files: {current_dir_files}")
                print(f"  Duplicate files: {duplicate_subdir_files}")
                try:
                    shutil.rmtree(duplicate_subdir_path)
                    print(f"  Successfully deleted: {duplicate_subdir_path}")
                    deleted_count += 1
                except OSError as e:
                    print(f"  Error deleting {duplicate_subdir_path}: {e}")
            else:
                print(f"Skipping {duplicate_subdir_path}: Contents do not match parent's files.")
                print(f"  Parent files: {current_dir_files}")
                print(f"  Duplicate files: {duplicate_subdir_files}")

    print(f"Scan complete. Total duplicate subfolders deleted: {deleted_count}")

if __name__ == "__main__":
    # Define the root directory to start cleaning from
    # This should be the 'final_assets' directory as per your request.
    root_directory_to_clean = "/Users/cdslipp/Code/sherwood/web-apps/input-list/stage-plot-creator/static/final_assets/"
    delete_duplicate_subfolders(root_directory_to_clean)
