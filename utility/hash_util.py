import hashlib as hl
import json


def hash_string_512(string):

    return hl.sha512(string).hexdigest()


def hash_block(block):

    return hash_string_512(json.dumps(block, sort_keys=True).encode())
