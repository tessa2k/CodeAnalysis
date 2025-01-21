'''
Binary Classification Test on Parkinson's
'''
import requests
import pprint
import time
from tqdm import tqdm
import json
import pandas as pd
import random
from prepare import api_request, sample_negative

# openAI API
import os
from openai import OpenAI
from dotenv import load_dotenv

# file screening


def run():
    pass

api_key = os.getenv('API_KEY')
organization=os.getenv('ORGANIZATION')

MODEL_IDS = "/api/v1/models"
MODEL_ID_FILTER_HEADER = "/api/v1/models?model_concept="

# the concept name to be classified
CONCEPT_NAME = "Parkinson's"
MODEL_ID_FILTER_URL = MODEL_ID_FILTER_HEADER + CONCEPT_NAME

pos_samples= api_request(MODEL_ID_FILTER_URL)
print(pos_samples)

all_ids = api_request(MODEL_IDS)
neg_samples = sample_negative(all_ids, pos_samples, len(pos_samples), seed=123123)
print(neg_samples)

# ground truth labels
labels = {i: 1 for i in pos_samples}
labels.update({i: 0 for i in neg_samples})