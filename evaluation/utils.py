'''
module for process_result, api_request
'''
# utils
import requests

def process_result(id_list, metadata, output, type, group_name):
    y_true_list = []
    y_pred_list = []
    for num in id_list:
        if num in metadata.keys():
            y_true = metadata[str(num)][type]
            y_pred = output[str(num)][group_name].split(',')
            y_pred = [i.strip() for i in y_pred]
            y_true_list.append(y_true)
            y_pred_list.append(y_pred)
    
    
    return y_true_list, y_pred_list

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