'''
evaluate gpt generated metadata types
'''
import json
from pprint import pprint

class Evaluate:
    def __init__(self, y_true, y_pred):
        """
        Parameters:
        - y_true (list): Ground truth (correct) labels.
        - y_pred (list): Generated metadata types.

        Examples:
        - y_true = ['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG']
        - y_pred = ['I Ca', 'I h', 'I_CAB', 'I_CAP', 'I_CLAMP'].
        """
        self.y_true = y_true if y_true is not None else []
        self.y_pred = y_pred if y_pred is not None else []

    def precision(self):
        """
        Precision: TP / (TP + FP)
        
        Returns:
        - Precision (float): The precision score.
        """
        if not self.y_pred:
            print("Warning: No predictions provided.")
            return None
        true_positives = len(set(self.y_pred).intersection(set(self.y_true)))
        return true_positives / len(self.y_pred)

    def recall(self):
        """
        Recall: TP / (TP + FN)
        
        Returns:
        - Recall (float): The recall score.
        """
        if not self.y_true:
            print("Warning: Ground truth is empty; recall is undefined.")
            return None

        true_positives = len(set(self.y_pred).intersection(set(self.y_true)))
        return true_positives / len(self.y_true)

    def result(self):
        """     
        Returns:
        - dict: Dictionary with precision and recall.
        """
        return {
            "precision": self.precision(),
            "recall": self.recall()
        }
    

def test_examples():
    # case I: normal predictions
    y_pred = ['I Calcium', 'I h', 'I_CAP', 'I_CLAMP']
    y_true = ['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG']
    print(f"Predict - {y_pred}; \nTrue - {y_true}")
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()

    # case II: ground truth is empty
    y_pred = ['I Ca', 'I h', 'I_CAB', 'I_CAP', 'I_CLAMP']
    y_true = None
    print(f"Predict - {y_pred}; \nTrue - {y_true}")
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()

    # case III: prediction is empty
    y_pred = []
    y_true = ['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG']
    print(f"Predict - {y_pred};\nTrue - {y_true}")
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()

if __name__ == "__main__":
    # test_examples()
    sample_list = [114665, 118434, 114424, 105383, 113949]
    metadata_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/model_metadata.json'
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    test_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/prompt_test.json'
    with open(test_file_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)
    
    most_relevant, potentially_relevant = output[0]["results"], output[1]["results"]
    result_1, result_2 = {}, {}
    for i, num in enumerate(sample_list):
        if num == 118434: continue
        y_true = metadata[str(num)]["currents"]

        y_pred = most_relevant[i]["metadata"].split(',')
        y_pred = [i.strip() for i in y_pred]
        result_1[num] = Evaluate(y_pred, y_true).result()
        result_1[num]["True"] = y_true
        result_1[num]["Predict"] = y_pred

        y_pred = potentially_relevant[i]["metadata"].split(',')
        y_pred = [i.strip() for i in y_pred]
        result_2[num] = Evaluate(y_pred, y_true).result()
        result_2[num]["True"] = y_true
        result_2[num]["Predict"] = y_pred

    print("Most relevant:")
    pprint(result_1)
    print()
    print("Potentially relevant:")
    pprint(result_2)

    output_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/sample_performance.json'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump({
            "Most Relevant": result_1,
            "Potentially Relevant": result_2
        }, output_file, indent=4)

    
    