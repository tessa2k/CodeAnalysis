import json
import pandas as pd
import tqdm
from sklearn.preprocessing import MultiLabelBinarizer
from run_sklearn import result_packed, API_HEAD
from utils import api_request

TOPIC_NAMES_DICT = {
        "neurons": "celltypes",
        "currents": "currents",
        "modeling_application": "simenvironments",
        "model_concept": "modelconcepts",
        "model_type": "modeltypes",
        "receptors": "receptors",
        "region": "regions"
    }

def process_result(id_list, metadata, output, topic_name, search_name):
    y_true_list = []
    y_pred_list = []
    for num in id_list:
        if num in metadata.keys():
            y_true = metadata[str(num)][topic_name]
            y_pred = output[str(num)][search_name]
            y_true_list.append(y_true)
            y_pred_list.append(y_pred)
    return y_true_list, y_pred_list

def run(metadata_file_path, rulebased_result_path):
    results = {}
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    with open(rulebased_result_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)

    for topic_name, search_name in tqdm.tqdm(TOPIC_NAMES_DICT.items()):
        # topic_name is to query the ground truth
        # search_name is to query the output and metadata_list
        metadata_list_url = API_HEAD + search_name + '/name'
        metadata_list = api_request(metadata_list_url)
        mlb = MultiLabelBinarizer()
        mlb.fit([metadata_list])

        y_true, y_pred = process_result(list(output.keys()), metadata, output, topic_name, search_name)
        results[search_name] = result_packed(y_true, y_pred, mlb)
    return results

def main():
    # ground truth
    metadata_file_path = 'evaluation/model_metadata.json'

    # rule-based results path
    rulebased_result_path = "rule_based/kgram_results/results_partial.json"

    results = run(metadata_file_path, rulebased_result_path)
    print(results)

    # convert to csv
    df = pd.DataFrame(results)
    df.to_csv("rule_based/rule_based_eval.csv")

if __name__ == "__main__":
    main()
