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

# Helper functions

def generate_password(prefix, postfix, length):
    """
    Generates a password: prefix + random_alphanumeric + postfix.
    The random part excludes 'l', '1', 'o', '0' to avoid confusion.
    """
    # Define allowed characters: alphanumeric excluding confusing ones
    allowed_chars = [
        c for c in string.ascii_letters + string.digits 
        if c not in ['l', '1', 'o', '0']
    ]
    
    random_part = ''.join(random.choice(allowed_chars) for _ in range(length))
    return f"{prefix}{random_part}{postfix}"


# --- Account Creation ---

def create_groups(student_data):
    """
    Creates a CSV file for groups based on distinct combinations of CourseCode, 
    SchoolDBN, and AssignedSectionID.
    """
    print(f"Processing group account creation...")

    if not student_data:
        print("No valid student data available to create groups.")
        return 0

    # Convert the list of valid records (Series) back to a DataFrame
    df = pd.DataFrame(student_data)

    # Ensure necessary columns are strings to prevent concatenation errors
    # (e.g., if AssignedSectionId was read as int)
    df['CourseCode'] = df['CourseCode'].astype(str)
    df['SchoolDBN'] = df['SchoolDBN'].astype(str)
    df['AssignedSectionId'] = df['AssignedSectionId'].astype(str)
    df['SchoolYear'] = df['SchoolYear'].astype(str)

    # 1. Generate Group Name
    # Logic: <CourseCode><last 2 digits of SchoolYear>@<DBN><AssignedSectionId>
    
    # Get last 2 digits of school year
    school_year_suffix = df['SchoolYear'].str[-2:]
    
    df['group_name'] = (
        df['CourseCode'] + 
        school_year_suffix + 
        "@" + 
        df['SchoolDBN'] + 
        df['AssignedSectionId']
    )

    # 2. Extract unique groups
    # We only need one entry per distinct group name
    groups_output = df[['group_name']].drop_duplicates().copy()

    # 3. Add static columns
    # "group_description", "group_active", "group_organizationId"
    groups_output['group_description'] = ""
    groups_output['group_active'] = "TRUE"
    groups_output['group_organizationId'] = "Root"

    # 4. Reorder columns to match requirements
    required_columns = ["group_name", "group_description", "group_active", "group_organizationId"]
    groups_output = groups_output[required_columns]

    # 5. Write to file
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"groups_{timestamp}.csv"

    try:
        groups_output.to_csv(filename, index=False)
        record_count = len(groups_output)
        print(f"Created group file: **{filename}** with {record_count} unique groups.")
        return record_count
    except Exception as e:
        print(f"Error writing group file: {e}")
        return 0

def create_student_accounts(student_data):
    """
    Creates a CSV file for student accounts (testtakers).
    """
    print(f"Processing student account creation for {len(student_data)} valid records.")
    
    if not student_data:
        print("No valid student data available to create student accounts.")
        return 0

    # Convert to DataFrame
    df = pd.DataFrame(student_data)
    
    # Ensure necessary columns are strings
    df['CourseCode'] = df['CourseCode'].astype(str)
    df['SchoolDBN'] = df['SchoolDBN'].astype(str)
    df['AssignedSectionId'] = df['AssignedSectionId'].astype(str)
    df['SchoolYear'] = df['SchoolYear'].astype(str)
    df['FirstName'] = df['FirstName'].astype(str)
    df['LastName'] = df['LastName'].astype(str)
    df['StudentDOEEmail'] = df['StudentDOEEmail'].astype(str)

    # 1. Generate Group Name (Same logic as create_groups)
    school_year_suffix = df['SchoolYear'].str[-2:]
    
    df['group_name'] = (
        df['CourseCode'] + 
        school_year_suffix + 
        "@" + 
        df['SchoolDBN'] + 
        df['AssignedSectionId']
    )

    # 2. Construct Student Fields
    
    # user_username: StudentDOEEmail
    df['user_username'] = df['StudentDOEEmail']
    
    # user_name: First and last names concatenated
    df['user_name'] = df['FirstName'] + df['LastName']
    
    # user_password: Prefix (FirstInitial + LastInitial) + 6 random chars + No Postfix
    def make_student_password(row):
        # Get first initials, defaulting to 'X' if empty
        f_init = row['FirstName'][0].upper() if row['FirstName'] else 'X'
        l_init = row['LastName'][0].upper() if row['LastName'] else 'X'
        prefix = f"{f_init}{l_init}"
        return generate_password(prefix, "", 6)

    df['user_password'] = df.apply(make_student_password, axis=1)

    # user_email: Blank
    df['user_email'] = ""
    
    # user_language: "en-US"
    df['user_language'] = "en-US"
    
    # user_active: "TRUE"
    df['user_active'] = "TRUE"
    
    # group_role: "TestTaker"
    df['group_role'] = "TestTaker"
    
    # user_organizationId: DBN
    df['user_organizationId'] = df['SchoolDBN']

    # 3. Reorder columns
    required_columns = [
        "user_username", "user_name", "user_password", "user_email", 
        "user_language", "user_active", "group_role", "group_name", 
        "user_organizationId"
    ]
    
    students_output = df[required_columns].copy()

    # 4. Write to file
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"testtakers_{timestamp}.csv"

    try:
        students_output.to_csv(filename, index=False)
        record_count = len(students_output)
        print(f"Created student file: **{filename}** with {record_count} student accounts.")
        return record_count
    except Exception as e:
        print(f"Error writing student file: {e}")
        return 0


def create_proctor_accounts(student_data):
    """
    Creates a CSV file for proctor accounts.
    One proctor for each unique group.
    """
    print("Processing proctor account creation...")

    if not student_data:
        print("No valid student data available to create proctors.")
        return 0

    # Reuse DataFrame logic from create_groups to determine unique groups
    df = pd.DataFrame(student_data)
    
    df['CourseCode'] = df['CourseCode'].astype(str)
    df['SchoolDBN'] = df['SchoolDBN'].astype(str)
    df['AssignedSectionId'] = df['AssignedSectionId'].astype(str)
    df['SchoolYear'] = df['SchoolYear'].astype(str)

    school_year_suffix = df['SchoolYear'].str[-2:]
    
    df['group_name'] = (
        df['CourseCode'] + 
        school_year_suffix + 
        "@" + 
        df['SchoolDBN'] + "-" +
        df['AssignedSectionId']
    )

    # Extract unique groups
    proctors_output = df[['group_name']].drop_duplicates().copy()

    # Define Proctor Logic
    # user_username and user_name: group_name + "PCT"
    proctors_output['user_username'] = proctors_output['group_name'] + "PCT"
    proctors_output['user_name'] = proctors_output['group_name'] + "PCT"

    proctors_output['user_password'] = proctors_output.apply(
        lambda x: generate_password("", "PCT", 6), axis=1
    )

    # Static fields
    proctors_output['user_email'] = ""
    proctors_output['user_language'] = "en-US"
    proctors_output['user_active'] = "TRUE"
    proctors_output['group_name'] = proctors_output['group_name'] + "PCT"
    proctors_output['user_organizationId'] = df['SchoolDBN'] 

    # Reorder columns
    required_columns = [
        "user_username", "user_name", "user_password", "user_email", 
        "user_language", "user_active", "group_role", "group_name", 
        "user_organizationId"
    ]
    
    proctors_output = proctors_output[required_columns]

    # Write to file
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"proctors_{timestamp}.csv"

    try:
        proctors_output.to_csv(filename, index=False)
        record_count = len(proctors_output)
        print(f"Created proctor file: **{filename}** with {record_count} unique proctor accounts.")
        return record_count
    except Exception as e:
        print(f"Error writing proctor file: {e}")
        return 0


def create_admin_accounts(student_data, num_admins=2):
    """
    Creates a CSV file for admin accounts.
    Creates 'num_admins' (default 2) for each distinct SchoolDBN.
    """
    print(f"Processing admin account creation for {num_admins} admins per DBN...")
    
    if not student_data:
        print("No valid student data available to create admins.")
        return 0

    # Convert to DataFrame
    df = pd.DataFrame(student_data)
    
    # Ensure columns are strings
    df['SchoolDBN'] = df['SchoolDBN'].astype(str)
    df['SchoolYear'] = df['SchoolYear'].astype(str)
    
    # Get distinct combinations of DBN and SchoolYear
    # We need SchoolYear to determine the suffix (YY) for the username
    unique_orgs = df[['SchoolDBN', 'SchoolYear']].drop_duplicates()
    
    admin_records = []
    
    for _, row in unique_orgs.iterrows():
        dbn = row['SchoolDBN']
        year = row['SchoolYear']
        # Extract last 2 digits of the year
        year_suffix = year[-2:]
        
        for i in range(1, num_admins + 1):
            # Username format: ADM+<Admin number>-<last 2 digits of year>@<DBN>
            # Example: ADM1-25@02M123
            username = f"ADM{i}-{year_suffix}@{dbn}"
            
            admin_records.append({
                "user_username": username,
                "user_name": username,
                # Using ADM postfix for password consistency
                "user_password": generate_password("", "ADM", 6), 
                "user_email": "",
                "user_language": "en-US",
                "user_active": "TRUE",
                "group_role": "ADMIN",
                "group_name": "", # Admins are typically organization-level, so group is blank
                "user_organizationId": dbn
            })
            
    admins_output = pd.DataFrame(admin_records)
    
    # Reorder columns
    required_columns = [
        "user_username", "user_name", "user_password", "user_email", 
        "user_language", "user_active", "group_role", "group_name", 
        "user_organizationId"
    ]
    
    # Write to file
    if not admins_output.empty:
        admins_output = admins_output[required_columns]
        
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"admins_{timestamp}.csv"
        
        try:
            admins_output.to_csv(filename, index=False)
            record_count = len(admins_output)
            print(f"Created admin file: **{filename}** with {record_count} admin accounts.")
            return record_count
        except Exception as e:
            print(f"Error writing admin file: {e}")
            return 0
    else:
        print("No admin accounts generated.")
        return 0

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
    parser = argparse.ArgumentParser(description="Process assessment registrations and create TAO account files.\nGroup file created automatically.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    
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
