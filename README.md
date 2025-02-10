# CodeAnalysis - Automated Metadata Assignment for Neuroscience Models with LLM

## 1 Introduction
The analysis of neuroscience model code presents unique challenges due to the complexity and variability inherent in computational neuroscience models. These models, often coupled with detailed metadata describing neurons, currents, and biological systems, are critical for advancing our understanding of brain function and disease. Recent advancements in large language models (LLMs), such as ChatGPT, provide new opportunities for automating metadata assignment from neuroscience code files. By leveraging LLMs, researchers can streamline the labor-intensive process of extracting and classifying metadata while addressing the inherent ambiguity and randomness in automated systems. This project explores the use of LLMs in this domain, aiming to improve the accuracy and reliability of metadata classification while reducing manual effort.

The scope of this project involves developing a strategy for selecting files from neuroscience model code for analysis and designing a mapping for metadata types likely to be predicted. Our initial focus is on testing LLMs for metadata assignment using a small, controlled set of tags, allowing for a detailed comparison with traditional rule-based approaches. This includes reviewing and implementing strategies to handle term ambiguity and randomness, both of which pose significant challenges to automated systems. By addressing these issues in the early stages, the project sets a solid foundation for systematic evaluation and broader application in the subsequent phases. This work not only contributes to the field of computational neuroscience but also provides insights into the broader applicability of LLMs in scientific data analysis.

## 2 Methods

### 2.1 Tools
In our capstone project, we utilized several key tools to explore the ability of large language models (LLMs), such as ChatGPT, to extract metadata from neuroscience-related code files. **ModelDB** served as our primary data source, providing a repository of computational neuroscience models coupled with neuron property archives. This platform allowed us to access a diverse set of neuroscience code files and metadata for analysis. To streamline dataset acquisition, we implemented **Azure authentication** for secure and automated access to shared files hosted on Google Drive, ensuring seamless integration with Python scripts. Additionally, we utilized **Python’s GPT API** for interaction with ChatGPT, enabling the extraction and analysis of metadata. The API facilitated the input of code samples and retrieval of model-predicted metadata, forming the backbone of our experimental pipeline. Together, these tools established a robust framework for evaluating LLMs' metadata extraction capabilities within the context of neuroscience research.

### 2.2 Evaluation
The evaluation module employs precision and recall metrics, including both micro and macro averages. In this context, a true positive (TP) is defined as a predictive value that matches the ground truth label.

$$
\mathrm{Precision}_\mathrm{Micro} = \frac{\mathrm{TP}_1 + \mathrm{TP}_2 + \cdots + \mathrm{TP}_N}{\mathrm{TP}_1 + \mathrm{FP}_1 + \mathrm{TP}_2 + \mathrm{FP}_2 + \cdots + \mathrm{TP}_N}
$$

$$
\mathrm{Recall}_\mathrm{Micro} = \frac{\mathrm{TP}_1 + \mathrm{TP}_2 + \cdots + \mathrm{TP}_N}{\mathrm{TP}_1 + \mathrm{FN}_1 + \mathrm{TP}_2 + \mathrm{FN}_2 + \cdots + \mathrm{TP}_N}
$$

$$
\mathrm{Precision}_\mathrm{Macro} = \frac{\mathrm{Precision}_1 + \mathrm{Precision}_2 + \cdots + \mathrm{Precision}_N}{N}
$$

$$
\mathrm{Recall}_\mathrm{Macro} = \frac{\mathrm{Recall}_1 + \mathrm{Recall}_2 + \cdots + \mathrm{Recall}_N}{N}
$$

## 3 Progress

### 3.1 Pipeline
The pipeline for our project consists of the following steps:

1. **Model Access**:  
   We accessed the ModelDB models using Azure. All model IDs were shuffled, and we selected the first five models for experimentation.

2. **File Screening for Relevant Models**:  
   To identify the most relevant models and ensure compatibility with GPT, we performed file screening:  
   - For each model, we selected only files with specific extensions, including `.py`, `.cpp`, `.java`, `.m`, `.txt`, `.h`, `.data`, `.html`, `.c`, `.mod`, `.g`, `.p`, and `.ode`.  
   - After filtering by file type, we applied rule-based selection using ModelDB-provided rules. Each file was assessed based on the number of matching rules, and we selected the top 50% of files that matched the most rules to identify the most relevant ones.  
   - Finally, all selected files were combined into a single file.

3. **GPT Processing and Metadata Extraction**:  
   - The combined file was input into GPT along with a prompt designed to extract relevant metadata.  
   - The prompt included an instructional section, such as:  
     *"Based on this content, please provide the most relevant ion current(s). Just list them separated by commas; DO NOT analyze."*  
   - Additionally, the prompt included a selection list covering various metadata types like `cell types`, `currents`, `genes`, `model concepts`, and others.  
   - GPT's output was then used for further evaluation.


### 3.2 Pilot Experiment
Our pivot experiment workflow begins by loading data from Google Drive to a local environment using automated scripts integrated with Azure authentication. Once the data is accessible, we perform a file screening process based on our designed methodology to filter relevant files for analysis. The specific screening criteria and methods are detailed in subsequent sections. Types of metadata listed in modelDB is as follows: `['celltypes', 'currents', 'genes', 'modelconcepts', 'models', 'modeltypes', 'papers', 'receptors', 'regions', 'simenvironments', 'transmitters']`. For the experiment, we focused on extracting currents as the metadata type of interest, leveraging Python’s GPT API for metadata prediction. This metadata was chosen for its significance in neuroscience and its frequent occurrence in the dataset. The predicted metadata was then evaluated against the ground truth annotations manually curated in ModelDB. This evaluation process allows us to measure the accuracy and reliability of the LLM's predictions, providing insights into its performance for metadata extraction in computational neuroscience. This workflow represents a systematic approach to assessing the capabilities of LLMs in handling domain-specific tasks.

## 4 Conclusion and Next Steps
We have designed and implemented a pipeline for experiments, including modules for data processing, metadata generation and evaluation. While we have conducted only a baseline experiment on a small dataset, our pipeline is structured to support a diverse range of experiments efficiently by simply adjusting the input data and parameters. We acknowledge that our project currently have some limitations, which we anticipate will be carried forward in the next semester.

### 4.1 Improve Experiment Design
Currently, our experiments are limited to a single metadata type: currents. We acknowledge that current-related information in model files is primarily located within ".mod" files. As a result, experiments focused solely on generating "currents" metadata may not infer the effectiveness of our data preprocessing and file screening processes. To address this, our next steps will extend experiments to include other metadata types, such as "modelconcepts," which are interpretable and retrievable.

### 4.2 Balance Randomness and Performance
LLMs generate text by calculating token probabilities, making the generation process inherently stochastic. As a result, running our experiments multiple times can yield different metadata outputs for each model, leading to performance variations. Therefore, we need to address two issues: (1) evaluating the degree of randomness in the results, (2) establishing a method to identify and select the preferred outcomes among multiple rounds of results.

### 4.3 New Scenario
Our current pipeline is designed for the following senario: Suppose a researcher is given a folder with all the code files for a compuational neuroscience model, our pipeline will help (1) select the most informative files from the folder and (2) use LLM to generate metadata for the code files. This approach allows us to evaluate the LLM's ability to extract metadata information based on a curated list of choices. 

A potential new scenario involves a person searching for a model related to a specific neuroscience topic (e.g., Parkinson's disease). In this case, the LLM would first determine whether the model pertains to the topic and then generate the metadata. We hypothesize that the LLM produces more accurate metadata when it has a better understanding of the context, as different types of metadata are inherently interconnected.

To test this hypothesis, we propose gathering all models related to Parkinson's disease (True group) and randomly selecting unrelated models (False group). The initial evaluation will focus on the LLM's ability to correctly classify models into these groups. If the accuracy is high, we will further refine our approach by employing the Chain-of-Thought strategy: prompting the LLM with a binary classification question first, followed by metadata extraction.

## Setup
Make sure the work directory is root directory, run:
```
pip install -e .
```