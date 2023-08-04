import os
import filecmp
from tqdm import tqdm
###THIS VERSION DOSENT CARE ABOUT ORDERING IN DIRS AND COMAPRES FILES USING SIZE NAME AND MODIFIED DATRE???

# Aloow for multiple directories to be compared
# fix the issue that the files are being compared in the same order only and if there is any missordering the mathces will fail
# maekt the shallew argument True or false a user input to controll if the long search is conducted that compares the entire file scontents (False) or just compaing the name and date created (True)
# Number of files present in folder 1 but not found in folder 2: 0   ----- this thig will alwys be zero for the smaller of the two folders, needs fixing
def count_subdirectories(directory):
    subdirectories_count = 0

    for entry in os.scandir(directory):
        if entry.is_dir():
            subdirectories_count += 1

    return subdirectories_count


import os
from stat import S_ISREG, ST_CTIME, ST_SIZE

def file_generator(directory): #BROKEN
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def compare_directories(dir1, dir2):
    files_scanned = 0
    perfect_matches = 0
    files_only_in_dir1 = 0
    files_only_in_dir2 = 0

    gen1 = file_generator(dir1)
    gen2 = file_generator(dir2)

    file_info1 = {}
    file_info2 = {}

    for file1 in gen1:
        file_info1[file1] = (os.stat(file1).st_size, os.stat(file1).st_mtime)

    for file2 in gen2:
        file_info2[file2] = (os.stat(file2).st_size, os.stat(file2).st_mtime)

    files_scanned = len(file_info1) + len(file_info2)

    for file1, info1 in file_info1.items():
        if file1 in file_info2:
            info2 = file_info2[file1]
            if info1 == info2:
                perfect_matches += 1
            else:
                files_only_in_dir1 += 1
        else:
            files_only_in_dir1 += 1

    files_only_in_dir2 = len(file_info2) - perfect_matches

    return files_scanned, perfect_matches, files_only_in_dir1, files_only_in_dir2




# Example usage
dir1 = r'A:\Users\Ada\Desktop\Audio sort out\1\\' #/path/to/folder1'
dir2 =  r'A:\Users\Ada\Desktop\Audio sort out\2\\'  #'/path/to/folder2'

files_scanned_1, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2 = compare_directories(dir1, dir2)
num_subdirectories1 = count_subdirectories(dir1)
num_subdirectories2 = count_subdirectories(dir2)

print(f"\nIn Data Dir {dir1}")
print(f" there are {files_scanned_1} files in {num_subdirectories1} subdirectories")

print(f"\nIn Target Dir {dir2}")


print("\nNumber of files with a perfect match:", num_perfect_matches)
print("Number of files present in folder 1 but not found in folder 2:", num_files_only_in_dir1)
print("Number of files present in folder 2 but not found in folder 1:", num_files_only_in_dir2)
