'''
RuleBased Model Version 1.1
python rule_based/rule_based.py

Items Improved:
- Precompile Regular Expressions in _get_regex_mapping()
- Process File by File instead of Line by Line in _traverse_file()
- Map to Sets in self.type_mapping (quicker to check __contain__)
- Optional for Parallel Traversing
'''

import os
import json
import re
from tqdm import tqdm
import pprint
from prepare.utils import _api_request, get_model_code
from concurrent.futures import ThreadPoolExecutor, as_completed  # Uncomment for parallelization

class RuleBased:
    _MODEL_IDS_URL = "/api/v1/models"
    _CAT_URL = "/api/v1/"
    _REG_EX = "manual_classifier_rules.json"
    _DATA_FOLDER = "../All_Data"  # Set this to your models directory
    _TYPE_TO_NAME = {
        "celltypes": "neurons",
        "currents": "currents",
        "genes": "genes",
        "modelconcepts": "model_concept",
        "modeltypes": "model_type",
        "receptors": "receptors",
        "regions": "region"
    }
    
    def __init__(self, parallel: bool = False):
        self.parallel = parallel # True if apply parallel approach
        self.metadata_types = _api_request(self._CAT_URL)
        self.model_id_list = get_model_code()
        # Convert type mapping values to sets for faster membership tests:
        self.type_mapping = {k: set(v) for k, v in self._fetch_type_mapping().items()}
        self.regex_mapping = self._get_regex_mapping()  # precompiled regex mapping
        self.type_list = list(self._TYPE_TO_NAME.keys())
        self.file_extensions = set()

    def _traverse_file(self, model_id):
        '''
        Traverse the folder given a model id and classify them based on regex mapping.
        Returns:
            set: matched categories
        '''
        directory = os.path.join(self._DATA_FOLDER, str(model_id))
        matched_categories = set()
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file_path)[1]
                self.file_extensions.add(file_extension) # collect file extensions
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read entire file content (adjust if files are huge)
                        content = f.read()
                    matched_categories.update(self._search_regex(content))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        return matched_categories
    
    def _search_regex(self, text):
        '''
        Search for patterns in the provided text using precompiled regex objects.
        '''
        matched = set()
        for key, (compiled, categories) in self.regex_mapping.items():
            if isinstance(compiled, list):
                if all(comp.search(text) for comp in compiled):
                    matched.update(categories)
            else:
                if compiled.search(text):
                    matched.update(categories)
        return matched
    
    def _scan_all_files_sequential(self):
        """
        Scans all model folders in the dataset directory and applies `_traverse_file` 
        to each one, aggregating results.
        Returns:
            dict: mapping each model_id (folder) to its classified categories.
        """
        all_results = {}
        for model_id in tqdm(os.listdir(self._DATA_FOLDER)):
            model_path = os.path.join(self._DATA_FOLDER, model_id)
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
    
    def _scan_all_files_parallel(self):
        """
        Parallel scanning of model folders using a thread pool.
        """
        all_results = {}
        # Get list of model directories
        model_dirs = [
            d for d in os.listdir(self._DATA_FOLDER)
            if os.path.isdir(os.path.join(self._DATA_FOLDER, d))
        ]
        with ThreadPoolExecutor() as executor:
            future_to_model = {executor.submit(self._traverse_file, model_id): model_id 
                               for model_id in model_dirs}
            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    matched_categories = future.result()
                    results = self._match_results(matched_categories)
                    if results:
                        all_results[model_id] = results
                except Exception as e:
                    print(f"Error scanning {model_id}: {e}")
        return all_results

    def _scan_all_files(self):
        """
        Scans all model folders in the dataset directory and applies `_traverse_file` 
        to each one, aggregating results.
        
        Returns:
            dict: Mapping each model_id (folder) to its classified categories.
        """
        if self.parallel:
            return self._scan_all_files_parallel()
        else:
            return self._scan_all_files_sequential()

    def _fetch_type_mapping(self):
        '''
        Create a mapping between metadata_type and metadata_type_names.
        Returns:
            dict: keys are metadata_types and values are lists of metadata_type_names.
        '''
        mapping = {}
        for metadata_type in self.metadata_types:
            url = f"/api/v1/{metadata_type}/name"
            try:
                metadata_names = _api_request(url)
                if metadata_names is None:
                    raise ValueError(f"API response for {metadata_type} returned None.")
                mapping[metadata_type] = metadata_names
            except Exception as e:
                print(f"Error fetching metadata for {metadata_type}: {e}")
                mapping[metadata_type] = []
        return mapping
    
    def _get_regex_mapping(self):
        '''
        Get and precompile regular expression mapping from manual_classifier_rules.json.
        '''
        with open(self._REG_EX, "r") as f:
            regex_mapping = json.load(f)
        
        compiled_mapping = {}
        for pattern, categories in regex_mapping.items():
            if "$" in pattern:
                sub_patterns = pattern.split("$")
                compiled_subs = [re.compile(sub_p, re.IGNORECASE) for sub_p in sub_patterns]
                compiled_mapping[pattern] = (compiled_subs, categories)
            else:
                compiled_mapping[pattern] = (re.compile(pattern, re.IGNORECASE), categories)
        return compiled_mapping

    def _match_results(self, matched_categories: set):
        '''
        Map matched_categories to metadata types.
        '''
        results = {metadata_type: [] for metadata_type in self.type_list}
        for item in matched_categories:
            for metadata_type in self.type_list:
                if item in self.type_mapping.get(metadata_type, set()):
                    results[metadata_type].append(item)
        return results

    def get_extentions(self):
        '''
        Get the set of file extension among all models
        '''
        return self.file_extensions
    
    def print_results(self, model_id):
        '''
        Print partial results for testing.
        '''
        all_results = self._scan_all_files()
        if model_id not in self.model_id_list:
            print('ID is not found in ModelDB.')
        print(all_results.get(str(model_id), {}))

    def write_results(self):
        '''
        Write results into a json file.
        '''
        results = self._scan_all_files()
        with open("rule_based_results.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == '__main__':
    # some local tests
    model = RuleBased(True)
    model._DATA_FOLDER = "sampleAlzheimer"  # Set your folder here
    
    model_id = 21329
    matched_categories = model._traverse_file(model_id)
    print("Matched Categories:")
    print(matched_categories)
    pprint.pprint(model._match_results(matched_categories))
    print()

    ground_truth_path = "evaluation/model_metadata.json"
    with open(ground_truth_path, "r") as f:
        ground_truth = json.load(f)
    pprint.pprint(ground_truth.get(str(model_id), {}))
