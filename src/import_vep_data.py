import os
import json
from functools import cmp_to_key
#from sqlalchemy.exc import IntegrityError
#from src.database import create_tables, Session

def iterative_file_reader(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                yield line
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def transcript_selection(a, b):
    def calculate_score(x):
        return sum([
            16 if x["canonical"] == "1" else 0,
            8 if x["impact"] == "HIGH" else 0,
            4 if x["impact"] == "MODERATE" else 0,
            2 if x["impact"] == "LOW" else 0,
            1 if x["impact"] == "MODIFIER" else 0,
        ])

    return calculate_score(b)- calculate_score(a)

def parse_and_insert_vep_data(vep_data_folder_path="data"):
    print("Starting VEP data import...")
    #session = Session()

    try:
        # Path to the downloaded JSON file(s)
        if not os.path.exists(vep_data_folder_path):
            print(f"Error: Data folder not found at {vep_data_folder_path}")
            return
        
        vep_data_files = [f for f in os.listdir(vep_data_folder_path) if f.endswith(".json")]
        for vep_data_file in vep_data_files:
            data_path = os.path.join(vep_data_folder_path, vep_data_file)

            sample_name = data_path.replace(".json", "")

            line_count = 0
            for variant_raw_line in iterative_file_reader(data_path):
                if line_count >= 1:
                    break

                line_count += 1
                variant = json.loads(variant_raw_line)
                print(variant)

                # Parse VCF input part
                vinp = variant["input"].split("\t")
                vcf_inp = dict(zip(
                    vinp[8].split(":"),
                    [v if v != "." else None for v in vinp[9].split(":")]
                ))

                chrom = vinp[0]
                pos = vinp[1]
                ref = vinp[3]
                alt = vinp[4]

                # Transcript consequence selection
                vtrxs = variant["transcript_consequences"]
                worst_trx = sorted(vtrxs, key=cmp_to_key(transcript_selection))[0]

                ### INSERTION IMPLEMENTATION GOES HERE

        
    except Exception as e:
        #session.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Final commit and close the session
        #session.commit()
        #session.close()
        print("Data import finished.")

if __name__ == "__main__":
    # create_tables()
    parse_and_insert_vep_data("data")
