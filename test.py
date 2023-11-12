import os
import shutil

def file_copier(reference_dir, target_dir, missing_files_list):
    for missing_file_path in missing_files_list:
        # Extract the file name
        missing_file_name = os.path.basename(missing_file_path)

        # Determine the relative path of the missing file within the reference directory
        relative_path = os.path.relpath(missing_file_path, reference_dir)

        # Construct the target file path
        target_file_path = os.path.join(target_dir, relative_path)

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        # Copy the missing file to the target directory
        shutil.copy(missing_file_path, target_file_path)

reference_dir = r"A:\Users\Ada\Desktop\test\ref"
target_dir = r"A:\Users\Ada\Desktop\test\tar"
missing_files_list = [r'A:/Users/Ada/Desktop/test/ref/2/t2.txt', r'A:/Users/Ada/Desktop/test/ref/3/t1.txt', r'A:\Users\Ada\Desktop\test\ref\4\5\6\8\t1.txt', r'A:\Users\Ada\Desktop\test\ref\4\5\7\t3.txt']

file_copier(reference_dir, target_dir, missing_files_list)

