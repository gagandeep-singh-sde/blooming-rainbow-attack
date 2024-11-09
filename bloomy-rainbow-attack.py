from rbloom import Bloom
from utils import consistent_hash
from multiprocessing import Pool
import psycopg2
import time

db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
    "port": "5432",
}

PROCESSOR_CORES = 10
BATCH_SIZE = 1000


def get_total_entries():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    total_entries = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_entries


def find_hash_in_bloom_filter(args):
    index, given_hash = args
    try:
        bloom_filter = Bloom.load(
            f"bloom_filters/bloom_filter_{index}.bloom", hash_func=consistent_hash
        )
        if given_hash in bloom_filter:
            return index
    except FileNotFoundError:
        return None
    return None


def find_hash_in_bloom_filters(given_hash, num_bloom_filters):
    found_indices = []
    with Pool(PROCESSOR_CORES) as pool:
        results = pool.map(
            find_hash_in_bloom_filter,
            [(i, given_hash) for i in range(num_bloom_filters)],
        )
        found_indices = [index for index in results if index is not None]
    return found_indices


def get_passwords_for_hash(given_hash):
    total_entries = get_total_entries()
    num_bloom_filters = (total_entries + BATCH_SIZE - 1) // BATCH_SIZE
    found_indices = find_hash_in_bloom_filters(given_hash, num_bloom_filters)
    passwords = []
    if found_indices:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        for index in found_indices:
            offset = index * BATCH_SIZE
            cursor.execute(
                "SELECT password FROM dictionary WHERE hash = %s LIMIT %s OFFSET %s",
                (given_hash, BATCH_SIZE, offset),
            )
            result = cursor.fetchone()
            if result:
                passwords.append(result[0])
        cursor.close()
        conn.close()
    return passwords


if __name__ == "__main__":
    start_time = time.time()
    given_hash = "$2b$04$TZPA01nhJXLQvYQx/wPXHe2DKYhdkSM0P.NWAnTL3hF6iYGwnUWWC"  # $V
    passwords = get_passwords_for_hash(given_hash)
    if passwords:
        for password in passwords:
            print(f"Password for hash {given_hash}: {password}")
    else:
        print(f"Hash {given_hash} not found in any Bloom filter")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
