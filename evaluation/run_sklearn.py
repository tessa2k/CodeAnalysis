'''
Use metrics defined in sklearn
'''

from sklearn.metrics import precision_score, recall_score, f1_score, jaccard_score, hamming_loss
from sklearn.preprocessing import MultiLabelBinarizer
import sys
from pprint import pprint
import json

# self-defined
from utils import api_request, process_result


API_HEAD = "/api/v1/"
TOPIC_NAMES_DICT = {
    'neurons': 'celltypes',
    'model_concept': 'modelconcepts'
}


def result_packed(y_true, y_pred, mlb):
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

def run(metadata_file_path, test_file_path, topic_name, output_dir=None):
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    with open(test_file_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)
    
    metadata_list_url = API_HEAD + TOPIC_NAMES_DICT[topic_name] + '/name'
    metadata_list = api_request(metadata_list_url)
    mlb = MultiLabelBinarizer()
    mlb.fit([metadata_list])
    
    result_dict = {}
    # print("Filtered results")
    y_true, y_pred = process_result(list(output.keys()), metadata, output, topic_name, group_name="filter")
    result_dict['filter'] = result_packed(y_true, y_pred, mlb)

    # print("Unfiltered results")
    y_true, y_pred = process_result(list(output.keys()), metadata, output, topic_name, group_name="unfilter")
    result_dict['unfilter'] = result_packed(y_true, y_pred, mlb)

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
    # Example ground truth and predictions
    # y_true = [{"tag1", "tag2", "tag3"}, {"tag4", "tag5"}]
    # y_pred = [{"tag1", "tag3"}, {"tag4", "tag6"}] # it ignores tag6 because it doesn't appear in ground truth

    # # Convert to binary indicator format if needed for sklearn metrics
    # from sklearn.preprocessing import MultiLabelBinarizer

    # mlb = MultiLabelBinarizer()
    # y_true_bin = mlb.fit_transform(y_true)
    # y_pred_bin = mlb.transform(y_pred)

    # precision = precision_score(y_true_bin, y_pred_bin, average='micro')
    # recall = recall_score(y_true_bin, y_pred_bin, average='micro')
    # f1 = f1_score(y_true_bin, y_pred_bin, average='micro')
    # jaccard = jaccard_score(y_true_bin, y_pred_bin, average='samples')
    # hamming = hamming_loss(y_true_bin, y_pred_bin)

    # print(f"Precision: {precision}, Recall: {recall}, F1-score: {f1}, Jaccard: {jaccard}, Hamming Loss: {hamming}")
    main()
