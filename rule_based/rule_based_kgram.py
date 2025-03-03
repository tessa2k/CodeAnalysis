'''
RuleBased Model Version 2.0
python rule_based/rule_based.py

Items Improved:
- Add tokenization
- Search expressions only based on kgram

Modified from modeldb2020
'''

import os
import json
import re
import argparse
import pprint
import tqdm
from prepare.utils import _api_request
from concurrent.futures import ThreadPoolExecutor, as_completed

class RuleBased:
    _MODEL_IDS_URL = "/api/v1/models"
    _CAT_URL = "/api/v1/"
    _REG_EX = "manual_classifier_rules.json"
    _DATA_FOLDER = "../2020_Data"  # current plan: only 2020+
    _TYPE_TO_NAME = {
        "celltypes": "neurons",
        "currents": "currents",
        "simenvironments": "modeling_application",
        "modelconcepts": "model_concept",
        "modeltypes": "model_type",
        "receptors": "receptors",
        "regions": "region"
    }
    _TOKEN = re.compile("[a-zA-Z0-9]+")

    def __init__(self, k=5, parallel: bool = False, batch: bool = True, batch_size: int = 50, max_num: int = 300):
        '''
        Parameter:
            k: determine the number of grams to search for regex
        Optional:
            parallel (bool): True if wanted to process folders in parallel
            batch (bool): True if wanted to process folders in batch
            batch_size (int): batch size
            max_num (int): maximum number of folders to assess in the DATA_FOLDER
        '''
        self.k = k # k gram
        self.parallel = parallel # True if apply parallel approach
        self.metadata_types = _api_request(self._CAT_URL)
        self.model_id_list = [d for d in os.listdir(self._DATA_FOLDER)
                         if os.path.isdir(os.path.join(self._DATA_FOLDER, d))]
        self.batch_size = batch_size
        self.batch = batch
        self.max_num = max_num

        # Convert type mapping values to sets for faster membership tests:
        self.type_mapping = {k: set(v) for k, v in self._fetch_type_mapping().items()}
        self.regex_mapping = self._get_regex_mapping()  # precompiled regex mapping
        self.type_list = list(self._TYPE_TO_NAME.keys())
        self.file_extensions = set()

    
    def get_extentions(self):
        '''
        Get the set of file extension among all models
        '''
        return self.file_extensions

    def scan_all_files_batches(self, retry_errors: bool = False,
                               errors_file: str = "rule_based/kgram_results/errors.json",
                               results_file: str = "rule_based/kgram_results/results_partial.json"):
        """
        Process all model folders in batches. If retry_errors is True, only process folders that previously errored.
        
        Args:
            retry_errors (bool): If True, read errors_file to process only errored folders.
            errors_file (str): File path to store errors.
            results_file (str): File path to store intermediate results.
        
        Returns:
            dict: Mapping each model_id (folder) to its classified categories.
        """
        # Get all model folder IDs.
        all_model_ids = self.model_id_list
        
        # If retry_errors is enabled, load the error model IDs.
        if retry_errors:
            try:
                with open(errors_file, "r") as f:
                    errors_data = json.load(f)
                error_model_ids = list(errors_data.keys())
                print("Retrying error model ids:", error_model_ids)
                all_model_ids = error_model_ids
            except Exception as e:
                print(f"Could not load {errors_file}: {e}")
                print("Processing all folders instead.")
        
        results_dict = {}  # To store successful results.
        errors_dict = {}   # To record errors.

        total = min(len(all_model_ids), self.max_num)
        
        for i in range(0, total, self.batch_size):
            batch = all_model_ids[i: i + self.batch_size]
            batch_idx = i // self.batch_size + 1
            print(f"\n--- Processing batch {batch_idx} (folders: {batch}) ---")
            if self.parallel:
                results_batch = {}
                errors_batch = {}
                with ThreadPoolExecutor() as executor:
                    future_to_model = {executor.submit(self._process_single_folder, model_id): model_id for model_id in batch}
                    for future in as_completed(future_to_model):
                        model_id = future_to_model[future]
                        try:
                            results = future.result()
                            results_batch[model_id] = results
                        except Exception as e:
                            errors_batch[model_id] = str(e)
                            print(f"Error processing model id {model_id}: {e}")
                # Update the overall dictionaries.
                results_dict.update(results_batch)
                errors_dict.update(errors_batch)
            else:
                results_batch, errors_batch = self._process_single_batch_sequential(batch)
                results_dict.update(results_batch)
                errors_dict.update(errors_batch)
            
            # Write intermediate results and errors.
            with open(results_file, "w") as f:
                json.dump(results_dict, f, indent=2)
            with open(errors_file, "w") as f:
                json.dump(errors_dict, f, indent=2)
            print(f"Batch {batch_idx} complete. Results and errors saved.")
        
        return results_dict

    def scan_all_files(self):
        """
        Scans all model folders in the dataset directory and applies `_traverse_file` 
        to each one, aggregating results.
        
        Returns:
            dict: Mapping each model_id (folder) to its classified categories.
        """
        if self.batch:
            return self.scan_all_files_batches()
        elif self.parallel:
            return self._scan_all_files_parallel()
        else:
            return self._scan_all_files_sequential()
    # **************************************
    # *           BEGIN PRIVATE            *
    # **************************************
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

    def _traverse_file(self, model_id):
        '''
        Traverse the folder given a model id and classify them based on regex mapping.
        Returns:
            set: matched categories
        '''
        directory = os.path.join(self._DATA_FOLDER, str(model_id))
        matched_categories = set()
        skip_extensions = {
        # Image formats.
        '.gif', '.jpg', '.jpeg', '.bmp', '.png', '.tiff', '.tif', '.ico', '.webp',
        # Multimedia (audio/video).
        '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.ogg', '.wav',
        # Archives / compressed files.
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.tgz',
        # Binary/executable files.
        '.exe', '.bin', '.dll', '.so', '.obj', '.pyc', '.class', '.npy',
        # Data files.
        '.csv', '.tsv', '.xlsx', '.xls', '.jsonl',
        # Other non-text binary files.
        '.iso', '.img', '.apk', '.msi'
        }
        for root, _, files in os.walk(directory):
            for file in tqdm.tqdm(files):
                if file.startswith('.'): 
                    continue # skip any file in __MACOSX
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file_path)[1]
                self.file_extensions.add(file_extension) # collect file extensions

                if file_extension in skip_extensions:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read entire file content (adjust if files are huge)
                        content = f.read()
                    # remove any numerical values larger than 100
                    content = re.sub(r'\b\d{3,}\b', '', content)
                    matched_categories.update(self._search_regex(content))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        return matched_categories

    def _process_single_folder(self, model_id): 
        """
        Process a single model folder: traverse its files and match results.
        
        Returns:
            dict: The classification results for this model folder.
        """
        matched_categories = self._traverse_file(model_id)
        return self._match_results(matched_categories)

    def _process_single_batch_sequential(self, batch):
        results_batch = {}  # To store successful results.
        errors_batch = {}   # To record errors.
        for model_id in tqdm.tqdm(batch):
            try:
                print(f"Processing {model_id}")
                results = self._process_single_folder(model_id)
                results_batch[model_id] = results
            except Exception as e:
                errors_batch[model_id] = str(e)
                print(f"Error processing model id {model_id}: {e}")
        return results_batch, errors_batch


    def _scan_all_files_sequential(self):
        """
        Scans all model folders sequentially.
        
        Returns:
            dict: Mapping each model_id (folder) to its classified categories.
        """
        results_dict = {}
        errors_dict = {}
        total = min(len(self.model_id_list), self.max_num)
        for model_id in tqdm.tqdm(self.model_id_list[:total]):
            try:
                results = self._process_single_folder(model_id)
                results_dict[model_id] = results
            except Exception as e:
                errors_dict[model_id] = str(e)
                print(f"Error processing model id {model_id}: {e}")
        return results_dict

    def _scan_all_files_parallel(self):
        """
        Scans all model folders in parallel.

        Returns:
            dict: Mapping each model_id (folder) to its classified categories.
        """
        results_dict = {}
        errors_dict = {}
        total = min(len(self.model_id_list), self.max_num)
        with ThreadPoolExecutor() as executor:
            future_to_model = {executor.submit(self._process_single_folder, model_id): model_id 
                               for model_id in self.model_id_list[:total]}
            for future in as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    results = future.result()
                    results_dict[model_id] = results
                except Exception as e:
                    errors_dict[model_id] = str(e)
                    print(f"Error processing model id {model_id}: {e}")
        # Optionally, you can write the full results and errors to files here.
        return results_dict

    # +++++++++++++++++++++++++++++++++++++++++
    # +           KGram helpers               +
    # +++++++++++++++++++++++++++++++++++++++++
    def _tokenize(self, text):
        """tokenize text"""
        return [word for word in self._TOKEN.findall(text)]

    def _get_n_grams_with_spaces(self, tokens, n):
        """return the n-grams comprised of consecutive tokens"""
        return [" %s " % " ".join(tokens[i : n + i]) for i in range(len(tokens) - n + 1)]

    def _search_regex(self, text):
        '''
        Search for patterns in the provided text using precompiled regex objects.
        '''
        matched = set()
        tokens = self._tokenize(text)
        n_grams = self._get_n_grams_with_spaces(tokens, self.k)
        for key, (compiled, categories) in self.regex_mapping.items():
            for item in n_grams:
                if isinstance(compiled, list):
                    if all(comp.search(item) for comp in compiled):
                        matched.update(categories)
                else:
                    if compiled.search(item):
                        matched.update(categories)
        return matched

if __name__ == "__main__":
    # tests for single id
    model = RuleBased(True)
    model._DATA_FOLDER = "../2020_Data"  # Set your folder here
    parser = argparse.ArgumentParser(
        description="Run RuleBased Model for a single id."
    )
    parser.add_argument(
        "-d", type=int, default=182129,
        help="Single model id."
    )
    args = parser.parse_args()
    model_id = args.d
    print(f"Run rule-based model for id = {model_id}")
    matched_categories = model._traverse_file(model_id)
    print("Matched Categories:")
    # print(matched_categories)
    pprint.pprint(model._match_results(matched_categories))
    print()

    ground_truth_path = "evaluation/model_metadata.json"
    with open(ground_truth_path, "r") as f:
        ground_truth = json.load(f)
    pprint.pprint(ground_truth.get(str(model_id), {}))