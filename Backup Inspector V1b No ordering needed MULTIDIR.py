import os
import filecmp
from tqdm import tqdm
###THIS VERSION DOSENT CARE ABOUT ORDERING IN DIRS BUT DOES ONLY COMPARE BASED ON FILE NAME ALONE!!!!!!!!!!!

# Aloow for multiple directories to be compared



def count_subdirectories(directory):
    subdirectories_count = 0

    for entry in os.scandir(directory):
        if entry.is_dir():
            subdirectories_count += 1

    return subdirectories_count


def file_generator(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield file

def compare_directories(dirs1, dirs2, return_lost_file_list=False):
    set1 = set()
    set2 = set()

    for dir1 in dirs1:
        gen1 = file_generator(dir1)
        for file1 in tqdm(gen1, desc=f"Scanning files in {dir1}", unit="files", leave=True):
            set1.add(file1)

    for dir2 in dirs2:
        gen2 = file_generator(dir2)
        for file2 in tqdm(gen2, desc=f"Scanning files in {dir2}", unit="files", leave=True):
            set2.add(file2)

    files_scanned_in_dir1 = len(set1)
    files_scanned_in_dir2 = len(set2)
    perfect_matches = len(set1 & set2)
    files_only_in_dir1 = len(set1 - set2)
    files_only_in_dir2 = len(set2 - set1)

    percent_matched_dir1 = (perfect_matches / files_scanned_in_dir2) * 100
    percent_matched_dir2 = (perfect_matches / files_scanned_in_dir1) * 100

    return_lost_file_list1 = False
    if return_lost_file_list1:
        # print list of the file names of the files that are only in dir1
        print("\nFiles only in dir1:")
        for file in set1 - set2:
            print(f"\n # {file}")

        # print list of the file names of the files that are only in dir2
        print("\nFiles only in dir2:")
        for file in set2 - set1:
            print(f"\n # {file}")

    if return_lost_file_list:

        # Create a text file to write the results
        file_path = "comparison_results.txt"

        with open(file_path, "w") as f:
            # Write list of the file names of the files that are only in dir1
            f.write("\nFiles only in dir1:\n")
            for file in set1 - set2:
                f.write(f"\n# {file}\n")

            # Write list of the file names of the files that are only in dir2
            f.write("\nFiles only in dir2:\n")
            for file in set2 - set1:
                f.write(f"\n# {file}\n")

    # Open the file in Notepad
    os.system(f"notepad.exe {file_path}")

    return (
        files_scanned_in_dir1,
        files_scanned_in_dir2,
        perfect_matches,
        files_only_in_dir1,
        files_only_in_dir2,
        percent_matched_dir1,
        percent_matched_dir2,
    )

# Example usage
dirs1 = [r'C:\\', r'A:\Users\Ada\\']  # List of data directories
dirs2 = [r'I:\Ada 8700K Cobian Backup\8700K OS and User Folders\C\\', r'I:\Ada 8700K Cobian Backup\8700K OS and User Folders\A\Users\Ada\\']  # List of target directories

files_scanned_1, files_scanned_2, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2, percent_matched_dir1, percent_matched_dir2 = compare_directories(dirs1, dirs2, return_lost_file_list=True)

num_subdirectories1 = sum(count_subdirectories(dir) for dir in dirs1)
num_subdirectories2 = sum(count_subdirectories(dir) for dir in dirs2)


print("Data Directories:")
for i, dir1 in enumerate(dirs1):
    num_subdirectories1 = count_subdirectories(dir1)
    print(f"\nData Dir {i+1} ({dir1}):")
    print(f"  There are {files_scanned_1[i]} files in {num_subdirectories1} subdirectories")

print("\nTarget Directories:")
for i, dir2 in enumerate(dirs2):
    num_subdirectories2 = count_subdirectories(dir2)
    print(f"\nTarget Dir {i+1} ({dir2}):")
    print(f"  There are {files_scanned_2[i]} files in {num_subdirectories2} subdirectories")

print("\nNumber of files with a perfect match:")
print(f"  {num_perfect_matches}")

print("\nNumber of files present in Data but not found in Target:")
print(f"  {num_files_only_in_dir1}")

print("\nNumber of files present in Target but not found in Data:")
print(f"  {num_files_only_in_dir2}")

print("\nPercentage of files in Data that match the files in Target:")
for i, dir1 in enumerate(dirs1):
    print(f"  Data Dir {i+1} ({dir1}): {percent_matched_dir1[i]:.2f}%")

print("\nPercentage of files in Target that match the files in Data:")
for i, dir2 in enumerate(dirs2):
    print(f"  Target Dir {i+1} ({dir2}): {percent_matched_dir2[i]:.2f}%")
