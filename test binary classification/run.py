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

# openAI API
import os
from openai import OpenAI
from dotenv import load_dotenv


def run(para):
    results = {}
    client = OpenAI(api_key=para["api_key"], organization=para["organization"])
    topic = para["topic"] 
    for entry in os.listdir(para["directory"]):
        full_path = os.path.join(para["directory"], entry)
        code = entry.split('_')[0]
        with open(full_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            file_content = file_content[:5000]
        prompt = (
            f"You are a neuroscience expert specializing in ion channel and current analysis. "
            f"Given the following content:\n\n{file_content}\n\n"
            f"Please identify whether this content contains relevant information about {topic}. "
            f"If the answer is yes, please answer Y; otherwise, answer N. DO NOT analyze."
        )
        chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        )

        response_dict = chat_completion.to_dict()
        print(code)
        print(response_dict)
        break

if __name__ == "__main__":
    para = {
        "api_key": os.getenv('API_KEY'),
        "organization": os.getenv('ORGANIZATION'),
        "topic": "Parkinson's",
        "directory": "../sampleParkinsons/match_file" 
    } 
    run(para)