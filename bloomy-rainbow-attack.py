import bcrypt
from rbloom import Bloom
import itertools
from utils import get_character_set, is_valid_password, consistent_hash
from multiprocessing import Pool
import time
from constants import (
    PASSWORD_LENGTH,
    PROCESSOR_CORES,
    BATCH_SIZE,
    FALSE_POSITIVE_RATE,
    fixed_salt,
)

characters = get_character_set()


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
    total_combinations = len(characters) ** PASSWORD_LENGTH
    num_bloom_filters = (total_combinations + BATCH_SIZE - 1) // BATCH_SIZE
    found_indices = find_hash_in_bloom_filters(given_hash, num_bloom_filters)
    passwords = []
    if found_indices:
        for index in found_indices:
            start = index * BATCH_SIZE
            end = min((index + 1) * BATCH_SIZE, total_combinations)
            for i, password_tuple in enumerate(
                itertools.product(characters, repeat=PASSWORD_LENGTH)
            ):
                if i < start:
                    continue
                if i >= end:
                    break
                password = "".join(password_tuple)
                if is_valid_password(password):
                    password_bytes = password.encode("utf-8")
                    hashed = bcrypt.hashpw(password_bytes, fixed_salt).decode("utf-8")
                    if hashed == given_hash:
                        passwords.append(password)
    return passwords


if __name__ == "__main__":
    start_time = time.time()
    given_hash = input("Enter the hash value: ")  # 5C
    passwords = get_passwords_for_hash(given_hash)
    if passwords:
        for password in passwords:
            print(f"Password for hash {given_hash}: {password}")
    else:
        print(f"Hash {given_hash} not found in any Bloom filter")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
