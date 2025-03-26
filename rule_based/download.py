from prepare import download_and_unzip_files, filter_models_by_year
import os

def delete_zip_files(directory):
    """
    Recursively deletes all .zip files in the given directory.
    
    Args:
        directory (str): The root directory to start searching for zip files.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file ends with .zip (case insensitive)
            if file.lower().endswith('.zip'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

def main():
    file_code_list = filter_models_by_year(2022) # min_year = 2020 by default
    print("Total number of models after 2022:", len(file_code_list))
    sample_folder = '../2022_Data'
    num_file = len(file_code_list)
    download_and_unzip_files(file_code_list, sample_folder, num_file)
    delete_zip_files(sample_folder)

if __name__ == "__main__":
    main()