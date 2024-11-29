import string
import hashlib


def get_character_set():
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = "0123456789"
    special = "~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',./ "
    characters = uppercase + lowercase + digits + special
    return characters


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
        elif c in "~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',./ ":
            has_special = True
        if has_upper and has_lower and has_digit and has_special:
            return True
    return False


def consistent_hash(item):
    item_bytes = item.encode("utf-8") if isinstance(item, str) else item
    hash_value = hashlib.md5(item_bytes).hexdigest()
    return int(hash_value[:8], 16)
