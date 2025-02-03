# utils
import os
from tqdm import tqdm
from openai import OpenAI
import pandas as pd
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


def get_score_metric(model_name, json_file_path, sample_folder):
    extract_folder = f'{sample_folder}/{model_name}'
    score_metric = []
    # Load rules from the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        rules = json.load(json_file)
    # Convert rules to a dictionary of regex patterns and replacements
    pattern_mapping = {re.compile(pattern): replacement for pattern, replacement in rules.items()}
    # Define acceptable file extensions
    acceptable_extensions = ('.py', '.cpp', '.java', '.m', '.txt', '.h', '.data', 
                             '.html', '.c', '.mod', '.g', '.p', ".ode", ".html")  # Adjust as needed

    traverse_folder(extract_folder, score_metric, acceptable_extensions, pattern_mapping)
    return score_metric

def traverse_folder(path, score_metric, acceptable_extensions, pattern_mapping):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            print(f'Traverse folder: {full_path}')
            traverse_folder(full_path, score_metric, acceptable_extensions, pattern_mapping)
        else:
            # Check if the file extension is acceptable
            if not entry.lower().endswith(acceptable_extensions):
                continue  # Skip the file if the extension is not acceptable
            score = 0   
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in pattern_mapping.keys():
                    if pattern.search(content):  # If any rule matches the file content
                        score += 1
            score_metric.append((score, full_path))

def concat_files(code, sample_folder, file_path_list, topK):
    output_file_folder = f'{sample_folder}/match_file'
    os.makedirs(output_file_folder, exist_ok=True)
    output_file_path = f'{output_file_folder}/{code}_top{topK}.txt'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for file_path in file_path_list:
            output_file.write(f'=== {file_path} ===\n')  # Write the file path
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                output_file.write(f.read())  # Write the file content
                output_file.write('\n\n')  # Add a newline between files

    print(f"Concatenated file for model {code} have been saved to {output_file_path}")

if __name__ == "__main__":
    '''
    To change model concept for experiments, change variables:
    - sample_folder: model output folder directory
    - df = pd.read_csv("binary_labels_{concept_name}.csv")
    '''
    # file screening
    json_file_path = "../manual_classifier_rules.json"
    sample_folder = '../sampleAlzheimer' # change this for new concept name
    df = pd.read_csv("binary_labels_Alzheimer.csv") # change this for new concept name
    file_code_list = df["code"]
    for code in tqdm(file_code_list):
        scores = get_score_metric(code, json_file_path, sample_folder)
        scores.sort(key = lambda x: x[0], reverse = True)
        proportion = 0.5
        topK = int(proportion * len(scores))
        if topK == 0:
            print(f"topK is 0 for model {code}, ignore")
            continue
        file_path_list = [s[1] for s in scores[:topK]]
        concat_files(code, sample_folder, file_path_list, topK)