import os
import json
from functools import cmp_to_key
from src.database import create_tables, Session, Gene, Variant, VariantCall

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
            16 if "canonical" in x and x["canonical"] == "1" else 0,
            8 if "impact" in x and x["impact"] == "HIGH" else 0,
            4 if "impact" in x and x["impact"] == "MODERATE" else 0,
            2 if "impact" in x and x["impact"] == "LOW" else 0,
            1 if "impact" in x and x["impact"] == "MODIFIER" else 0,
        ])

    return calculate_score(b)- calculate_score(a)

def parse_and_insert_vep_data(vep_data_folder_path="data"):
    print("Starting VEP data import...")
    session = Session()

    try:
        # Path to the downloaded JSON file(s)
        if not os.path.exists(vep_data_folder_path):
            print(f"Error: Data folder not found at {vep_data_folder_path}")
            return
        
        vep_data_files = [f for f in os.listdir(vep_data_folder_path) if f.endswith(".json")]
        for vep_data_file in vep_data_files:
            data_path = os.path.join(vep_data_folder_path, vep_data_file)

            sample_name = vep_data_file.replace(".json", "").split("_")[0]

            line_count = 0
            for variant_raw_line in iterative_file_reader(data_path):
                if line_count % 10000 == 0:
                    session.commit()

                # TODO: Remove later on, intended for testing
                if line_count >= 5000:
                    break

                line_count += 1
                variant = json.loads(variant_raw_line)

                if "transcript_consequences" not in variant:
                    continue

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

                # Extract gene information from worst transcript
                gene_symbol = worst_trx.get("gene_symbol")
                gene_biotype = worst_trx.get("biotype")  # May not be present in all cases
                
                # Extract rs_id if present in the variant
                rs_id = None
                if "colocated_variants" in variant:
                    for colocated in variant["colocated_variants"]:
                        if colocated.get("id", "").startswith("rs"):
                            rs_id = colocated["id"]
                            break
                
                # Create or get Gene
                gene = None
                if gene_symbol:
                    gene = session.query(Gene).filter_by(symbol=gene_symbol).first()
                    if not gene:
                        gene = Gene(
                            symbol=gene_symbol,
                            biotype=gene_biotype
                        )
                        session.add(gene)
                        session.flush()  # To get the gene_id
                
                # Create Variant
                variant_obj = Variant(
                    chrom=chrom,
                    pos=int(pos),
                    ref=ref,
                    alt=alt,
                    rs_id=rs_id,
                    impact=worst_trx.get("impact"),
                    gene_id=gene.gene_id if gene else None
                )
                session.add(variant_obj)
                session.flush()  # To get the variant_id
                
                # Create VariantCall
                genotype = vcf_inp.get("GT")
                depth = vcf_inp.get("DP")
                variant_call = VariantCall(
                    sample_name=sample_name,
                    genotype=genotype,
                    depth=depth,
                    variant_id=variant_obj.variant_id
                )
                session.add(variant_call)
                
                print(f"Processed variant (line: {line_count}): {chrom}:{pos} {ref}>{alt} in gene {gene_symbol} (impact: {worst_trx.get('impact')})")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Final commit and close the session
        session.commit()
        session.close()
        print("Data import finished.")

if __name__ == "__main__":
    create_tables()
    parse_and_insert_vep_data("/data")
