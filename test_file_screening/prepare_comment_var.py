import os
import re
import shutil
import json
import zipfile
import random
import requests
from dotenv import load_dotenv

# GLOBAL VARIABLES
ACCEPTABLE_EXTENSIONS = ('.py', '.cpp', '.java', '.m', '.txt', '.h', '.data', 
                            '.html', '.c', '.mod', '.g', '.p', ".ode", ".html")  #.mdl
            
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

def traverse_folder_extract_comments_variables(path, model_code, extracted_data):
    """
    Traverse through all files in a directory, extract comments and variables from each file.
    """
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            print(f'Traverse folder: {full_path}')
            traverse_folder_extract_comments_variables(full_path, model_code, extracted_data)
        else:
            if not entry.lower().endswith(ACCEPTABLE_EXTENSIONS):
                continue
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                comments = extract_comments(content, entry)
                variables = extract_variables(content)
                file_name = os.path.basename(full_path)
                extracted_data[model_code][file_name] = {"comments": comments, "variables": variables}

def extract_comments(content, filename):
    file_extension = os.path.splitext(filename)[1] 
    comment_patterns = {
        '.py': r'#.*',
        '.cpp': r'//.*|/\*.*?\*/',
        '.java': r'//.*|/\*.*?\*/',
        '.c': r'//.*|/\*.*?\*/',
        '.h': r'//.*|/\*.*?\*/',
        '.html': r'<!--.*?-->'  ,
        '.mod': r'COMMENT(.*?)ENDCOMMENT' ,#need to change
        '.ode': r'%.*',
        '.txt': r'.*',
        '.m': r'%.*' ,
        '.g': r'//.*|/\*.*?\*/' 
    }
    pattern = comment_patterns.get(file_extension, r'')
    return re.findall(pattern, content, re.DOTALL) if pattern else []


def extract_variables(content):
    """
    Extract variable names from code files using regex.
    """
    variable_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    return list(set(re.findall(variable_pattern, content)))

def process_files(sample_folder, output_file_folder, file_code_list, num_extracted_files):
    os.makedirs(output_file_folder, exist_ok=True)
    extracted_data = {}
    for code in file_code_list[:num_extracted_files]:
        path = os.path.join(sample_folder, code)
        if os.path.isdir(path):
            extracted_data[code] = {}
            traverse_folder_extract_comments_variables(path, code, extracted_data)
    for code, data in extracted_data.items():
        with open(os.path.join(output_file_folder, f'{code}_extracted.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    # get the file_model_id
    file_code_path = "/Users/mengmengdu/Desktop/CodeAnalysis/samples/file_code_list.json"
    with open(file_code_path, "r") as f:
        file_code_list = json.load(f)
    print(f"Total number of files is {len(file_code_list)}")
    sample_folder = '/Users/mengmengdu/Desktop/CodeAnalysis/samples'

    # file screening
    # ================================== Need to fill ====================================
    output_file_folder = '/Users/mengmengdu/Desktop/CodeAnalysis/data/extracted_data'
    if os.path.exists(output_file_folder):
        shutil.rmtree(output_file_folder)
    process_files(sample_folder, output_file_folder, file_code_list, 20)
   