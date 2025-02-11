'''
RuleBased Model
python rule_based/rule_based.py
'''

import os
import json
import re
from tqdm import tqdm
import pprint
from prepare.utils import api_request, get_model_code

class RuleBased:
    _MODEL_IDS_URL = "/api/v1/models"
    _CAT_URL = "/api/v1/"
    _REG_EX = "manual_classifier_rules.json"
    _DATA_FOLDER = "" # change this for the 1898 models
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
        self.metadata_types = api_request(self._CAT_URL)
        self.model_id_list = get_model_code()
        self.type_mapping = self._fetch_type_mapping()
        self.regex_mapping = self._get_regex_mapping()
        self.type_list = list(self._TYPE_TO_NAME.keys())

    def _traverse_file(self, model_id):
        '''
        Traverse the folder given a model id and classify them based on regex mapping.
        Returns:
            set: matched categories
        '''
        directory = os.path.join(self._DATA_FOLDER, str(model_id))
        matched_categories = set()
        for root, _, files in os.walk(directory):
            for file in tqdm(files):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        matched_categories.update(self._search_regex(line, matched_categories))         
        return matched_categories
    
    def _search_regex(self, line, matched_categories):
        '''
        Search for patterns the regex file
        '''
        for pattern, categories in self.regex_mapping.items():
            # add a transformation step for "pattern" items here 
            if "$" in pattern:
                sub_patterns = pattern.split("$")
                if all(re.search(sub_p, line, re.IGNORECASE) for sub_p in sub_patterns):
                    matched_categories.update(categories)
            else:
                if re.search(pattern, line, re.IGNORECASE):
                    matched_categories.update(categories)
        return matched_categories
    
    def _scan_all_files(self):
        """
        Scans all model folders in the dataset directory and applies `_traverse_file` 
        to each one, aggregating results.

        Returns:
            dict: A dictionary mapping each model_id (folder) to its classified files and categories.
        """
        all_results = {}
        for model_id in os.listdir(self._DATA_FOLDER):
            model_path = os.path.join(self._DATA_FOLDER, model_id)
            # Ensure it's a directory (skip files)
            if os.path.isdir(model_path):
                print(f"Scanning folder: {model_id}...")
                try:
                    matched_categories = self._traverse_file(model_id)
                    results = self._match_results(matched_categories)
                    if results:
                        all_results[model_id] = results
                except Exception as e:
                    print(f"Error scanning {model_id}: {e}")
        return all_results
    
    def _fetch_type_mapping(self):
        '''
        Create a mapping between metadata_type and metadata_type_names
        Returns:
            dict: A dictionary where keys are metadata_types and values are lists of metadata_type_names.
        '''
        mapping = {}
        for metadata_type in self.metadata_types:
            url = f"/api/v1/{metadata_type}/name"
            try:
                metadata_names = api_request(url)
                if metadata_names is None:
                    raise ValueError(f"API response for {metadata_type} returned None.")
                mapping[metadata_type] = metadata_names
            except Exception as e:
                print(f"Error fetching metadata for {metadata_type}: {e}")
                mapping[metadata_type] = []
        return mapping
    
    def _get_regex_mapping(self):
        '''
        Get regular expression mapping from manual_classifier_rules.json
        '''
        with open(self._REG_EX, "r") as f:
            regex_mapping = json.load(f)
        return regex_mapping

    # TODO: match the result with the metadata_type mapping
    def _match_results(self, matched_categories: set):
        '''
        Map matched_categories to metadatatypes
        '''
        results = {metadata_type: [] for metadata_type in self.type_list}
        for item in matched_categories:
            for metadata_type in self.type_list:
                if item in set(self.type_mapping[metadata_type]):
                    results[metadata_type].append(item)
        return results

    def print_results(self, model_id):
        '''
        Print partial results for testing
        '''
        all_results = self._scan_all_files()
        if model_id not in self.model_id_list:
            print('ID is not found in ModelDB.')
        print(all_results[model_id])

    def write_results(self):
        '''
        Write results into a json file
        '''
        pass

if __name__ == '__main__':
    model = RuleBased()
    model._DATA_FOLDER = "sampleAlzheimer"
    
    model_id = 21329
    matched_categories = model._traverse_file(model_id)
    print(matched_categories)
    pprint.pprint(model._match_results(matched_categories))
    print()

    ground_truth_path = "evaluation/model_metadata.json"
    with open(ground_truth_path, "r") as f:
        ground_truth = json.load(f)
    pprint.pprint(ground_truth[str(model_id)])