'''
Use self-defined precision/recall to evaluate gpt generated metadata types
'''
import json
from pprint import pprint
import evaluation as eval
import sys
from utils import process_result


def run(metadata_file_path, test_file_path, topic_name, output_dir=None):
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    with open(test_file_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)
    
    result_dict = {}
    # print("Filtered results")
    y_true, y_pred = process_result(list(output.keys()), metadata, output, topic_name, group_name="filter")
    # print(y_true, y_pred)
    result = eval.Evaluate(y_true, y_pred).result()
    
    result_dict["filter"] = {'precision_macro': result['precision_macro'],
                             'precision_micro': result['precision_micro'],
                             'recall_macro': result['recall_macro'],
                             'recall_micro': result['recall_micro']}

    # print("Unfiltered results")
    y_true, y_pred = process_result(list(output.keys()), metadata, output, topic_name, group_name="unfilter")
    # print(y_true, y_pred)
    result = eval.Evaluate(y_true, y_pred).result()

    result_dict["unfilter"] = {'precision_macro': result['precision_macro'],
                             'precision_micro': result['precision_micro'],
                             'recall_macro': result['recall_macro'],
                             'recall_micro': result['recall_micro']}
    return result_dict

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <test_file> <metadata_type>")
        sys.exit(1)

    # ground truth
    metadata_file_path = 'model_metadata.json'

    test_file = sys.argv[1]
    test_file_path = 'results/' + test_file

    metadata_type = sys.argv[2]

    print(f"Evaluate {metadata_type} predictions...")
    result = run(metadata_file_path, test_file_path, metadata_type)
    pprint(result)


if __name__ == "__main__":
    # ground truth
    # metadata_file_path = 'model_metadata.json'

    # # modelconcepts
    # print("Evaluate modelconcepts predictions...")
    # test_file_path = 'results/modelconcepts_filter_test_1.json'
    # result = run(metadata_file_path, test_file_path, "model_concept")
    # pprint(result)
    # print()

    # # celltypes
    # print("Evaluate celltypes predictions...")
    # test_file_path = 'results/celltype_filter_test_1.json'
    # result = run(metadata_file_path, test_file_path, "neurons") 
    # pprint(result)

    main()
    # command examples
    # python run.py modelconcepts_filter_test_1.json model_concept


