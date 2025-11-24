import argparse
import pandas as pd
import re
import os
import sys
from datetime import datetime

# --- Validation Functions ---

def is_valid_course_code(code):
    """
    Validate the CourseCode: exactly 5 alphanumeric characters.
    """
    if not isinstance(code, str):
        return False
    # Use regex to check for exactly 5 characters, each being alphanumeric
    return bool(re.match(r'^[a-zA-Z0-9]{5}$', code))

def is_valid_school_dbn(dbn):
    """
    Validate the SchoolDBN format 
    Uses regex to check for exactly two digits, a borough letter, and three digits.
    """
    if not isinstance(dbn, str):
        return False
    pattern = r'^\d{2}[MXQKR]\d{3}$'
    return bool(re.match(pattern, value))
    

def is_valid_student_id(student_id):
    """
    Validate the StudentID: exactly 9 numeric digits.
    """
    if not isinstance(student_id, (int, str)):
        return False
    # Convert to string to ensure consistent length check
    s_id = str(student_id)
    return len(s_id) == 9 and s_id.isdigit()

def is_valid_assigned_section_id(section_id):
    """
    Validate the AssignedSectionId: an integer between 0 and 99 (inclusive).
    """
    if not isinstance(section_id, (int, str)):
        return False
    try:
        s_id = int(section_id)
        return 0 <= s_id <= 99
    except ValueError:
        return False

def is_valid_schoolyear(schoolyear):
    """
    Validate the schoolyear: an integer starting with 20.
    """
    if not isinstance(schoolyear, (int, str)):
        return False
    return len(schoolyear) >= 4 and schoolyear[:2] == '20' and schoolyear[-2:].isdigit()

def is_valid_term_id(term_id: str) -> bool:
    """
    Validate the term_ID: an integer 1,2, or 3.
    """
    if not isinstance(term_id, (int, str)):
        return False
    return term_id in ['1', '2', '3']

# (Stubs for other column validations as needed)

# --- Account Creation Stubs ---

def create_groups(student_data):
    """Stub for creating group accounts."""
    print(f"Processing group account creation.")
    # Add account creation logic here
    pass

def create_student_accounts(student_data):
    """Stub for creating student accounts."""
    print(f"Processing student account creation for {len(student_data)} valid records.")
    # Add account creation logic here
    pass

def create_proctor_accounts():
    """Stub for creating proctor accounts."""
    print("Processing proctor account creation. ")
    # Add account creation logic here
    pass

def create_admin_accounts():
    """Stub for creating admin accounts."""
    print("Processing admin account creation.")
    # Add account creation logic here
    pass

def create_tickets():
    """Stub for creating test tickets."""
    print("Processing test ticket creation.")
    # Add ticket creation logic here
    pass

# --- Main Processing Logic ---

def process_registrations(filename, create_students: bool, create_proctors: bool, create_admins: bool, create_tickets: bool):
    """
    Loads and validates the CSV file, then calls account creation functions based on flags.
    Generates a timestamped 'rejects.csv' file for all rejected records.
    """
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    try:
        df = pd.read_csv(filename)
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{filename}' is empty.")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Error: Could not parse '{filename}'. Check file format.")
        sys.exit(1)

    required_cols = ['CourseCode', 'SchoolDBN', 'FirstName', 'LastName', 'StudentID', 'AssignedSectionId', 
                     'LEPFlag', 'GradeLevel', 'CreatedDate', 'UpdatedDate', 'SchoolYear', 'TermId', 'GUID', 
                     'StudentDOEEmail']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        print(f"Error: Missing required columns in CSV file: {missing_cols}")
        sys.exit(1)

    valid_records = []
    rejected_records = []
    invalid_rows_count = 0

    for index, row in df.iterrows():
        is_valid = True
        if not is_valid_course_code(row['CourseCode']):
            print(f"Invalid entry in row {index + 1}: Invalid CourseCode '{row['CourseCode']}'")
            is_valid = False
        if not is_valid_school_dbn(row['SchoolDBN']):
            print(f"Invalid entry in row {index + 1}: Invalid SchoolDBN '{row['SchoolDBN']}'")
            is_valid = False
        if not is_valid_student_id(row['StudentID']):
            print(f"Invalid entry in row {index + 1}: Invalid StudentID '{row['StudentID']}'")
            is_valid = False
        if not is_valid_assigned_section_id(row['AssignedSectionId']):
            print(f"Invalid entry in row {index + 1}: Invalid AssignedSectionId '{row['AssignedSectionId']}'")
            is_valid = False
        if not is_valid_schoolyear(row['SchoolYear']):
            print(f"Invalid entry in row {index + 1}: Invalid School Year '{row['SchoolYear']}'")
            is_valid = False
        if not is_valid_term_id(row['termID']):
            print(f"Invalid entry in row {index + 1}: Invalid TermID '{row['TermID']}'")
            is_valid = False
        if is_valid:
            valid_records.append(row)
        else:
            invalid_rows_count += 1
            rejected_records.append(row)
            print(f"Ignoring row {index + 1} due to invalid entries.")

#    print(f"\nCSV processing complete. Total rows: {len(df)}, Valid rows: {len(valid_records)}, Invalid rows: {invalid_rows_count}")

# --- Rejects File Creation Logic ---
    if rejected_records:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        rejects_filename = f"rejects_{timestamp}.csv"
        # Convert the list of rejected records (which are Pandas Series) back into a DataFrame
        # using the same columns as the original file
        rejected_df = pd.DataFrame(rejected_records, columns=df.columns)

        # Write the DataFrame to a CSV file, including the header
        try:
            rejected_df.to_csv(rejects_filename, index=False)
            print(f"\nCreated rejects file: **{rejects_filename}** with {len(rejected_records)} rejected records.")
        except Exception as e:
            print(f"\nError writing rejects file: {e}")
            
    # --- End Rejects File Creation Logic ---

    print(f"\nCSV processing complete. Total rows: {len(df)}, Valid rows: {len(valid_records)}, Invalid rows: {invalid_rows_count}")

    if valid_records:
        create_groups(valid_records)
        if create_students:
            create_student_accounts(valid_records)
        if create_proctors:
            create_proctor_accounts(valid_records)
        if create_admins:
            create_admin_accounts(valid_records)
        if create_tickets:
            create_tickets()
    else:
        print("No valid records to process for account creation.")


# --- Command Line Argument Parsing ---

def main():
    parser = argparse.ArgumentParser(description="Process assessment registrations and create TAO account files.")
    
    parser.add_argument('input', type=str, help="The input CSV file name (e.g., filename.csv)")
    
    parser.add_argument('-s', '--students', action='store_true', help="Create TAO student account file")
    parser.add_argument('-p', '--proctors', action='store_true', help="Create TAO proctor account file")
    parser.add_argument('-a', '--admins', action='store_true', help="Create TAO admin account file")
    parser.add_argument('-t', '--tickets', action='store_true', help="Create test ticket lists")
    
    args = parser.parse_args()

    # Determine which accounts to create. Default is all if no flags are present.
    no_flags_set = not any([args.students, args.proctors, args.admins, args.tickets])
    
    create_students_bool = args.students or no_flags_set
    create_proctors_bool = args.proctors or no_flags_set
    create_admins_bool = args.admins or no_flags_set
    create_tickets_bool = args.tickets or no_flags_set
    print (f"Create Students: {create_students_bool}, Proctors: {create_proctors_bool}, Admins: {create_admins_bool}, Tickets: {create_tickets_bool}")
    process_registrations(args.input, create_students_bool, create_proctors_bool, create_admins_bool, create_tickets_bool)

if __name__ == "__main__":
    main()
