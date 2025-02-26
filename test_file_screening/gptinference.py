import os
import json
import argparse
import requests
from openai import OpenAI
from tqdm import tqdm  
from dotenv import load_dotenv

load_dotenv()  

VALID_CATEGORIES = ['celltypes', 'currents', 'genes', 'modelconcepts', 'models', 'modeltypes', 'papers', 'receptors', 'regions', 'simenvironments', 'transmitters']

CATEGORY_NAME_MAPPING = {
    'celltypes': 'cell types',
    'currents': 'currents',
    'genes': 'genes',
    'modelconcepts': 'model concepts',
    'models': 'models',
    'modeltypes': 'model types',
    'papers': 'papers',
    'receptors': 'receptors',
    'regions': 'regions',
    'simenvironments': 'simulation environments',
    'transmitters': 'transmitters'
}

def api_request(url, method='GET', headers=None, params=None, json_data=None):
    '''
    Parameters:
      - url (str): The API endpoint.
      - method (str): The HTTP method ('GET', 'POST', etc.). Default is 'GET'.
      - headers (dict): Optional headers for the request.
      - params (dict): Optional URL parameters for the request.
      - json_data (dict): Optional JSON data for POST requests.

      Returns:
      - response (dict): Parsed JSON response from the API.
    '''
    base_url = "https://modeldb.science"
    full_url = f"{base_url}{url}"
    try:
        if method.upper() == 'GET':
            response = requests.get(full_url, headers=headers, params=params)
        elif method.upper() == 'POST':
            response = requests.post(full_url, headers=headers, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
    return None

def get_category_list(category):
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category '{category}'. Must be one of {VALID_CATEGORIES}")
    
    cat_url = f"/api/v1/{category}/name"
    metadata_list = api_request(cat_url, method='GET')
    return metadata_list if metadata_list else []

def process_file(file_folder, exact_file, client, category, result_key_prefix):
    full_path = os.path.join(file_folder, exact_file)
    with open(full_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        file_content = file_content[:5000] 

    category_list = get_category_list(category)
    category_items = ', '.join(category_list) if category_list else "No items available"

    mapped_category_name = CATEGORY_NAME_MAPPING.get(category, category)

    # prompt = (
    #    f"""You are an expert in computational neursocience, reviewing model repositories. This database includes computational models written in any programming language for any tool, but they all must have a mechanistic component for getting insight into the function individual neurons, networks of neurons, or of the nervous system in health or disease.
    
    # We will give you contents in the model repositories, and you will identify any highly relavent {mapped_category_name} in a list of choice. If a concept is mentioned but not very significant, please do not mention it in the answer. Just list them separated by commas, DO NOT analyze. Example: item1, item2, ...
    # Choice: {category_items}
    # Content: {file_content}
    # """
    # )
    prompt = (
    f"You are a neuroscience expert specializing in {mapped_category_name} analysis. "
    f"Given the following content:\n\n{file_content}\n\n"
    f"Please identify the most relevant {mapped_category_name} from the following list: {category_items}. "
    f"Just list them separated by commas, DO NOT analyze. "
    f"If none are relevant, respond with 'none'. "
    f"Example: item1, item2, ..."
    )

    chat_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    response_dict = chat_completion.to_dict()
    metadata = response_dict["choices"][0]["message"]["content"].strip()
    return metadata

def main(input_folder, output_file, n, category, result_key_prefix):
    api_key = os.getenv('API_KEY')
    organization = os.getenv('ORGANIZATION')
    if not api_key:
        raise ValueError("API_KEY is not set. Please check your .env file.")
    
    client = OpenAI(api_key=api_key, organization=organization)

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as json_file:
            results = json.load(json_file)
    else:
        results = {}

    filter_files = {entry: entry.split('_')[0] for entry in os.listdir(input_folder)}

    for filter_file, code in tqdm(filter_files.items(), desc="Processing Files", unit="file"):
        if code not in results:
            results[code] = {}
        
        for i in range(1, n + 1):
            result_key = f'{result_key_prefix}{i}'
            results[code][result_key] = process_file(input_folder, filter_file, client, category, result_key_prefix)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process neuroscience files and extract relevant information.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder containing files.")
    parser.add_argument("output_file", type=str, help="Path to save the output JSON file.")
    parser.add_argument("n", type=int, help="Number of times to process each file.")
    parser.add_argument("category", type=str, choices=VALID_CATEGORIES, help="Category to analyze.")
    parser.add_argument("result_key_prefix", type=str, help="Prefix for result keys in the output JSON.")
    
    args = parser.parse_args()
    main(args.input_folder, args.output_file, args.n, args.category, args.result_key_prefix)
#python ./test_file_screening/gptinference.py ./data/extracted_data ./evaluation/results/celltype_result.json 3 celltypes com_var
#python ./test_file_screening/gptinference.py ./data/concat_header ./evaluation/results/celltype_result.json 3 celltypes header
#python ./test_file_screening/gptinference.py ./data/extracted_data ./evaluation/results/receptors_result.json 3 receptors com_var
#python ./test_file_screening/gptinference.py ./data/concat_header ./evaluation/results/receptors_result.json 3 receptors header