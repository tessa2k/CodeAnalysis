# Test Binary Classification

New scenario: a person searching for a model related to a specific neuroscience topic (e.g., Parkinson's disease). 

Hypothesis: 
- LLM is able to classifiy whether a coding file/folder is relavant to certain topics/concepts/metadata or not with high accuracies.
- LLM produces more accurate metadata when it has a better understanding of the context, as different types of metadata are inherently interconnected.

TODO: 
- To test this hypothesis, we propose gathering all models related to Parkinson's disease (True group) and randomly selecting unrelated models (False group). 
- The initial evaluation will focus on the LLM's ability to correctly classify models into these groups. 
- If the accuracy is high, we will further refine our approach by employing the Chain-of-Thought strategy: prompting the LLM with a binary classification question first, followed by metadata extraction.