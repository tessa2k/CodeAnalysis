import argparse
import json
from sklearn.metrics import precision_score, recall_score, f1_score, jaccard_score, hamming_loss
from sklearn.preprocessing import MultiLabelBinarizer
from prepare import _api_request
from pprint import pprint
from collections import defaultdict
import numpy as np

API_HEAD = "/api/v1/"
TOPIC_NAMES_DICT = {
    'neurons': 'celltypes',
    'model_concept': 'modelconcepts'
}

def jaccard_similarity(sets):
    """ Compute Jaccard similarity for multiple sets """
    intersection = set.intersection(*sets) if sets else set()
    union = set.union(*sets) if sets else set()
    return len(intersection) / len(union) if len(union) > 0 else 1

def dice_similarity(sets):
    """ Compute Dice coefficient for multiple sets """
    intersection = set.intersection(*sets) if sets else set()
    total_size = sum(len(s) for s in sets)
    return (2 * len(intersection)) / total_size if total_size > 0 else 1

def process_result(id_list, metadata, output, type, test_types):
    """ Extract true labels and predicted labels for each test_type """
    code_data = defaultdict(lambda: defaultdict(list))  # Store predictions for consistency calculation
    y_true_list = defaultdict(list)  # Store true labels for each test_type
    y_pred_list = defaultdict(list)  # Store predicted labels for each test_type

    for code_id in id_list:
        if code_id in metadata.keys():
            for test_type in test_types:
                if test_type in output[str(code_id)]:
                    y_pred = output[str(code_id)][test_type].split(',')
                    y_pred = [i.strip() for i in y_pred]

                    prefix = ''.join(filter(str.isalpha, test_type))  # Extract prefix (e.g., com_var)
                    code_data[code_id][prefix].append(set(y_pred))  # Store for consistency calculation

                    # Store true and predicted labels for classification metrics
                    y_true_list[test_type].append(metadata[str(code_id)][type])
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
    jaccard = jaccard_score(y_true_bin, y_pred_bin, average='samples')
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
    """ Main function to parse arguments and run the evaluation """
    parser = argparse.ArgumentParser(description="Evaluate predictions against metadata.")
    parser.add_argument('test_file', type=str, help="The name of the test file located in the 'results' directory.")
    parser.add_argument('metadata_type', type=str, choices=TOPIC_NAMES_DICT.keys(), help="The type of metadata to evaluate against.")
    parser.add_argument('test_types', nargs='+', type=str, help="The test types to evaluate.")
    args = parser.parse_args()

    metadata_file_path = 'evaluation/model_metadata.json'
    test_file_path = f'{args.test_file}'

    print(f"Evaluating {args.metadata_type} predictions with test types {args.test_types}...")
    result, consistency_scores = run(metadata_file_path, test_file_path, args.metadata_type, args.test_types)
    pprint(result)
    pprint(consistency_scores)

if __name__ == "__main__":
    main()


#python evaluation/kfold_eval.py evaluation/results/celltype_result.json neurons com_var1 com_var2 com_var3  header1 header2 header3