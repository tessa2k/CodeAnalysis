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

def connect_onedrive():
    load_dotenv()

    # Azure application client info
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    tenant_id = os.getenv('TENANT_ID')
    # redirect_uri = 'https://login.microsoftonline.com/common/oauth2/nativeclient'

    # Get access token
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    scopes = ['Files.Read', 'User.Read', 'Files.ReadWrite']
    app = msal.PublicClientApplication(client_id, authority=authority)

    # Request token
    result = app.acquire_token_interactive(scopes=scopes)

    if "access_token" in result:
        access_token = result["access_token"]
        headers = {'Authorization': f'Bearer {access_token}'}
    return headers

def get_model_id(headers):
    # Access "modeldb-code-analysis/modeldb-zips"
    endpoint = 'https://graph.microsoft.com/v1.0/me/drive/root:/modeldb-code-analysis/modeldb-zips:/children'
    file_code_id = {}
    while endpoint:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            files_in_subfolder = response.json().get('value', [])
            for file in files_in_subfolder:
                file_code = file['name'][:-4]
                if file_code.isdigit():
                    file_code_id[file_code] = file['id']
                # print(f"File Name: {file['name']} - File ID: {file['id']}")
            endpoint = response.json().get('@odata.nextLink')
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    return file_code_id

def shuffle(file_code_id):
    # get shuffled file code
    random.seed(20)
    file_code_list = list(file_code_id.keys())
    random.shuffle(file_code_list)
    return file_code_list

def dwn_files(sample_folder, file_code_id, headers, file_code_list, num_file=20):
    if os.path.exists(sample_folder):
        shutil.rmtree(sample_folder)
    os.makedirs(sample_folder)

    for code in file_code_list[:num_file]:
        file_id = file_code_id[code]
        zip_filename = f"{code}.zip"
        local_path = os.path.join(sample_folder, zip_filename)
        extract_path = os.path.join(sample_folder, code)

        # download zip file into local directory
        download_endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
        response = requests.get(download_endpoint, headers=headers)
        
        if response.status_code == 200:
            with open(local_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {zip_filename} to {local_path}")
            
            with zipfile.ZipFile(local_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print(f"Unzip {zip_filename} to {extract_path}")
        else:
            print(f"Failed to download {zip_filename}")

def get_score_metric(model_name, json_file_path, sample_folder):
    extract_folder = f'{sample_folder}/{model_name}'
    score_metric = []
    # Load rules from the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        rules = json.load(json_file)
    # Convert rules to a dictionary of regex patterns and replacements
    pattern_mapping = {re.compile(pattern): replacement for pattern, replacement in rules.items()}
    matched_files = []
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
    # authorization
    authorization_headers = connect_onedrive()
    file_model_id = get_model_id(authorization_headers)
    print(f"Total number of files is {len(file_model_id)}")
    # download files
    sample_folder = '/Users/tessakong/Desktop/CodeAnalysis/sample5'
    file_code_list = shuffle(file_model_id)
    dwn_files(sample_folder, file_model_id, authorization_headers, file_code_list)

    # file screening
    json_file_path = "/Users/tessakong/Desktop/CodeAnalysis/manual_classifier_rules.json"
    for code in file_code_list[:20]:
        print(f'==============================Processing model {code}==============================')
        file_id = file_model_id[code]
        scores = get_score_metric(code, json_file_path, sample_folder)
        scores.sort(key = lambda x: x[0], reverse = True)
        propotion = 0.5
        topK = int(propotion * len(scores))
        print(topK)
        if topK == 0:
            print(f"topK is 0 for model {code}, ignore")
            continue
        file_path_list = [s[1] for s in scores[:topK]]
        concat_files(code, sample_folder, file_path_list, topK)








