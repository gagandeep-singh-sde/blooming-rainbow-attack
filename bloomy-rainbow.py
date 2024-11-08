import bcrypt
import psycopg2
import itertools
import string
import os
from multiprocessing import Pool

# Define character sets
uppercase = string.ascii_uppercase
lowercase = string.ascii_lowercase
digits = "0123456789"
special = "!@#$%^&*"
characters = uppercase + lowercase + digits + special

# Define a fixed salt value
fixed_salt = b"$2b$04$FixedSaltForDemoTool123456"

# PostgreSQL connection settings
db_config = {
    "dbname": "bloomy_rainbow_table",
    "user": "gagandeepsinghlotey",
    "password": "Qwerty@123",
    "host": "localhost",
}


# PostgreSQL helper functions
def init_db():
    """Initialize the PostgreSQL database connection."""
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


def insert_password_to_db(password, hashed):
    """Insert hash and password pair into the database."""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO dictionary (hash, password) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (hashed.decode("utf-8"), password),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# Helper function to check if the password meets the criteria
def is_valid_password(password):
    has_upper = any(c in uppercase for c in password)
    has_lower = any(c in lowercase for c in password)
    has_digit = any(c in digits for c in password)
    has_special = any(c in special for c in password)
    return has_upper and has_lower and has_digit and has_special


# Process password combinations in chunks to avoid high memory usage
def process_chunk(start, end):
    """Generate valid password combinations and hash them for a range."""
    # Generate only passwords within the specific range
    for i, password_tuple in enumerate(itertools.product(characters, repeat=5)):
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

            # Store hash-password pair in the database
            insert_password_to_db(password, hashed)


# Main execution: Split combinations among processes
if __name__ == "__main__":
    init_db()
    # Get total combinations for 5 characters
    total_combinations = len(characters) ** 5
    num_chunks = 8  # Number of CPU cores or processes
    chunk_size = total_combinations // num_chunks

    # Use multiprocessing to process chunks in parallel
    with Pool(processes=num_chunks) as pool:
        pool.starmap(
            process_chunk,
            [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_chunks)],
        )
