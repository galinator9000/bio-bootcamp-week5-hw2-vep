import os
from sqlalchemy.exc import IntegrityError
from src.database import create_tables, Session

def parse_and_insert_vep_data():
    print("Starting ClinVar data import...")
    session = Session()

    try:
        # TODO: Implement logic
        pass
    
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
    parse_and_insert_vep_data()
