'''
Run rule based method for all models
'''
import os
import json
import argparse
from tqdm import tqdm
from rule_based.rule_based import RuleBased

def process_folders(model: RuleBased, folder_ids, results_dict, errors_dict):
    """
    Process a list of subfolder IDs:
      - For each folder, traverse the files and classify using the rule-based model.
      - Catch any errors and record them.
    
    Args:
        model (RuleBased): An instance of the RuleBased class.
        folder_ids (list): List of folder names (model IDs) to process.
        results_dict (dict): Dictionary to store successful results.
        errors_dict (dict): Dictionary to store error messages (keyed by model id).
    """
    for model_id in tqdm(folder_ids):
        print(f"Processing model id: {model_id}")
        try:
            # Process the folder and get matched categories.
            matched_categories = model._traverse_file(model_id)
            results = model._match_results(matched_categories)
            results_dict[model_id] = results
        except Exception as e:
            errors_dict[model_id] = str(e)
            print(f"Error processing model id {model_id}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Run RuleBased Model on subfolders in batches."
    )
    parser.add_argument(
        "--data_folder", type=str, default="sampleAlzheimer",
        help="Path to the root data folder containing subfolders (each a model id)."
    )
    parser.add_argument(
        "--batch_size", type=int, default=50,
        help="Number of subfolders to process per batch."
    )
    parser.add_argument(
        "--parallel", action="store_true",
        help="Enable parallel processing in the model (if supported)."
    )
    parser.add_argument(
        "--retry_errors", action="store_true",
        help="Retry previously errored folders (using errors.json)."
    )
    args = parser.parse_args()

    # Instantiate the model.
    model = RuleBased(parallel=args.parallel)
    model._DATA_FOLDER = args.data_folder

    # Get a list of all subfolder names in the data folder.
    all_model_ids = [
        d for d in os.listdir(args.data_folder)
        if os.path.isdir(os.path.join(args.data_folder, d))
    ]

    # If --retry_errors is set, read the error log and process only those folders.
    if args.retry_errors:
        try:
            with open("errors.json", "r") as f:
                errors_data = json.load(f)
            error_model_ids = list(errors_data.keys())
            print("Retrying error model ids:", error_model_ids)
            all_model_ids = error_model_ids
        except Exception as e:
            print(f"Could not load errors.json: {e}")
            print("Processing all folders instead.")

    results_dict = {}  # To store successful processing results.
    errors_dict = {}   # To record any errors encountered.

    total = len(all_model_ids)
    batch_size = args.batch_size

    print(f"Total folders to process: {total}")

    # Process folders in batches.
    for i in range(0, total, batch_size):
        batch = all_model_ids[i : i + batch_size]
        print(f"\n--- Processing batch {i // batch_size + 1} (folders: {batch}) ---")
        process_folders(model, batch, results_dict, errors_dict)

        # Write intermediate results to help avoid re-running everything if something fails.
        with open("results_partial.json", "w") as f:
            json.dump(results_dict, f, indent=2)
        with open("errors.json", "w") as f:
            json.dump(errors_dict, f, indent=2)
        print(f"Batch {i // batch_size + 1} complete. Results and errors saved.")

    # Write final results.
    with open("results.json", "w") as f:
        json.dump(results_dict, f, indent=2)
    print("\nProcessing complete. Final results saved to results.json.")
    if errors_dict:
        print("Some folders encountered errors. See errors.json for details.")
    else:
        print("No errors encountered.")

if __name__ == "__main__":
    main()
