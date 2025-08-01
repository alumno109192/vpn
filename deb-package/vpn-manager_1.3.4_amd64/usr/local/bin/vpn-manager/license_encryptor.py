import os
from pathlib import Path

from cryptography.fernet import Fernet


class LicenseEncryptor:
    def __init__(self, key_path='license.key', enc_path='license.json.enc', dec_path='license.json'):
        self.key_path = key_path
        self.enc_path = enc_path
        self.dec_path = dec_path
        self._key = None
        self._fernet = None

    @property
    def key(self):
        if self._key is None:
            self._key = self.load_or_create_key()
        return self._key

    @property
    def fernet(self):
        if self._fernet is None:
            self._fernet = Fernet(self.key)
        return self._fernet

    def load_or_create_key(self):
        # Create parent directory if it doesn't exist
        key_dir = Path(self.key_path).parent
        key_dir.mkdir(parents=True, exist_ok=True)

        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as f:
            f.write(key)
        return key

    def encrypt_file(self):
        with open(self.dec_path, 'rb') as f:
            data = f.read()
        encrypted = self.fernet.encrypt(data)
        with open(self.enc_path, 'wb') as f:
            f.write(encrypted)
        os.remove(self.dec_path)

    def decrypt_file(self):
        with open(self.enc_path, 'rb') as f:
            encrypted = f.read()
        decrypted = self.fernet.decrypt(encrypted)
        with open(self.dec_path, 'wb') as f:
            f.write(decrypted)

    def read_license(self):
        self.decrypt_file()
        with open(self.dec_path, 'r') as f:
            content = f.read()
        self.encrypt_file()
        return content

    def write_license(self, content):
        with open(self.dec_path, 'w') as f:
            f.write(content)
        self.encrypt_file()
