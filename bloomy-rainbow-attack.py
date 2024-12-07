import bcrypt
import itertools
from multiprocessing import Pool
import time
from rbloom import Bloom
from utils import get_character_set, is_valid_password, consistent_hash
from constants import (
    PASSWORD_LENGTH,
    PROCESSOR_CORES,
    BATCH_SIZE,
    fixed_salt,
)

characters = get_character_set()


def find_hash_in_bloom_filter(args):
    index, given_hash = args
    try:
        print(f"Checking in Magic Box {index}")
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


def process_chunk(start, end, given_hash):
    passwords = []
    batch_size = BATCH_SIZE // 10
    for batch_start in range(start, end, batch_size):
        batch_end = min(batch_start + batch_size, end)
        for i, password_tuple in enumerate(
            itertools.product(characters, repeat=PASSWORD_LENGTH)
        ):
            if i < batch_start:
                continue
            if i >= batch_end:
                break
            password = "".join(password_tuple)
            if is_valid_password(password):
                password_bytes = password.encode("utf-8")
                hashed = bcrypt.hashpw(password_bytes, fixed_salt).decode("utf-8")
                if hashed == given_hash:
                    passwords.append(password)
    return passwords


def get_passwords_for_hash(given_hash):
    total_combinations = len(characters) ** PASSWORD_LENGTH
    num_bloom_filters = (total_combinations + BATCH_SIZE - 1) // BATCH_SIZE
    found_indices = find_hash_in_bloom_filters(given_hash, num_bloom_filters)
    passwords = []
    if found_indices:
        ranges = [
            (
                index * BATCH_SIZE,
                min((index + 1) * BATCH_SIZE, total_combinations),
                given_hash,
            )
            for index in found_indices
        ]
        # Flatten the ranges to distribute the work more evenly
        flat_ranges = []
        for start, end, given_hash in ranges:
            chunk_size = (end - start) // 10
            for i in range(10):
                chunk_start = start + i * chunk_size
                chunk_end = start + (i + 1) * chunk_size if i < 9 else end
                flat_ranges.append((chunk_start, chunk_end, given_hash))

        with Pool(PROCESSOR_CORES) as pool:
            results = pool.starmap(process_chunk, flat_ranges)
            for result in results:
                passwords.extend(result)
    return passwords


if __name__ == "__main__":
    given_hash = input("Enter the hash value: ")
    start_time = time.time()
    passwords = get_passwords_for_hash(given_hash)
    if passwords:
        for password in passwords:
            print(f"Password for hash {given_hash}: {password}")
    else:
        print(f"Hash {given_hash} not found in any Bloom filter")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
