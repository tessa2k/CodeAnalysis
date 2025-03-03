# utils
import os
import re
import json
import requests
import zipfile
import msal
import shutil
import random
from tqdm import tqdm
from dotenv import load_dotenv

MODEL_CODE_FILE_PATH = "data/model_id_list.json"
MODEL_FILEID_PATH = "data/model_fileid.json"
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

def __save_model_code_to_json():
    """
    Fetches a list of model codes from an API and saves them as a JSON file.

    - Retrieves the model code list from the API endpoint.
    - If an existing JSON file is found, it is removed before writing the new data.
    - Saves the model code list in "data/model_id_list.json".

    Raises:
        Exception: If the API request fails.
    """

    model_url = "/api/v1/models"
    MODEL_CODE_FILE_PATH = "data/model_id_list.json"
    model_code_list = _api_request(model_url, method = 'GET')
    random.seed(10)
    random.shuffle(model_code_list)
    # print(len(model_id_list))
    if os.path.exists(MODEL_CODE_FILE_PATH):
        os.remove(MODEL_CODE_FILE_PATH)
    with open(MODEL_CODE_FILE_PATH, "w") as f:
        json.dump(model_code_list, f)

def get_model_code():
    """
    Reads and returns the model code list from a JSON file.

    Returns:
        list: A list of model codes loaded from "data/model_id_list.json".

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        JSONDecodeError: If the JSON file is not formatted correctly.
    """

    with open(MODEL_CODE_FILE_PATH, "r") as f:
        model_code_list = json.load(f)
    return model_code_list

def filter_models_by_year(min_year=2020):
    """
    Filters model codes based on the year in parentheses at the end of the model's name.

    Parameters:
    - min_year (int): Minimum year to filter the models (default is 2020).

    Returns:
    - list: A list containing model codes with years >= min_year.

    Usage:
    - Make sure current directory is root, filtered_model_code_list = filter_models_by_year(min_year=2022)
    """
    filtered_models = []  # List to store valid model codes
    model_codes = get_model_code()
    for model_id in tqdm(model_codes, desc="Processing Models", unit="model"):
        model_url = f"https://modeldb.science/api/v1/models/{model_id}"
        response = requests.get(model_url)

        if response.status_code != 200:
            print(f"Failed to fetch model {model_id}: HTTP {response.status_code}")
            continue  # Skip this model if API request fails

        model_data = response.json()
        model_name = model_data.get("name", "")

        # Extract year from the last four digits before the last closing parenthesis
        match = re.search(r'\((?:[^()]*\b(\d{4})\b[^()]*)\)$', model_name)

        # if match:
        #     model_year = int(match.group(1))
        #     if model_year >= min_year:
        #         filtered_models.append(model_id)
        #         print(f"Model {model_id} included: {model_name} ({model_year})")
        #     else:
        #         print(f"Model {model_id} excluded: {model_name} ({model_year})")
        # else:
        #     print(f"Model {model_id} has no valid year format: {model_name}")
        if match:
            model_year = int(match.group(1))
            if model_year >= min_year:
                filtered_models.append(model_id)
    return filtered_models

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

def _connect_onedrive():
    """
    Authenticates and connects to Microsoft OneDrive using MSAL (Microsoft Authentication Library).

    - Loads client credentials from environment variables.
    - Requests an access token for reading and writing files in OneDrive.
    - Returns an authorization header with the access token.

    Returns:
        dict: Authorization headers for API requests.

    Raises:
        Exception: If authentication fails.
    """

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

def _save_file_id_to_json():
    # Access "modeldb-code-analysis/modeldb-zips"
    headers = _connect_onedrive()
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
    if os.path.exists(MODEL_FILEID_PATH):
        os.remove(MODEL_FILEID_PATH)
    with open(MODEL_FILEID_PATH, "w") as f:
        json.dump(file_code_id, f)

def _get_file_id():
    with open(MODEL_FILEID_PATH, "r") as f:
        model_fileId_dict = json.load(f)
    return model_fileId_dict

def download_and_unzip_files(file_code_list, sample_folder, num_file):
    """
    Downloads and extracts ZIP files from OneDrive based on a list of file codes.

    Args:
        file_code_list (list): List of file codes to download.
        sample_folder (str): Local directory to store the downloaded files.
        num_file (int): Number of files to download from the list.

    Behavior:
        - Authenticates to OneDrive.
        - Downloads ZIP files using the given file codes.
        - Extracts the ZIP files into separate folders named after their file codes.
        - Deletes and recreates the `sample_folder` before downloading files.

    Raises:
        Exception: If the download request fails.
    """

    headers = _connect_onedrive()
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

if __name__ == "__main__":
    __save_model_code_to_json()
    _save_file_id_to_json()
