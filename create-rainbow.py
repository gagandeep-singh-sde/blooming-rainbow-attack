import bcrypt
import psycopg2
import itertools
import string
from multiprocessing import Pool, Manager
import time

# Define character sets
uppercase = string.ascii_uppercase
lowercase = string.ascii_lowercase
digits = "0123456789"
special = "!@#$%^&*"
characters = uppercase + lowercase + digits + special

# Define a fixed salt value
fixed_salt = bcrypt.gensalt(rounds=4)

PASSWORD_LENGTH = 5
PROCESSOR_CORES = 16
MAX_RECORDS = 100000  # Maximum number of records to insert
BATCH_SIZE = 1000  # Number of records to insert in each batch

# PostgreSQL connection settings
db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
    "port": "5432",
}


# PostgreSQL helper functions
def init_db():
    """Initialize the PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dictionary (
                hash TEXT PRIMARY KEY,
                password TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_hash ON dictionary (hash);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_password ON dictionary (password);
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized and table created.")
    except Exception as e:
        print(f"Error initializing database: {e}")


def insert_passwords_to_db(batch, counter, lock):
    """Insert a batch of hash and password pairs into the database."""
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO dictionary (hash, password) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            batch,
        )
        conn.commit()
        cursor.close()
        conn.close()
        with lock:
            counter.value += len(batch)
        print(f"Inserted batch of {len(batch)} records.")
    except Exception as e:
        print(f"Error inserting batch: {e}")


# Helper function to check if the password meets the criteria
def is_valid_password(password):
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    for c in password:
        if c.isupper():
            has_upper = True
        elif c.islower():
            has_lower = True
        elif c.isdigit():
            has_digit = True
        elif c in special:
            has_special = True
        if has_upper and has_lower and has_digit and has_special:
            return True
    return False


# Process password combinations in chunks to avoid high memory usage
def process_chunk(start, end, counter, lock):
    """Generate valid password combinations and hash them for a range."""
    batch = []
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
            # print(f"Hashed: {password} -> {hashed}")

            # Add hash-password pair to the batch
            batch.append((hashed.decode("utf-8"), password))

            # Insert batch into the database when it reaches BATCH_SIZE
            if len(batch) >= BATCH_SIZE:
                insert_passwords_to_db(batch, counter, lock)
                batch = []

            # Check if the maximum number of records has been reached
            with lock:
                if counter.value >= MAX_RECORDS:
                    return

    # Insert any remaining records in the batch
    if batch:
        insert_passwords_to_db(batch, counter, lock)


# Main execution: Split combinations among processes
if __name__ == "__main__":
    start_time = time.time()
    init_db()
    # Get total combinations for 5 characters
    total_combinations = len(characters) ** PASSWORD_LENGTH
    num_chunks = PROCESSOR_CORES  # Number of CPU cores or processes
    chunk_size = total_combinations // num_chunks

    # Create ranges for each chunk
    ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_chunks)]
    # Adjust the last chunk to include any remaining entries
    ranges[-1] = (ranges[-1][0], total_combinations)

    # Shared counter and lock
    with Manager() as manager:
        counter = manager.Value("i", 0)
        lock = manager.Lock()

        # Use multiprocessing to process chunks in parallel
        with Pool(processes=num_chunks) as pool:
            pool.starmap(
                process_chunk, [(start, end, counter, lock) for start, end in ranges]
            )

    print(f"Total combinations: {total_combinations}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Script completed in {elapsed_time:.2f} seconds")
