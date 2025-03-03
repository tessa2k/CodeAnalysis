'''
Run rule based method for all models
python rule_based/run.py [--data_folder] --batch_size 50 [--parallel]
'''
import os
import json
import argparse
from tqdm import tqdm
# from rule_based import RuleBased
from rule_based_kgram import RuleBased # rule-based v2.0

def main():
    parser = argparse.ArgumentParser(
        description="Run the RuleBased Model on all subfolders using batch processing."
    )
    parser.add_argument(
        "--data_folder",
        type=str,
        default="../All_Data",
        help="Path to the root data folder containing subfolders (each a model id)."
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        default=False,
        help="True to run in batch."
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=50,
        help="Number of subfolders to process per batch."
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Enable parallel processing for each batch (default: False)."
    )
    parser.add_argument(
        "--retry_errors",
        action="store_true",
        default=False,
        help="Retry processing folders that previously encountered errors."
    )

    args = parser.parse_args()

    # Instantiate the RuleBased model with the specified settings.
    model = RuleBased(parallel=args.parallel, batch_size=args.batch_size, batch=args.batch, max_num = 300) 
    model._DATA_FOLDER = args.data_folder

    print("Starting processing using scan_all_files() ...")
    if args.retry_errors:
        # If retrying, pass the retry_errors flag so only errored folders are reprocessed.
        results = model.scan_all_files_batches(retry_errors=True)
    else:
        results = model.scan_all_files()

    # Write the final results to a JSON file.
    output_file = "rule_based/rule_based_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Processing complete. Results written to {output_file}.")

    # Optionally, print out the collected file extensions.
    extensions = model.get_extentions()
    print("Collected file extensions:", extensions)

if __name__ == "__main__":
    main()
