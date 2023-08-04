# BackupInspector
Verify Data Backups by Comparing Directory Contents

[![Language](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Equations](#equations)
- [Effect of number of terms on accuracy](#effect-of-number-of-terms-on-accuracy)
- [License](#license)
- [Contributions](#contributions)
- [Contact](#contact)

## Introduction
BackupInspector is a simple python script that allows you to compare the contents of two sets of directories. It identifies file matches and reports the number of unmatched files and their filenames. 

### Features
- Supports comparing multiple directories simultaneously.
- Option to use fast or rigourous comparison.
- Outputs a txt file with the results of the comparison.

## Installation

1. Make sure you have Python 3.x installed on your system.
2. Install the required libraries by running the following command:
   ```
   pip install filecmp tqdm
   ```

## Usage

1. Clone the repository or download the Python script `directory_compare.py`.
2. Import the required libraries and functions in your Python script:

```python
import os
import filecmp
from tqdm import tqdm
```

3. Place the `directory_compare.py` script in the same directory as your main script.
4. Use the `compare_directories` function to compare two directories:

```python
dir1 = r'/path/to/folder1'
dir2 = r'/path/to/folder2'

files_scanned_1, num_perfect_matches, num_files_only_in_dir1, num_files_only_in_dir2 = compare_directories(dir1, dir2)
num_subdirectories1 = count_subdirectories(dir1)
num_subdirectories2 = count_subdirectories(dir2)

print(f"\nIn Data Dir {dir1}")
print(f" there are {files_scanned_1} files in {num_subdirectories1} subdirectories")

print(f"\nIn Target Dir {dir2}")
print("Number of files with a perfect match:", num_perfect_matches)
print("Number of files present in folder 1 but not found in folder 2:", num_files_only_in_dir1)
print("Number of files present in folder 2 but not found in folder 1:", num_files_only_in_dir2)
```

## Configuration

The script allows you to configure two main options:

1. Shallow Comparison (True/False):
   - If set to True, the script will perform a quick comparison based on file name and modified date.
   - If set to False, the script will conduct a more thorough comparison of file contents, which might take longer for large files.

2. Multiple Directories Comparison:
   - The script supports comparing multiple directories by providing multiple directory paths as inputs to the `compare_directories` function.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

Feel free to contribute to this project by reporting issues or creating pull requests. Happy coding!
















# Directory Comparison Tool

This repository contains a Python script that provides functionality to compare two directories and identify common files, perfect matches, and files exclusive to each directory. The tool consists of three main functions: `count_subdirectories`, `file_generator`, and `compare_directories`.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Functions](#functions)
    1. [count_subdirectories](#count_subdirectories)
    2. [file_generator](#file_generator)
    3. [compare_directories](#compare_directories)
4. [Contributing](#contributing)
5. [License](#license)

## Installation

To use the directory comparison tool, ensure you have Python 3 installed on your system. The required dependencies (`os` and `stat`) come bundled with Python. No additional installation is required.

Clone the repository or download the script `directory_comparison.py` to your local machine.

```bash
git clone https://github.com/your_username/directory-comparison-tool.git
```

## Usage

Before using the tool, make sure you have two directories that you want to compare, let's call them `dir1` and `dir2`.

To count the number of subdirectories in a given directory, use the `count_subdirectories` function:

```python
import directory_comparison

directory = "/path/to/your/directory"
subdirectories_count = directory_comparison.count_subdirectories(directory)
print("Number of subdirectories:", subdirectories_count)
```

To compare two directories, use the `compare_directories` function:

```python
import directory_comparison

dir1 = "/path/to/your/dir1"
dir2 = "/path/to/your/dir2"

files_scanned, perfect_matches, files_only_in_dir1, files_only_in_dir2 = directory_comparison.compare_directories(dir1, dir2)

print("Files scanned:", files_scanned)
print("Perfect matches:", perfect_matches)
print("Files only in dir1:", files_only_in_dir1)
print("Files only in dir2:", files_only_in_dir2)
```

## Functions

### count_subdirectories

```python
def count_subdirectories(directory):
    """
    Count the number of subdirectories in the given directory.

    Parameters:
        directory (str): The path to the directory.

    Returns:
        int: Number of subdirectories in the given directory.
    """
```

This function counts the number of subdirectories in a given directory. It takes a string parameter `directory`, which should be the path to the directory you want to analyze. The function returns an integer representing the total count of subdirectories.

### file_generator

```python
def file_generator(directory):
    """
    A generator that yields all file paths within the directory (including subdirectories).

    Parameters:
        directory (str): The path to the directory.

    Yields:
        str: File path.
    """
```

**Note:** The `file_generator` function seems to be marked as "BROKEN," so use it with caution.

This generator function yields all the file paths within a given directory, including files present in its subdirectories. It takes a string parameter `directory`, which should be the path to the directory you want to traverse. The function yields individual file paths as strings one by one.

### compare_directories

```python
def compare_directories(dir1, dir2):
    """
    Compare two directories and identify common files, perfect matches, and exclusive files.

    Parameters:
        dir1 (str): The path to the first directory.
        dir2 (str): The path to the second directory.

    Returns:
        tuple: A tuple containing four integers representing:
            1. Total files scanned
            2. Number of perfect matches (same size and modification time)
            3. Number of files only present in dir1
            4. Number of files only present in dir2
    """
```

This function compares two directories (`dir1` and `dir2`) and identifies common files, perfect matches, and files exclusive to each directory. It returns a tuple containing four integers:

1. `files_scanned`: The total number of files scanned (including files in both directories).
2. `perfect_matches`: The number of files with the same size and modification time in both directories.
3. `files_only_in_dir1`: The number of files only present in `dir1`.
4. `files_only_in_dir2`: The number of files only present in `dir2`.

## Contributing

Contributions to this repository are welcome. If you find any bugs or have suggestions for improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.




## License
Form-Factor Calculator is distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributions
Contributions to this Form-Factor Calculator are welcome! If you encounter any issues or have suggestions for improvements, or new sample shapes we can compute please open an issue or a pull request on the [GitHub repository](https://github.com/adillwma/Material_Science_Form_Factor_Calculator).


## Contact
For any inquiries, feel free to reach out to me at adillwmaa@gmail.com.
