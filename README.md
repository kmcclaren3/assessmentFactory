The purpose of this repository it holds the code for the full lifecycle of an assessment administration. 
Part 1 - pullRegistrations.py  

usage: pullRegistrations.py [-h] [-C] [-P] [--year YEAR] [--output OUTPUT] --testlist TESTLIST

Utility script to process and output school registration data.

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

Part 2 - createTAOFiles.py

         input='filename.csv' 
         -s  
         -a
         -p
         -t  Create the .CSV file for printiing student admit tickets
         
