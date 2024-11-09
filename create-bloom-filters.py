import psycopg2
from multiprocessing import Pool
import time
from rbloom import Bloom
from utils import consistent_hash

db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
    "port": "5432",
}

PROCESSOR_CORES = 10
BATCH_SIZE = 1000
FALSE_POSITIVE_RATE = 0.00001  # 0.001%


def process_batch(offset):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT hash FROM dictionary LIMIT %s OFFSET %s", (BATCH_SIZE, offset)
        )
        hashes = cursor.fetchall()
        cursor.close()
        conn.close()

        bloom_filter = Bloom(
            expected_items=BATCH_SIZE,
            false_positive_rate=FALSE_POSITIVE_RATE,
            hash_func=consistent_hash,
        )
        for hash_value in hashes:
            bloom_filter.add(hash_value[0])
        bloom_filter.save(f"bloom_filters/bloom_filter_{offset // BATCH_SIZE}.bloom")
        print(f"Bloom filter for batch {offset // BATCH_SIZE} created and saved.")
    except Exception as e:
        print(f"Error processing batch {offset // BATCH_SIZE}: {e}")


def create_bloom_filters():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dictionary")
        total_entries = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"Total entries in dictionary: {total_entries}")

        offsets = range(0, total_entries, BATCH_SIZE)
        with Pool(PROCESSOR_CORES) as pool:
            pool.map(process_batch, offsets)

        print("All Bloom filters created and saved to files.")
    except Exception as e:
        print(f"Error creating Bloom filters: {e}")


if __name__ == "__main__":
    start_time = time.time()
    create_bloom_filters()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
