import hashlib


def consistent_hash(item):
    item_bytes = item.encode("utf-8") if isinstance(item, str) else item
    hash_value = hashlib.md5(item_bytes).hexdigest()
    return int(hash_value[:8], 16)
