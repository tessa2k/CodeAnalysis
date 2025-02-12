# utils
import os
import json
import requests
import zipfile
import msal
import shutil
from dotenv import load_dotenv

MODEL_CODE_FILE_PATH = "data/model_id_list.json"
ACCEPTABLE_EXTENSIONS = ('.py', '.cpp', '.java', '.m', '.txt', '.h', '.data', 
                         '.html', '.c', '.mod', '.g', '.p', ".ode", ".html", ".zip")  # Now includes .zip

def _api_request(url, method = 'GET', headers=None, params=None, json_data=None):
    '''
    Parameters:
      - url (str): The API endpoint.
      - method (str): The HTTP method ('GET', 'POST', etc.). Default is 'GET'.
      - headers (dict): Optional headers for the request.
      - params (dict): Optional URL parameters for the request.
      - json_data (dict): Optional JSON data for POST requests.

      Returns:
      - response (dict): Parsed JSON response from the API.
    '''
    url = "https://modeldb.science/" + url
    try:
        # Determine the request method
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=json_data)
        else:
            raise ValueError("Unsupported HTTP method: {}".format(method))

        # Check for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")

    return None

def save_model_code_to_json():
    model_url = "/api/v1/models"
    MODEL_CODE_FILE_PATH = "data/model_id_list.json"
    model_code_list = _api_request(model_url, method = 'GET')
    # print(len(model_id_list))
    if os.path.exists(MODEL_CODE_FILE_PATH):
        os.remove(MODEL_CODE_FILE_PATH)
    with open(MODEL_CODE_FILE_PATH, "w") as f:
        json.dump(model_code_list, f)


def get_model_code():
    with open(MODEL_CODE_FILE_PATH, "r") as f:
        model_code_list = json.load(f)
    return model_code_list

def traverse_folder(path, file_list):
    """
    Recursively traverses a folder, adding files with acceptable extensions to file_list.
    If a ZIP file is found, it extracts it and processes the contents.
    
    Args:
        path (str): The directory path to traverse.
        file_list (list): A list to store the paths of acceptable files.
    """
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        
        if os.path.isdir(full_path):
            print(f'Traverse folder: {full_path}')
            traverse_folder(full_path, file_list)

        elif entry.lower().endswith(".zip"):  # If it's a ZIP file, extract it
            extract_path = os.path.join(path, f"{entry}_extracted")  # New folder for extracted files
            
            if not os.path.exists(extract_path):  # Avoid re-extracting
                os.makedirs(extract_path)
                with zipfile.ZipFile(full_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)  # Extract files
                    print(f"Extracted {full_path} to {extract_path}")
            
            # Recursively traverse the extracted folder
            traverse_folder(extract_path, file_list)

        elif entry.lower().endswith(ACCEPTABLE_EXTENSIONS):
            file_list.append(full_path)

def __connect_onedrive():
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

def download_and_unzip_files(file_code_list, sample_folder, num_file):
    headers = __connect_onedrive()
    if os.path.exists(sample_folder):
        shutil.rmtree(sample_folder)
    os.makedirs(sample_folder)

    for code in file_code_list[:num_file]:
        code = str(code)
        zip_filename = f"{code}.zip"
        local_path = os.path.join(sample_folder, zip_filename)
        extract_path = os.path.join(sample_folder, code)

        # download zip file into local directory
        download_endpoint = f'https://graph.microsoft.com/v1.0/me/drive/root:/modeldb-code-analysis/modeldb-zips/{code}.zip:/content'
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
