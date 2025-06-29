import subprocess
import time



"""
? Verifies and re-runs Database Connection
"""
def wait_for_postgres(host,max_retries=5, delay_seconds=5):
    retries = 0
    while retries < max_retries:
        try:
            results = subprocess( # connect
                ["pg_isready", "-h", host], check=True,capture_output=True,text=True)
            if "accepting connections" in results.stdout:
                print("Successfully connected to db")
                return True # success
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to Postgres: {e}") # waiting for signal
            print(
                f"Restrying in {delay_seconds} seconds..... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting") # fails after max retries
    return False # fail

if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting ELT Script....")

source_config = {
    "dbname": "source_db",
    "user": "postgres",
    "password": "secret",
    "host": "source_postgres",
}

destination_config = {
    "dbname": "destination_db",
    "user": "postgres",
    "password": "secret",
    "host": "destination_postgres",
}

dump_command = {
    'pg_dump',
    '-h', source_config["host"],
    '-u', source_config["user"],
    '-d', source_config["dbname"],
    '-f', 'data_dump.sql',
    '-w'
}

subprocess_env = dict(PGPASSWORD=source_config['password'])

subprocess.run(dump_command, env=subprocess_env, check=True)

load_command = [
    'psql',
    '-h', destination_config["host"],
    '-u', destination_config["user"],
    '-d', destination_config["dbname"],
    '-a' ,'-f', 'data_dump.sql',
]

subprocess_env = dict(PGPASSWORD=destination_config['password'])

subprocess.run(load_command,env=subprocess_env, check=True)

print("Ending elt")