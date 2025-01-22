'''
evaluate gpt generated metadata types
'''
import json
from pprint import pprint
import evaluation as eval




# celltype
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


if __name__ == "__main__":
    # ground truth
    metadata_file_path = 'model_metadata.json'

    # modelconcepts
    print("Evaluate modelconcepts predictions...")
    test_file_path = 'results/modelconcepts_filter_test_1.json'
    result = run(metadata_file_path, test_file_path, "model_concept")
    pprint(result)
    print()

    # celltypes
    print("Evaluate celltypes predictions...")
    test_file_path = 'results/celltype_filter_test_1.json'
    result = run(metadata_file_path, test_file_path, "neurons") 
    pprint(result)


