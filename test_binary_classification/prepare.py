import requests
import pprint
import time
from tqdm import tqdm
import json
import pandas as pd

# utils
import os
import tqdm
from openai import OpenAI
import io
import zipfile
import json
import re
import msal
import requests
import random
import pprint
from dotenv import load_dotenv

def api_request(url, method = 'GET', headers=None, params=None, json_data=None):
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


def sample_negative(list_from, list_exclude, n, seed=None):
    '''
    Parameters:
      - list_from: the list to sample negative samples
      - list_exclude: the list with all positive samples
      - n: the number of negative samples we need
      - seed: to set random seed
    '''
    if seed is not None:
        random.seed(seed)
    list_filtered = [i for i in list_from if i not in set(list_exclude)]
    if len(list_filtered) < n:
        raise ValueError("Not enough elements to sample after excluding the positive samples.")
    # Randomly sample n elements
    return random.sample(list_filtered, n)

def prepare_file_code_id():
    # Access "modeldb-code-analysis/modeldb-zips"
    endpoint = 'https://graph.microsoft.com/v1.0/me/drive/root:/modeldb-code-analysis/modeldb-zips:/children'
    file_code_id = {}
    while endpoint:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            files_in_subfolder = response.json().get('value', [])
            for file in files_in_subfolder:
                file_code = file['name'][:-4]
                file_code_id[file_code] = file['id']
            endpoint = response.json().get('@odata.nextLink')
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
           
    return file_code_id

def extract_samples(sample_folder, file_code_id, pos_samples, neg_samples):
    '''
    Parameters:
        - file_code_id: a dictionary with model id and its corresponding file id
        - pos_samples: list of model ids with positive labels
        - neg_samples: list of model ids with negative labels
    Download files
    '''
    os.makedirs(sample_folder, exist_ok=True)
    for code in tqdm.tqdm(list(file_code_id.keys())):
        file_id = file_code_id[code]
        try:
            numeric_code = int(''.join(filter(str.isdigit, code)))
            if numeric_code in set(pos_samples + neg_samples):
                zip_filename = f"{code}.zip"
                local_path = os.path.join(sample_folder, zip_filename)
                extract_path = os.path.join(sample_folder, code)

                # download zip file into local directory
                download_endpoint = f'https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content'
                response = requests.get(download_endpoint, headers=headers)

                if response.status_code == 200:
                    with open(local_path, 'wb') as file:
                        file.write(response.content)
                    
                    with zipfile.ZipFile(local_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                else:
                    print(f"Failed to download {zip_filename}")
        except ValueError:
            print(f"Skipping invalid code: {code}")

if __name__ == "__main__":
    '''
    To change model concept for experiments, change variables:
    - CONCEPT_NAME = "Aging/Alzheimer`s"
    - sample_folder: model output folder directory
    - df.to_csv('binary_labels_{new_concept_name}.csv', index=False)
    '''
    print("Prepare positive and negative samples...")
    MODEL_IDS = "/api/v1/models"
    MODEL_ID_FILTER_HEADER = "/api/v1/models?model_concept="

    # the concept name to be classified
    # CONCEPT_NAME = "Parkinson's"
    CONCEPT_NAME = "Aging/Alzheimer`s"
    MODEL_ID_FILTER_URL = MODEL_ID_FILTER_HEADER + CONCEPT_NAME

    pos_samples= api_request(MODEL_ID_FILTER_URL)
    print("Positive Samples:")
    print(pos_samples)

    all_ids = api_request(MODEL_IDS)
    neg_samples = sample_negative(all_ids, pos_samples, len(pos_samples), seed=123123)
    print("Negative Samples:")
    print(neg_samples)

    # test file extraction
    print("Loading Azure application client...")
    load_dotenv()

    # Azure application client info
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    tenant_id = os.getenv('TENANT_ID')

    # Get access token
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    scopes = ['Files.Read', 'User.Read', 'Files.ReadWrite']
    app = msal.PublicClientApplication(client_id, authority=authority)

    # Request token
    result = app.acquire_token_interactive(scopes=scopes)

    if "access_token" in result:
        access_token = result["access_token"]
        headers = {'Authorization': f'Bearer {access_token}'}

    print("Preparing file_code_id ...")
    file_code_id = prepare_file_code_id()

    # write file_code_id, labels into a DataFrame
    # ground truth labels
    labels = {i: 1 for i in pos_samples}
    labels.update({i: 0 for i in neg_samples})
    df = pd.DataFrame({
        'code': labels.keys(),
        'label': labels.values(),
        'file_id': [file_code_id[str(code)] for code in labels.keys()]
    })
    # df.to_csv('binary_labels_Parkinson.csv', index=False)
    df.to_csv('binary_labels_Alzheimer.csv', index=False)

    print("Extracting samples files and downloading...")
    # sample_folder = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/CodeAnalysis/sampleParkinsons'
    sample_folder = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/CodeAnalysis/sampleAlzheimer'
    extract_samples(sample_folder, file_code_id, pos_samples, neg_samples)