import requests
import json


class RuleBased:
    _MODEL_IDS_URL = "/api/v1/models"
    _CAT_URL = "/api/v1/"
    _REG_EX = "../manual_classifier_rules.json"
    _DATA_FOLDER = ""
    _TYPE_TO_NAME = {
        "celltypes": "neurons",
        "currents": "currents",
        "genes": "genes",
        "modelconcepts": "model_concept",
        "modeltypes": "model_type",
        "receptors": "receptors",
        "regions": "region"
    }
    
    def __init__(self):
        self.metadata_types = self._api_request(self._CAT_URL)
        self.model_id_list = self._api_request(self._MODEL_IDS_URL)

    # TODO: helper function to transform the regex
    def _transform_regex(self, ):
        '''
        Transform the regex file, specifically for the "$" sign
        '''
        pass

    def _traverse_single_folder(self, model_id):
        '''
        Traverse the folder of given model id, and match with regex
        '''
        pass
    
    # TODO: traverse folder, and walk through the regex
    def _traverse_all(self):
        pass
    
    def _mapping_type_name(self):
        '''
        Create a mapping between metadata_type and metadata_type_names
        Returns:
            dict: A dictionary where keys are metadata_types and values are lists of metadata_type_names.
        '''
        mapping = {}
        for metadata_type in self.metadata_types:
            url = f"/api/v1/{metadata_type}/name"
            try:
                metadata_names = self._api_request(url)
                if metadata_names is None:
                    raise ValueError(f"API response for {metadata_type} returned None.")
                mapping[metadata_type] = metadata_names
            except Exception as e:
                print(f"Error fetching metadata for {metadata_type}: {e}")
                mapping[metadata_type] = []
        for key, value in mapping.items():
            print(f"{key}: {len(value)} items retrieved")
        return mapping

    # TODO: match the result with the metadata_type mapping
    def _match_results(self):
        
        pass

    # TODO: save the result for all 1898 models
    def _view_results(self):
        pass

    def write_results(self):
        pass

    def _api_request(self, url, method = 'GET', headers=None, params=None, json_data=None):
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


if __name__ == '__main__':
    model = RuleBased()
    model._mapping_type_name()
