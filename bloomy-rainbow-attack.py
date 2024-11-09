from rbloom import Bloom
from utils import consistent_hash
from multiprocessing import Pool
import psycopg2

db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
    "port": "5432",
}

PROCESSOR_CORES = 10


def find_hash_in_bloom_filter(args):
    index, given_hash = args
    try:
        bloom_filter = Bloom.load(
            f"bloom_filter_{index}.bloom", hash_func=consistent_hash
        )
        if given_hash in bloom_filter:
            return index
    except FileNotFoundError:
        return None
    return None


def find_hash_in_bloom_filters(given_hash):
    found_indices = []
    with Pool(PROCESSOR_CORES) as pool:
        results = pool.map(
            find_hash_in_bloom_filter, [(i, given_hash) for i in range(21000)]
        )
        found_indices = [index for index in results if index is not None]
    return found_indices


def get_passwords_for_hash(given_hash):
    found_indices = find_hash_in_bloom_filters(given_hash)
    passwords = []
    if found_indices:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        for index in found_indices:
            offset = index * 1000
            cursor.execute(
                "SELECT password FROM dictionary WHERE hash = %s LIMIT 1000 OFFSET %s",
                (given_hash, offset),
            )
            result = cursor.fetchone()
            if result:
                passwords.append(result[0])
        cursor.close()
        conn.close()
    return passwords


if __name__ == "__main__":
    given_hash = "$2b$04$zWePqYXlJt.dnw.PKL0WY.ucxi/791EX.5ztvhQ..QtQUg.KqlgcO"  # xA
    passwords = get_passwords_for_hash(given_hash)
    if passwords:
        for password in passwords:
            print(f"Password for hash {given_hash}: {password}")
    else:
        print(f"Hash {given_hash} not found in any Bloom filter")
