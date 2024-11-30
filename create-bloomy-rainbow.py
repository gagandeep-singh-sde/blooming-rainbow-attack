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
    FALSE_POSITIVE_RATE,
    fixed_salt,
)

# Define character sets
characters = get_character_set()


# Process password combinations in chunks to avoid high memory usage
def process_chunk(start, end, chunk_index):
    start_time = time.time()
    """Generate valid password combinations and hash them for a range."""
    bloom_filter = Bloom(
        expected_items=BATCH_SIZE,
        false_positive_rate=FALSE_POSITIVE_RATE,
        hash_func=consistent_hash,
    )
    count = 0
    # Generate only passwords within the specific range
    for i, password_tuple in enumerate(
        itertools.product(characters, repeat=PASSWORD_LENGTH)
    ):
        if i < start:
            continue
        if i >= end:
            break
        password = "".join(password_tuple)

        # Filter by required criteria
        if is_valid_password(password):
            password_bytes = password.encode("utf-8")

            # Hash with bcrypt using the fixed salt
            hashed = bcrypt.hashpw(password_bytes, fixed_salt)
            # print(f"Password: {password}, Hash: {hashed.decode('utf-8')}")

            # Add hash to Bloom filter
            bloom_filter.add(hashed.decode("utf-8"))
            count += 1
            if count >= BATCH_SIZE:
                break
    bloom_filter.save(f"bloom_filters/bloom_filter_{chunk_index}.bloom")
    print(f"\nBloom filter for chunk {chunk_index} created and saved.\n")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Chunk {chunk_index} completed in {elapsed_time:.4f} seconds")


# Main execution: Split combinations among processes
if __name__ == "__main__":
    start_time = time.time()
    total_combinations = 10000000
    # total_combinations = len(characters) ** PASSWORD_LENGTH
    num_chunks = (total_combinations + BATCH_SIZE - 1) // BATCH_SIZE

    # Create ranges for each chunk
    ranges = [
        (i * BATCH_SIZE, min((i + 1) * BATCH_SIZE, total_combinations), i)
        for i in range(num_chunks)
    ]

    # Use multiprocessing to process chunks in parallel
    with Pool(processes=PROCESSOR_CORES) as pool:
        pool.starmap(process_chunk, ranges)

    print(f"Total combinations: {total_combinations}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
