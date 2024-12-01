import psycopg2
import time

db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
    "port": "5432",
}


def get_password_for_hash(given_hash):
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM dictionary WHERE hash = %s", (given_hash,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None


if __name__ == "__main__":
    start_time = time.time()
    given_hash = input("Enter the hash value: ")  # Ask the user for the hash value
    password = get_password_for_hash(given_hash)
    if password:
        print(f"Password for hash {given_hash}: {password}")
    else:
        print(f"Hash {given_hash} not found in the database")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
