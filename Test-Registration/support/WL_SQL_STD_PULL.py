import pyodbc
import csv
import os

# Connect to the SQL server
cnxn = pyodbc.connect("DRIVER={SQL Server};"
                      "SERVER=ES00vPADOSQL150;"
                      "DATABASE=STARS;"
                      "Trusted_Connection=yes;")

# Create a cursor
cursor = cnxn.cursor()

# Define the SQL query
query = """
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

# Execute the query
cursor.execute(query)

# Fetch the results
rows = cursor.fetchall()
print
# Now you can use the updated rows as needed

# Define the folder path where the CSV file will be saved
folder_path = 'E:\\NYCDOE-github-KM3\\Test-Registration\\'

# Define the file name for the CSV file
import datetime

now = datetime.datetime.now()
file_name = f"studentLvl_query_results_{now.strftime('%Y-%m-%d %H-%M-%S')}.csv"

# Open the file in write mode and create a CSV writer object
with open(folder_path + file_name, "w", newline="") as file:
    writer = csv.writer(file)

    # Write the column names
    writer.writerow([i[0] for i in cursor.description])

    # Write the rows
    writer.writerows(rows)

# Close the cursor and connection
cursor.close()
cnxn.close()
