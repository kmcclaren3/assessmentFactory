# This python script is used to pull the World Language Exam Data for district and charter schools
import pyodbc
import csv
import datetime
import os

now = datetime.datetime.now()

def pull_roster_data(server, database, output_file, query, transform_func=None, output_header=None):
    """
    Connects to a SQL Server database, executes the provided query to retrieve roster data,
    applies an optional transformation function to each row, and saves the results to a CSV file.

    Args:
        server (str): The SQL Server instance name.
        database (str): The database name.
        output_file (str): The path to the output CSV file.
        query (str): The SQL query to execute.
        transform_func (callable, optional): A function that takes a row (tuple) and returns a transformed row (list or tuple).
                                             For example, a transformation function may split a full name, replace blank values, etc.
                                             If None, rows are written as returned.
        output_header (list, optional): The header row for the CSV output. If None and no transformation is applied,
                                        the original column names (from cursor.description) are used.
    """
    try:
        # Connect to the SQL server
        cnxn = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        )
        cursor = cnxn.cursor()

        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()

        # Apply transformation if provided
        if transform_func:
            transformed_rows = [transform_func(row) for row in rows]
        else:
            transformed_rows = rows

        # Determine header row. If an output header isn't provided, and no transformation is done,
        # then use the column names from the cursor.
        if output_header is None:
            if transform_func is None:
                output_header = [col[0] for col in cursor.description]
            else:
                # If a transform was applied, the caller should supply a header.
                raise ValueError("When applying a transformation, please provide an output_header parameter.")

        # Write the results to a CSV file
        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(output_header)  # Write header row
            writer.writerows(transformed_rows)

        print(f"Data successfully written to {output_file}")

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            print("Authentication error. Please check your credentials.")
        else:
            print(f"Database error: {ex}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnxn' in locals():
            cnxn.close()


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
charter_query = """
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
WHERE SCHOOL_YEAR = '20242025'
  AND (RECTYPE LIKE 'LOT%')
  AND (EXAM_CDE LIKE 'FX1SE')
  AND LEFT(SCHOOL_DBN, 2) = '84';
"""

# Define the custom header for the output CSV
header = [
    "CourseCode", "SchoolDBN", "FirstName", "LastName", "StudentID",
    "AssignedSectionId", "LEPFlag", "GradeLevel", "CreatedDate",
    "UpdatedDate", "SchoolYear", "TermId", "GUID", "StudentDOEEmail"
]
# Define the folder path where the CSV file will be saved
#charter_folder_path = r"E:\Users\gbenners\Documents\python_files\\"
charter_folder_path = 'E:\\NYCDOE-github-KM3\\Test-Registration\\'
charter_file_name = f"charter_school_students_{now.strftime('%Y-%m-%d %H-%M-%S')}.csv"
charter_output_file = charter_folder_path + charter_file_name
#  Output CSV file name
pull_roster_data("ES00vPADOSQL110", "ATS_Demo", charter_output_file, charter_query, transform_func=transform_row, output_header=header);

# Define the SQL query
district_query = """
WITH MaxGradeLevel AS (
    SELECT ST.StudentID, MAX(GL.GradeLevel) AS GradeLevel
    FROM [STARS].[dbo].[Student] AS ST
    LEFT JOIN [STARS].[dbo].[StudentGradeOfficialClassFromATS] AS GL ON ST.StudentID = GL.StudentID
    WHERE GL.SchoolYear = '2024'
    GROUP BY ST.StudentID
)

SELECT DISTINCT SR.CourseCode, SC.SchoolDBN, ST.FirstName, ST.LastName, SR.StudentID, SR.AssignedSectionId, 
  ST.LEPFlag, GL.GradeLevel, SR.CreatedDate, SR.UpdatedDate,  SR.SchoolYear, SR.TermId, ST.GUID, ST.StudentDOEEmail 
FROM [STARS].[dbo].[StudentRequest] AS SR
LEFT JOIN [STARS].[dbo].[School] AS SC ON SR.NumericSchoolDBN = SC.NumericSchoolDBN
LEFT JOIN [STARS].[dbo].[Student] AS ST ON SR.StudentID = ST.StudentID
LEFT JOIN MaxGradeLevel AS GL ON ST.StudentID = GL.StudentID
WHERE SR.SchoolYear = '2024' 
  AND ((SR.CourseCode LIKE 'FX%' AND RIGHT(SR.CourseCode, 1) = 'E') OR SR.CourseCode LIKE 'ZXFS%')
ORDER BY SC.SchoolDBN ASC;
"""

# Define the folder path where the CSV file will be saved
district_folder_path = 'E:\\NYCDOE-github-KM3\\Test-Registration\\'
district_file_name = f"studentLvl_query_results_{now.strftime('%Y-%m-%d %H-%M-%S')}.csv"
district_output_file = district_folder_path + district_file_name
#  Output CSV file name

pull_roster_data("ES00vPADOSQL150", "STARS", district_output_file, district_query);
