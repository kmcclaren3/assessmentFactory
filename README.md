The purpose of this repository it holds the code for the full lifecycle of an assessment administration.  
pullRegistrations.py  
usage: pullRegistrations.py [-h] [-C] [-P] [--year YEAR] [--output OUTPUT] --testlist TESTLIST

Utility script to process and output school registration data from both ATS and STARS.

         options:
                    -h, --help           show this help message and exit
                    -C, --charter        Include Charter School data.
                                         If used alone, Public School data (-P) is excluded.
                                         If both -C and -P are used, both are included.
                    -P, --public         Include Public School data.
                                         If used alone, Charter School data (-C) is excluded.
                                         If both -C and -P are used, both are included.
                    --year YEAR          Specify the registration year (default: 2025).
                    --output OUTPUT      Name of merged output CSV file (default: registrations.csv).
                    --testlist TESTLIST  Path to a file containing a comma-separated list of exam codes.
                    
Dependedncies: Requieres ODBC connection on host machine to both databases.  
         output:         Column headers and definitions --  
                         CourseCode - Maximum of 5 alphanumeric characters.
                         SchoolDBN - Two digits followed by a member of the set: {M, X, Q, K, R}, followed by three numeric digits.
                         FirstName - Alpha String
                         LastName - Alpha string
                         StudentID - A string with exactly nine numeric digits.
                         AssignedSectionId - An integer between 0 and 99.
                         LEPFlag - A single digit of "0" or "1" 
                         GradeLevel - Should be an integer between 01-12, OK and PK are technically acceptable but will be flagged. 
                         CreatedDate - 
                         UpdatedDate - 
                         SchoolYear - A string with the format "20yy", where yy are the 2 digits of the Fall year of the school year.
                         TermId - A single member of the set {1, 2, 3}.
                         GUID -  
                         StudentDOEEmail - ALphanumeric string appended with "@nycstudents.net"
       

Part 2 - createTAOFiles.py

         input='filename.csv' 
         -s  
         -a
         -p
         -t  Create the .CSV file for printiing student admit tickets
         
