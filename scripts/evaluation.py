'''
evaluate gpt generated metadata types
'''
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

if __name__ == "__main__":
    # case I: normal predictions
    y_pred = ['I Calcium', 'I h', 'I_CAP', 'I_CLAMP']
    y_true = ['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG']
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()

    # case II: ground truth is empty
    y_pred = ['I Ca', 'I h', 'I_CAB', 'I_CAP', 'I_CLAMP']
    y_true = None
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()

    # case III: prediction is empty
    y_pred = []
    y_true = ['I L high threshold', 'I h', 'I K,Ca', 'I Calcium', 'I_HERG']
    eval_result = Evaluate(y_pred, y_true).result()
    print(eval_result)
    print()
