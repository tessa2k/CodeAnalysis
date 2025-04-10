# utils
import os
from tqdm import tqdm
from openai import OpenAI
import pandas as pd
from prepare import *
import io
import zipfile
import json
import re
import msal
import requests
import random
import pprint
import shutil
from dotenv import load_dotenv

ACCEPTABLE_EXTENSIONS = ('.py', '.cpp', '.java', '.m', '.txt', '.h', '.data', 
                            '.html', '.c', '.mod', '.g', '.p', ".ode", ".html")  # Adjust as needed

def concat_files(model_code, file_list, output_path, num_header_lines = 40):

    output_file = f'{output_path}/{model_code}_header.txt'

    # concat files
    with open(output_file, 'w', encoding='utf-8') as output_file:
        for file_path in file_list:
            output_file.write(f'=== Following is the header of {file_path} ===\n')  # Write the file path
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= num_header_lines:  # only read first 20 lines
                        break
                    output_file.write(line)
                output_file.write('\n\n')  # add a newline between files

    print(f"Headers of the files have been concatenated into {output_file.name}")


if __name__ == "__main__":

    #model_code_list = get_model_code()
    model_code_list=filter_models_by_year(min_year=2022)
    print(model_code_list[:106])
    # samples_path = 'samples'
    #download_and_unzip_files(model_code_list, samples_path, 100)

    # create new folder for header-concatenated files
    concat_file_path = 'data/concat_header'
    if os.path.exists(concat_file_path):
        shutil.rmtree(concat_file_path)
    os.makedirs(concat_file_path)
 
    for model_code in model_code_list:
        list_of_all_files = []
        path = f'samples/{model_code}'
        if not os.path.exists(path):
            print(f"Skipping {model_code}: No directory found in samples/")
            continue

        traverse_folder(path, list_of_all_files)
        if not list_of_all_files:
            print(f"Skipping {model_code}: No valid files found in {path}")
            continue

        concat_files(model_code, list_of_all_files, concat_file_path)