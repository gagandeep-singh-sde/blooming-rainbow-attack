import bcrypt
import os

PASSWORD_LENGTH = 4
PROCESSOR_CORES = 10
BATCH_SIZE = 1000
FALSE_POSITIVE_RATE = 0.00001  # 0.001%

# Path to the file where the salt is stored
SALT_FILE = "fixed_salt.txt"


# Function to save the salt to a file
def save_salt(salt):
    with open(SALT_FILE, "wb") as f:
        f.write(salt)


# Function to load the salt from a file
def load_salt():
    if os.path.exists(SALT_FILE):
        with open(SALT_FILE, "rb") as f:
            return f.read()
    else:
        return None


# Load the salt if it exists, otherwise generate a new one
fixed_salt = load_salt()
if fixed_salt is None:
    fixed_salt = bcrypt.gensalt(rounds=4)
    save_salt(fixed_salt)
