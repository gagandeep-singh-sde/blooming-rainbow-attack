import bcrypt
from constants import fixed_salt


def generate_bcrypt_hash(password):
    # Generate the bcrypt hash using the fixed salt
    bcrypt_hash = bcrypt.hashpw(password.encode("utf-8"), fixed_salt)
    return bcrypt_hash


if __name__ == "__main__":
    # Take a 5-character password from the user
    password = input("Enter a 5-character password: ")
    if len(password) != 5:
        print("Password must be exactly 5 characters long.")
    else:
        # Generate the bcrypt hash
        bcrypt_hash = generate_bcrypt_hash(password)
        print(
            f"Bcrypt hash for the password '{password}': {bcrypt_hash.decode('utf-8')}"
        )
