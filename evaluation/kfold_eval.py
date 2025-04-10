import argparse
import json
from sklearn.metrics import precision_score, recall_score, f1_score, jaccard_score, hamming_loss
from sklearn.preprocessing import MultiLabelBinarizer
from prepare import _api_request
from pprint import pprint
from collections import defaultdict
import numpy as np
from itertools import combinations
import pandas as pd

API_HEAD = "/api/v1/"
TOPIC_NAMES_DICT = {
    'neurons': 'celltypes',
    'model_concept': 'modelconcepts',
    'receptors': 'receptors',
    "currents": "currents",
    "model_type":"modeltypes",
    "modeling_application":"simenvironments",
    "region":"regions"

}


def jaccard_similarity(sets):
    """ Compute average Jaccard similarity for all pairwise sets """
    if len(sets) < 2:
        return 1  
    
    pairwise_similarities = []
    for s1, s2 in combinations(sets, 2):  
        intersection = len(s1 & s2)
        union = len(s1 | s2)
        pairwise_similarities.append(intersection / union if union > 0 else 1)

    return sum(pairwise_similarities) / len(pairwise_similarities)

def dice_similarity(sets):
    """ Compute average Dice coefficient for all pairwise sets """
    if len(sets) < 2:
        return 1  

    pairwise_similarities = []
    for s1, s2 in combinations(sets, 2):
        intersection = len(s1 & s2)
        total_size = len(s1) + len(s2)
        pairwise_similarities.append((2 * intersection) / total_size if total_size > 0 else 1)

    return sum(pairwise_similarities) / len(pairwise_similarities)

def process_result(id_list, metadata, output, type, test_types):
    """ Extract true labels and predicted labels for each test_type """
    code_data = defaultdict(lambda: defaultdict(list))  # Store predictions for consistency calculation
    y_true_list = defaultdict(list)  # Store true labels for each test_type
    y_pred_list = defaultdict(list)  # Store predicted labels for each test_type

    for code_id in id_list:
        if code_id in metadata.keys():
            for test_type in test_types:
                if test_type in output[str(code_id)]:
                    # Extract predictions from output.json
                    y_pred_raw = output[str(code_id)][test_type]
                    
                    # Handle 'none' case properly
                    if y_pred_raw.lower() in ["'none'","none"]:
                        y_pred = ["none"]
                    else:
                        # Extract terms correctly, handling single quotes and spaces
                        y_pred = [term.strip(" '\"") for term in y_pred_raw.split("', '")]

                    # Extract the true labels from metadata.json
                    if code_id in metadata and type in metadata[code_id]:
                        metadata_value = metadata[code_id][type]
                        
                        # Handle None or empty list cases
                        if metadata_value is None or (isinstance(metadata_value, list) and len(metadata_value) == 0):
                            y_true = ["none"]
                        else:
                            y_true = list(metadata_value)
                    else:
                        y_true = []  # No metadata available for this test_type

                    # Store processed values
                    prefix = ''.join(filter(str.isalpha, test_type))  # Extract prefix (e.g., "header")
                    code_data[code_id][prefix].append(set(y_pred))  # Store for consistency calculation

                    # Store true and predicted labels for classification metrics
                    y_true_list[test_type].append(y_true)
                    y_pred_list[test_type].append(y_pred)

    return code_data, y_true_list, y_pred_list

def result_packed(y_true, y_pred, mlb):
    """ Compute precision, recall, F1, Jaccard similarity, and Hamming loss """
    y_true, y_pred = zip(*[(i, j) for i, j in zip(y_true, y_pred) if i is not None and j is not None])
    y_true_bin = mlb.transform(y_true)
    y_pred_bin = mlb.transform(y_pred)

    precision = precision_score(y_true_bin, y_pred_bin, average='micro')
    recall = recall_score(y_true_bin, y_pred_bin, average='micro')
    f1 = f1_score(y_true_bin, y_pred_bin, average='micro')
    jaccard = jaccard_score(y_true_bin, y_pred_bin, average='samples', zero_division=0)
    hamming = hamming_loss(y_true_bin, y_pred_bin)

    return {
        'precision_micro': precision,
        'recall_micro': recall,
        'f1_micro': f1,
        'jaccard': jaccard,
        'hamming': hamming
    }

def run(metadata_file_path, test_file_path, topic_name, test_types):
    """ Run evaluation and compute classification metrics and consistency per code_id """
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    with open(test_file_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)

    id_list = list(output.keys())

    # Process results: Get grouped predictions per code_id and per test_type
    code_data, y_true_dict, y_pred_dict = process_result(id_list, metadata, output, topic_name, test_types)
    results = defaultdict(list)  # Store classification metrics for each test_type
    consistency_scores = defaultdict(list)  # Store consistency per prefix

    # Fit MultiLabelBinarizer with all possible labels
    metadata_list_url = API_HEAD + TOPIC_NAMES_DICT[topic_name] + '/name'
    metadata_list = _api_request(metadata_list_url)
    # all_labels = set(metadata_list)
    # for y_true_list in y_true_dict.values():
    #     for y_true in y_true_list:
    #         all_labels.update(y_true)  
    # for y_pred_list in y_pred_dict.values():
    #     for y_pred in y_pred_list:
    #         all_labels.update(y_pred)  

    # mlb = MultiLabelBinarizer()
    # mlb.fit([list(all_labels)]) 
    mlb = MultiLabelBinarizer()
    mlb.fit([metadata_list])

    # Compute classification metrics per test_type (first method)
    per_test_type_results = defaultdict(list)

    for test_type, y_true_list in y_true_dict.items():
        if y_true_list:
            y_pred_list = y_pred_dict[test_type]
            metrics = result_packed(y_true_list, y_pred_list, mlb)
            prefix = ''.join(filter(str.isalpha, test_type))  # Extract prefix
            per_test_type_results[prefix].append(metrics)  # Store results per test_type
    #print(per_test_type_results)
    # Compute per-prefix averaged classification metrics
    averaged_results = {}
    for prefix, metrics_list in per_test_type_results.items():
        averaged_metrics = {key: np.mean([m[key] for m in metrics_list]) for key in metrics_list[0]}
        averaged_results[prefix] = averaged_metrics

    # Compute consistency per code_id (second method)
    for code_id, prefix_dict in code_data.items():
        for prefix, sets in prefix_dict.items():
            if len(sets) > 1:  # Only compute if multiple test_types exist
                jaccard = jaccard_similarity(sets)
                dice = dice_similarity(sets)
                consistency_scores[prefix].append((jaccard, dice))

    # Compute average consistency across all code_id
    for prefix, scores in consistency_scores.items():
        jaccard_avg = np.mean([s[0] for s in scores]) if scores else 1
        dice_avg = np.mean([s[1] for s in scores]) if scores else 1
        averaged_results[prefix]['jaccard_consistency'] = jaccard_avg
        averaged_results[prefix]['dice_consistency'] = dice_avg

    return averaged_results, consistency_scores

def main():
    # """ Main function to parse arguments and run the evaluation """
    # parser = argparse.ArgumentParser(description="Evaluate predictions against metadata.")
    # parser.add_argument('test_file', type=str, help="The name of the test file located in the 'results' directory.")
    # parser.add_argument('metadata_type', type=str, choices=TOPIC_NAMES_DICT.keys(), help="The type of metadata to evaluate against.")
    # parser.add_argument('test_types', nargs='+', type=str, help="The test types to evaluate.")
    # args = parser.parse_args()

    # metadata_file_path = 'evaluation/model_metadata.json'
    # test_file_path = f'{args.test_file}'

    # print(f"Evaluating {args.metadata_type} predictions with test types {args.test_types}...")
    # result, consistency_scores = run(metadata_file_path, test_file_path, args.metadata_type, args.test_types)
    # pprint(result)
    # #pprint(consistency_scores)
    parser = argparse.ArgumentParser(description="Evaluate predictions for multiple metadata types.")
    parser.add_argument('metadata_types', nargs='+', type=str, choices=TOPIC_NAMES_DICT.keys(),
                        help="List of metadata types to evaluate, e.g. neurons currents")
    parser.add_argument('--test_files', nargs='+', required=True,
                        help="List of test files (prediction results), one per metadata type.")
    parser.add_argument('--test_types', nargs='+', required=True,
                        help="Test types (e.g. com_var1 com_var2 header1 header2)")
    args = parser.parse_args()

    if len(args.metadata_types) != len(args.test_files):
        raise ValueError("The number of metadata_types must match the number of test_files.")

    metadata_file_path = 'evaluation/model_metadata.json'

    comvar_dict = {}
    header_dict = {}

    for metadata_type, test_file in zip(args.metadata_types, args.test_files):
        print(f"\n--- Evaluating {metadata_type} ---")
        result, _ = run(metadata_file_path, test_file, metadata_type, args.test_types)
        pprint(result)

        if 'comvar' in result:
            comvar_dict[metadata_type] = result['comvar']
        if 'header' in result:
            header_dict[metadata_type] = result['header']

    if comvar_dict:
        df_comvar = pd.DataFrame(comvar_dict)
        df_comvar.index.name = 'metric'
        df_comvar.to_csv("evaluation/results/comvar_metrics.csv")
        print("Saved comvar_metrics.csv")

    if header_dict:
        df_header = pd.DataFrame(header_dict)
        df_header.index.name = 'metric'
        df_header.to_csv("evaluation/results/header_metrics.csv")
        print("Saved header_metrics.csv")

if __name__ == "__main__":
    main()


#python evaluation/kfold_eval.py evaluation/results/neurons_result.json neurons com_var1 com_var2 com_var3  header1 header2 header3
# python evaluation/kfold_eval.py \
#   neurons currents model_type model_concept modeling_application receptors region\
#   --test_files \
#     evaluation/results/neurons_result.json \
#     evaluation/results/currents_result.json \
#     evaluation/results/model_type_result.json \
#     evaluation/results/model_concept_result.json \
#     evaluation/results/modeling_application_result.json \
#     evaluation/results/receptors_result.json \
#     evaluation/results/region_result.json \
#   --test_types com_var1 com_var2 com_var3  header1 header2 header3