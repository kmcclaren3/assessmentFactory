import pyodbc

# Replace with your specific connection string
# Examples are shown below
connection_string = 'DRIVER={SQL Server}; SERVER=ES00vPADOSQL150; DATABASE=STARS; Trusted_Connection=yes;'

try:
    with pyodbc.connect(connection_string, timeout=5) as cnxn: # Consider setting a timeout parameter to prevent long hangs on failed connections
        print(f"Successfully connected to the database.")

except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print(f"Connection failed.")
    print(f"Error details: {ex}")
    # Inspect the SQLSTATE for more specific information if needed
