import argparse
import datetime
import csv
import os
import sys
import pyodbc

ATS_SERVER='ES00vPADOSQL110'
STARS_SERVER='ES00vPADOSQL150'
ATS_DATABASE='ATS_DEMO'
STARS_DATABASE='STARS'   
DRIVER='SQL Server'
def parse_arguments():
    """
    Parses command-line arguments and returns a dictionary of processed options.
    """
    current_year = datetime.datetime.now().year

    parser = argparse.ArgumentParser(
        description="Utility script to process and output school registration data.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- School Type Selection ---
    parser.add_argument(
        '-C', '--charter',
        dest='_charter_specified',
        action='store_true',
        help=('Include Charter School data.\n'
              'If used alone, Public School data (-P) is excluded.\n'
              'If both -C and -P are used, both are included.')
    )
    parser.add_argument(
        '-P', '--public',
        dest='_public_specified',
        action='store_true',
        help=('Include Public School data.\n'
              'If used alone, Charter School data (-C) is excluded.\n'
              'If both -C and -P are used, both are included.')
    )

    # --- Year Argument ---
    parser.add_argument(
        '--year',
        type=int,
        default=current_year,
        help=f'Specify the registration year (default: {current_year}).'
    )

    # --- Output Filenames ---
    parser.add_argument(
        '--output',
        type=str,
        default='registrations.csv',
        help='Name of merged output CSV file (default: registrations.csv).'
    )

    # --- Exam Code List Argument ---
    parser.add_argument(
        '--testlist',
        type=str,
        required=True,
        help='Path to a file containing a comma-separated list of exam codes.'
    )


    args = parser.parse_args()

    # --- Read exam code list ---
    if not os.path.exists(args.testlist):
        print(f"Error: test list file '{args.testlist}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.testlist, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        test_codes = {code.strip() for code in content.split(',') if code.strip()}

    # --- Determine charter/public inclusion logic ---
    if args._charter_specified and args._public_specified:
        charter = True
        public = True
    elif args._charter_specified:
        charter = True
        public = False
    elif args._public_specified:
        charter = False
        public = True
    else:
        charter = True
        public = True  # default: both

    return {
        "charter": charter,
        "public": public,
        "year": args.year,
        "output": args.output,
        "test_codes": test_codes
    }


def transform_row(row):
    # Assume row indexes correspond to:
    # 0: StudentDOEEmail, 1: STUDENT_NAM, 2: StudentID, 3: SchoolDBN,
    # 4: CourseCode, 5: GradeLevel, 6: RECTYPE, 7: SCHOOL_YEAR,
    # 8: TermId, 9: AssignedSectionId

    # STUDENT_NAM is "LastName, FirstName"
    full_name = row[1] if row[1] else ""
    name_parts = full_name.split(",")
    if len(name_parts) == 2:
        last_name = name_parts[0].strip()
        first_name = name_parts[1].strip()
    else:
        first_name = full_name.strip()
        last_name = ""

    # Set AssignedSectionId to '99' if blank (None or empty)
    assigned_section = row[9] if row[9] not in (None, "") else "99"
    # Extract the first 4 characters of SCHOOL_YEAR
    school_year = row[7][:4] if row[7] else ""

    # Construct the new row in the desired order
    return [
        row[4],           # CourseCode
        row[3],           # SchoolDBN
        first_name,       # FirstName
        last_name,        # LastName
        row[2],           # StudentID
        assigned_section, # AssignedSectionId
        "",               # LEPFlag (blank)
        row[5],           # GradeLevel
        "",               # CreatedDate (blank)
        "",               # UpdatedDate (blank)
        school_year,      # SchoolYear (first 4 characters)
        row[8],           # TermId
        "",               # GUID (blank)
        row[0]            # StudentDOEEmail
    ]


def query_student_data(include_public=True, include_charter=True, year=datetime.datetime.now().year, test_codes=None):
    #connection_string = f"DRIVER={DRIVER}; SERVER={STARS_SERVER}; DATABASE={STARS_DATABASE}; Trusted_Connection=yes;"
    #print({connection_string})
    year=int(year)  
    # print(year)
    """
    Stub function for querying the database.
    Returns one or two lists of students (one per school type).
    Each student is represented as a tuple or dict (to be defined later).
    """
    print(f"Querying database(s) for year={year}...")
    charter_students = []
    public_students = []

    if include_charter:
        connection_string = f"DRIVER={DRIVER}; SERVER={ATS_SERVER}; DATABASE={ATS_DATABASE}; Trusted_Connection=yes;"
        # print({connection_string})
        try:
            with pyodbc.connect(connection_string, timeout=5) as cnxn: # Setting a timeout parameter to prevent long hangs on failed connections
                print(f"Successfully connected to the ATS database.")
                # print(f"Year={year}{year+1}")
                # print(f"Test Codes={test_codes}")
                test_codes_list = list(test_codes) # Convert set to list for consistent ordering
                placeholders = ','.join(['?'] * len(test_codes_list))
                # print(placeholders)
                cursor = cnxn.cursor()
                query = f"""
                        SELECT DISTINCT                              
                          APPROVAL_USER as StudentDOEEmail,
                          STUDENT_NAM,
                          STUDENT_ID as StudentID,                                                                            
                          SCHOOL_DBN as SchoolDBN,
                          EXAM_CDE as CourseCode,
                          GRADE_LEVEL as GradeLevel,
                          RECTYPE,
                          SCHOOL_YEAR,
                          TERM as TermId,
                          SECTION_NUM as AssignedSectionId
                        FROM [ATS_Demo].[dbo].[EXAMSCAN]
                        WHERE SCHOOL_YEAR = CAST(? AS VARCHAR)
                          AND EXAM_CDE IN ({placeholders})
                          AND LEFT(SCHOOL_DBN, 2) = '84';
                        """ 

# Need to change to something like.... EXAM_CDE IN ('string_value_1', 'string_value_2', 'string_value_3', ...)
# Would I need the RECTYPE? 

                # print(query)
                params = [f"{year}{year+1}", *test_codes_list]
                # print(params)
                # print("Query:\n", query)
                cursor.execute(query, params)
                charter_students = cursor.fetchall()
                charter_students = [transform_row(row) for row in charter_students]
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Connection failed.")
            print(f"Error details: {ex}")
            print(f"SERVER={ATS_SERVER} DB={ATS_DATABASE}")
            # Inspect the SQLSTATE for more specific information if needed      

    if include_public:
        connection_string = f"DRIVER={DRIVER}; SERVER={STARS_SERVER}; DATABASE={STARS_DATABASE}; Trusted_Connection=yes;"
        # print({connection_string})
        try:
            with pyodbc.connect(connection_string, timeout=5) as cnxn: # Setting a timeout parameter to prevent long hangs on failed connections
                print(f"Successfully connected to the STARS database.")
                test_codes_list = list(test_codes) # Convert set to list for consistent ordering
                placeholders = ','.join(['?'] * len(test_codes_list))
               # print(placeholders)
               # print(test_codes={test_codes_list})
                cursor = cnxn.cursor()
                # Define the SQL query
                query = f"""
                    WITH MaxGradeLevel AS (
                        SELECT ST.StudentID, MAX(GL.GradeLevel) AS GradeLevel
                        FROM [STARS].[dbo].[Student] AS ST
                        LEFT JOIN [STARS].[dbo].[StudentGradeOfficialClassFromATS] AS GL ON ST.StudentID = GL.StudentID
                        WHERE GL.SchoolYear = CAST(? AS SMALLINT)
                        GROUP BY ST.StudentID
                    )

                    SELECT DISTINCT SR.CourseCode, SC.SchoolDBN, ST.FirstName, ST.LastName, SR.StudentID, SR.AssignedSectionId, 
                    ST.LEPFlag, GL.GradeLevel, SR.CreatedDate, SR.UpdatedDate,  SR.SchoolYear, SR.TermId, ST.GUID, ST.StudentDOEEmail 
                    FROM [STARS].[dbo].[StudentRequest] AS SR
                    LEFT JOIN [STARS].[dbo].[School] AS SC ON SR.NumericSchoolDBN = SC.NumericSchoolDBN
                    LEFT JOIN [STARS].[dbo].[Student] AS ST ON SR.StudentID = ST.StudentID
                    LEFT JOIN MaxGradeLevel AS GL ON ST.StudentID = GL.StudentID
                    WHERE SR.SchoolYear = CAST(? AS SMALLINT) 
                      AND (SR.CourseCode IN ({placeholders}))
                    ORDER BY SC.SchoolDBN ASC;
                """

# Need to change to something like.... SR.CourseCode IN ('string_value_1', 'string_value_2', 'string_value_3', ...)
                # print(query)
                params = [f"{year}",f"{year}", *test_codes_list]
                # print(params)
                cursor.execute(query, params)
                public_students = cursor.fetchall()    
                #print(public_students)
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Connection failed.")
            print(f"Error details: {ex}")
            print(f"SERVER={ATS_SERVER} DB={ATS_DATABASE}")
            # Inspect the SQLSTATE for more specific information if needed
    return public_students, charter_students


def write_merged_output(public_students, charter_students, output_filename):
    """
    Writes merged student data to a CSV file with a timestamp appended to the filename.
    """
    # Define the custom header for the output CSV
    HEADER = ["CourseCode", "SchoolDBN", "FirstName", "LastName", "StudentID",
              "AssignedSectionId", "LEPFlag", "GradeLevel", "CreatedDate",
              "UpdatedDate", "SchoolYear", "TermId", "GUID", "StudentDOEEmail"
            ]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(output_filename)
    merged_filename = f"{base}_{timestamp}{ext}"

    merged_data = []
    if public_students:
        merged_data.extend(public_students)
    if charter_students:
        merged_data.extend(charter_students)

    with open(merged_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADER)
        writer.writerows(merged_data)

    print(f"Data successfully written to {merged_filename}")


def main():
    opts = parse_arguments()
    # print("--- Pull Registrations Script Initialized ---")
    # print(f"Include Charter: {opts['charter']}")
    # print(f"Include Public: {opts['public']}")
    # print(f"Year: {opts['year']}")
    # print(f"Output File: {opts['output']}")
    # print("---------------------------------------------")

    public_students, charter_students = query_student_data(
        include_public=opts["public"],
        include_charter=opts["charter"],
        year=opts["year"],
        test_codes=opts["test_codes"]
    )
    print(f"Public Students Retrieved: {len(public_students)}")
    print(f"Charter Students Retrieved: {len(charter_students)}")

    write_merged_output(public_students, charter_students, opts["output"])

if __name__ == '__main__':
    main()