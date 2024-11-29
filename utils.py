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
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "~!@#$%^&*()_+{}|:\"<>?`-=[]\;',./ " for c in password)
    return has_upper and has_lower and has_digit and has_special


def consistent_hash(item):
    item_bytes = item.encode("utf-8") if isinstance(item, str) else item
    hash_value = hashlib.md5(item_bytes).hexdigest()
    return int(hash_value[:8], 16)
