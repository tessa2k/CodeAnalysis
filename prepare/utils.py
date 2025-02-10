# utils
import os
import json
import requests
from dotenv import load_dotenv

MODEL_CODE_FILE_PATH = "data/model_id_list.json"

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

def save_model_code_to_json():
    model_url = "/api/v1/models"
    MODEL_CODE_FILE_PATH = "data/model_id_list.json"
    model_code_list = api_request(model_url, method = 'GET')
    # print(len(model_id_list))
    if os.path.exists(MODEL_CODE_FILE_PATH):
        os.remove(MODEL_CODE_FILE_PATH)
    with open(MODEL_CODE_FILE_PATH, "w") as f:
        json.dump(model_code_list, f)


def get_model_code():
    with open(MODEL_CODE_FILE_PATH, "r") as f:
        model_code_list = json.load(f)
    return model_code_list

