'''
evaluate gpt generated metadata types
'''
import json
from pprint import pprint

class Evaluate:
    def __init__(self, y_true, y_pred):
        """
        Parameters:
        - y_true (list of list): Ground truth (correct) labels.
        - y_pred (list): Generated metadata types.

        Examples:
        - y_true = [['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG'], [], ...]
        - y_pred = [['I Ca', 'I h', 'I_CAB', 'I_CAP', 'I_CLAMP'], [], ...]
        """
        self.y_true = y_true if y_true is not None else []
        self.y_pred = y_pred if y_pred is not None else []
        self.tp_tot = self.true_positive(ret='total')
        self.tp_list = self.true_positive()

    def true_positive(self, ret = None):
        """
        Number of true positive values
        
        Returns:
        - a list of TP for each model, and the total TPs for all models.
        """
        true_positives = 0
        true_positives_list = []
        for pred, true in zip(self.y_pred, self.y_true):
            if (not pred) or (not true):
                true_positives_list.append(0)
            else:
                curr = len(set(pred).intersection(set(true)))
                true_positives += curr
                true_positives_list.append(curr)
        if ret == 'total':
            return true_positives
        else: return true_positives_list
        
    def precision_list(self):
        '''
        Returns: 
        - List of precision score for each model output
        '''
        result = []
        for pp, tp in zip(self.y_pred, self.tp_list):
            if pp and len(pp) != 0:
                result.append(tp/len(pp))
            else:
                result.append(None)
        return result
        
    def precision(self):
        '''
        Macro Precision: TP_total / pred_total
        Micro Precision: average(TP/(TP + FP))
        '''
        pp_tot = sum(len(items) for items in self.y_pred if items)
        ret_macro = self.tp_tot/pp_tot
        precision_results = self.precision_list()
        ret_micro = sum([item for item in precision_results if item])/len(precision_results)
        return {"macro": ret_macro, "micro": ret_micro}


    def recall_list(self):
        """
        Recall: TP / (TP + FN)
        
        Returns:
        - List of recall score for each model output.
        """
        recall_list = []
        for true, tp in zip(self.y_true, self.tp_list):
            if true and len(true) != 0:
                recall_list.append(tp/len(true))
            else:
                recall_list.append(None)
        return recall_list

    def recall(self):
        '''
        Macro Recall: TP_total / true_total
        Micro Recall: average(TP/(TP + FN))
        '''
        true_tot = sum(len(items) for items in self.y_true if items)
        ret_macro = self.tp_tot/true_tot
        recall_results = self.recall_list()
        ret_micro = sum([item for item in recall_results if item])/len(recall_results)
        return {"macro": ret_macro, "micro": ret_micro}
        
    def result(self):
        """     
        Returns:
        - dict: Dictionary with precision and recall.
        """
        prec = self.precision()
        rec = self.recall()
        return {
            "precision_macro": prec["macro"],
            "precision_micro": prec["micro"],
            "precision_list": self.precision_list(),
            "recall_macro": rec["macro"],
            "recall_micro": rec["micro"],
            "recall_list": self.recall_list()
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

def process_result(id_list, metadata, output, type="currents"):
    y_true_list = []
    y_pred_list = []
    for i, num in enumerate(id_list):
        y_true = metadata[str(num)][type]
        y_pred = output[i]["metadata"].split(',')
        y_pred = [i.strip() for i in y_pred]
        y_true_list.append(y_true)
        y_pred_list.append(y_pred)
    
    return y_true_list, y_pred_list




if __name__ == "__main__":
    # test_examples()
    sample_list = [118434, 105383, 114424, 114665, 113949]
    metadata_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/model_metadata.json'
    with open(metadata_file_path, 'r', encoding='utf-8') as json_file:
        metadata = json.load(json_file)
    test_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/prompt_test(2).json'
    with open(test_file_path, 'r', encoding='utf-8') as json_file:
        output = json.load(json_file)
    
    most_relevant = output["results"]

    print("Most relevant:")
    y_true, y_pred = process_result(sample_list, metadata, most_relevant, type="currents")
    print("True: ", y_true)
    print("Predict: ", y_pred)
    result_1 = Evaluate(y_true, y_pred).result()
    pprint(result_1)
    print()

    output_file_path = '/Users/cynthia/Desktop/Capstone-CodeAnalysis/Data/sample_performance_1.json'
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump({
            "y_true": y_true,
            "y_pred": y_pred,
            "Performance": result_1
        }, output_file, indent=4)

    
    