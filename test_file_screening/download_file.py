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

# GLOBAL VARIABLES
ACCEPTABLE_EXTENSIONS = ('.py', '.cpp', '.java', '.m', '.txt', '.h', '.data', 
                            '.html', '.c', '.mod', '.g', '.p', ".ode", ".html")  # Adjust as needed

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


if __name__ == "__main__":
    # authorization
    authorization_headers = connect_onedrive()
    file_model_id = get_model_id(authorization_headers)
    print(f"Total number of files is {len(file_model_id)}")
    # download files
    sample_folder = '/Users/mengmengdu/Desktop/CodeAnalysis/samples'
    file_code_list = shuffle(file_model_id)
    dwn_files(sample_folder, file_model_id, authorization_headers, file_code_list,100)
    file_code_path = "/Users/mengmengdu/Desktop/CodeAnalysis/samples/file_code_list.json"
    with open(file_code_path, "w") as f:
        json.dump(file_code_list, f)

