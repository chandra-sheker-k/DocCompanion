
import hashlib

def calculate_checksum(file):
    sha = hashlib.sha256()
    for chunk in file.chunks():
        sha.update(chunk)
    file.seek(0)
    return sha.hexdigest()