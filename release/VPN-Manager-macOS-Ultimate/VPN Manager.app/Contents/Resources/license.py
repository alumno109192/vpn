import base64
import hashlib


class LicenseManager:
    SECRET = 'TuClaveSecretaFija'  # Cambia esto por una clave secreta fuerte

    @staticmethod
    def generate_license_key(user_email):
        raw = f"{user_email}:{LicenseManager.SECRET}"
        digest = hashlib.sha256(raw.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode()

    @staticmethod
    def validate_license_key(user_email, license_key):
        expected = LicenseManager.generate_license_key(user_email)
        return license_key == expected
