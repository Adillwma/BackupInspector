import os
import filecmp
from tqdm import tqdm


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

def file_generator(directory):
    for dir_path, dir_names, file_names in os.walk(directory):
        for file_name in file_names:
            yield os.path.join(dir_path, file_name)


def compare_directories(dir1, dir2):
    files_scanned_dir_1 = 0
    files_scanned_dir_2 = 0

    perfect_matches = 0
    files_only_in_dir1 = 0
    files_only_in_dir2 = 0

    gen1 = file_generator(dir1)
    gen2 = file_generator(dir2)


    for file1, file2 in tqdm(zip(gen1, gen2)):               # Counts all the mathing files
        files_scanned_dir_1 += 1
        files_scanned_dir_2 += 1
        if filecmp.cmp(file1, file2, shallow=True):
            perfect_matches += 1
        #else:
        #    print("WARNING MISMATCH  ERROR NOW OCCURING")

    for _ in gen1:                                          # Continues the count in dir one after the matched files
        files_only_in_dir1 += 1
        files_scanned_dir_1 += 1

    for _ in gen2:                                          # Continues the count in dir two after the matched files
        files_only_in_dir2 += 1
        files_scanned_dir_2 += 1

    # calulate number of subidrectories in each directory
    # num_subdirs_dir1 = len(os.listdir(dir1))
    # num_subdirs_dir2 = len(os.listdir(dir2))

    # Calulate number of mathes of each directory as percentage of total files in each directory
    percent_matched_dir1 = (perfect_matches / files_scanned_dir_2) * 100
    percent_matched_dir2 = (perfect_matches / files_scanned_dir_1) * 100

    return files_scanned_dir_1, files_scanned_dir_2, perfect_matches, files_only_in_dir1, files_only_in_dir2, percent_matched_dir1, percent_matched_dir2


# Example usage
dir1 =  r'A:\Users\Ada\Desktop\\'           #r'A:\Users\Ada\Desktop\Audio sort out\1\\' #/path/to/folder1'
dir2 =  r'I:\Ada 8700K Cobian Backup\8700K OS and User Folders\A\Users\Ada\Desktop\\'     #r'A:\Users\Ada\Desktop\Audio sort out\2\\'  #'/path/to/folder2'

files_scanned_1, files_scanned_2, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2, percent_matched_dir1, percent_matched_dir2 = compare_directories(dir1, dir2)
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
