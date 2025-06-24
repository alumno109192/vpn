import os
from cryptography.fernet import Fernet

class LicenseEncryptor:
    def __init__(self, key_path='license.key', enc_path='license.json.enc', dec_path='license.json'):
        self.key_path = key_path
        self.enc_path = enc_path
        self.dec_path = dec_path
        self.key = self.load_or_create_key()
        self.fernet = Fernet(self.key)

    def load_or_create_key(self):
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
