import json
import argparse
import os

def process_metadata(result_files, metadata_file, output_file):
    new_metadata = {}

    # Load metadata.json
    with open(metadata_file, "r") as f:
        metadata_data = json.load(f)

    # Process each result file separately
    for result_file in result_files:
        # Extract key_to_extract (e.g., "neurons" from "neurons_result.json")
        key_to_extract = os.path.basename(result_file).split("_result")[0]

        # Load result.json file
        with open(result_file, "r") as f:
            result_data = json.load(f)
        # Process each code_id separately
        for code_id, result_entry in result_data.items():
            # Ensure code_id exists in new_metadata
            if code_id not in new_metadata:
                new_metadata[code_id] = {}

            matched_metadata = {}

            # Debug: Check if code_id is missing in metadata.json
            if code_id not in metadata_data:
                print(f"DEBUG: code_id {code_id} not in metadata_data")

            # Debug: Check if key_to_extract is missing for this code_id
            if code_id in metadata_data and key_to_extract not in metadata_data[code_id]:
                print(f"DEBUG: key_to_extract {key_to_extract} not in metadata_data[{code_id}]")

            # Extract relevant metadata values for this code_id and key_to_extract
            if code_id in metadata_data and key_to_extract in metadata_data[code_id]:
                metadata_value = metadata_data[code_id][key_to_extract]
                if metadata_value is None or (isinstance(metadata_value, list) and len(metadata_value) == 0):
                    metadata_values = {"none"}  # If it's None or an empty list, set metadata_value to {"none"}
                else:
                    metadata_values = set(metadata_value)
            else:
                metadata_values = set()  # If key is missing, use an empty set

            # Process each term in result.json and determine if it matches
            for key, value in result_entry.items():
                if value.lower() == "'none'":
                    matched_metadata["none"] = 2 if "none" in metadata_values else -1
                else:
                    terms = value.strip("'").split("', '")  
                    for term in terms:
                        matched_metadata[term] = 2 if term in metadata_values else -1

            # Save result under the extracted key (e.g., "neurons", "model_type")
            new_metadata[code_id][key_to_extract] = matched_metadata

    # Save the new JSON file
    with open(output_file, "w") as f:
        json.dump(new_metadata, f, indent=4)

    print(f"New JSON file generated: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match metadata fields for each code_id across multiple result files.")
    parser.add_argument("--result_files", type=str, required=True, nargs="+", help="List of result JSON files")
    parser.add_argument("--metadata_file", type=str, required=True, help="Path to the metadata.json file")
    parser.add_argument("--output_file", type=str, required=True, help="Path to save the new JSON file")

    args = parser.parse_args()

    process_metadata(args.result_files, args.metadata_file, args.output_file)


#python ./test_file_screening/result_process.py --result_file ./evaluation/results/neurons_result.json ./evaluation/results/receptors_result.json --metadata_file ./evaluation/model_metadata.json --output_file ./evaluation/process_result.json 