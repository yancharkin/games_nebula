import hashlib

def md5generator(file_path):
    """Generate MD5 checksum."""
    md5 = hashlib.md5()
    chunk_size = 4096
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()
