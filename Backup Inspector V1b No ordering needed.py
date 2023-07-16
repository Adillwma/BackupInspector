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

def compare_directories(dir1, dir2, return_lost_file_list=False):
    gen1 = file_generator(dir1)
    gen2 = file_generator(dir2)

    set1 = set()
    set2 = set()

    for file1 in tqdm(gen1, desc="Scanning files in folder 1", unit="files", leave=True):
        set1.add(file1)

    for file2 in tqdm(gen2, desc="Scanning files in folder 2", unit="files", leave=True):
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

    return files_scanned_in_dir1, files_scanned_in_dir2, perfect_matches, files_only_in_dir1, files_only_in_dir2, percent_matched_dir1, percent_matched_dir2

# Example usage
dir1 =  r'C:\\'           #r'A:\Users\Ada\Desktop\Audio sort out\1\\' #/path/to/folder1'
dir2 =  r'I:\Ada 8700K Cobian Backup\8700K OS and User Folders\C\\'     #r'A:\Users\Ada\Desktop\Audio sort out\2\\'  #'/path/to/folder2'

files_scanned_1, files_scanned_2, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2, percent_matched_dir1, percent_matched_dir2 = compare_directories(dir1, dir2, return_lost_file_list=True)
num_subdirectories1 = count_subdirectories(dir1)
num_subdirectories2 = count_subdirectories(dir2)

print(f"\nIn Data Dir {dir1}")
print(f" there are {files_scanned_1} files in {num_subdirectories1} subdirectories")

print(f"\nIn Target Dir {dir2}")
print(f" there are {files_scanned_2} files in {num_subdirectories2} subdirectories")


print("\nNumber of files with a perfect match:", num_perfect_matches)
print("Number of files present in folder 1 but not found in folder 2:", num_files_only_in_dir1)
print("Number of files present in folder 2 but not found in folder 1:", num_files_only_in_dir2)

print(f"\nData contains {percent_matched_dir1:.2f}% of the files in Target")
print(f"Target contains {percent_matched_dir2:.2f}% of the files in Data")