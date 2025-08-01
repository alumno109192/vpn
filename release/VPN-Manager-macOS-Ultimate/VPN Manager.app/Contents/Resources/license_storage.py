import datetime
import json
from pathlib import Path

from license_encryptor import LicenseEncryptor


class LicenseStorage:
    CONFIG_DIR = Path.home() / '.config' / 'vpn_manager'
    LICENSE_FILE = CONFIG_DIR / 'license.json'
    ENCRYPTED_FILE = CONFIG_DIR / 'license.json.enc'
    KEY_FILE = CONFIG_DIR / 'license.key'
    TRIAL_DAYS = 7  # Cambiado a 7 días
    LICENSE_DAYS = 30  # Validez de la licencia en días
    _encryptor = LicenseEncryptor(key_path=str(KEY_FILE), enc_path=str(ENCRYPTED_FILE), dec_path=str(LICENSE_FILE))

    @staticmethod
    def load():
        if not LicenseStorage.ENCRYPTED_FILE.exists():
            return None
        try:
            LicenseStorage._encryptor.decrypt_file()
            with open(LicenseStorage.LICENSE_FILE, 'r') as f:
                data = json.load(f)
            LicenseStorage._encryptor.encrypt_file()
            return data
        except Exception:
            return None

    @staticmethod
    def save(email=None, serial=None, trial_start=None, license_start=None, remove_trial=False):
        LicenseStorage.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = LicenseStorage.load() or {}
        if email is not None:
            data['email'] = email
        if serial is not None:
            data['serial'] = serial
        if trial_start is not None:
            data['trial_start'] = trial_start
        if license_start is not None:
            data['license_start'] = license_start
        if remove_trial and 'trial_start' in data:
            del data['trial_start']
        with open(LicenseStorage.LICENSE_FILE, 'w') as f:
            json.dump(data, f)
        LicenseStorage._encryptor.encrypt_file()

    @staticmethod
    def get_email():
        data = LicenseStorage.load()
        return data.get('email') if data else None

    @staticmethod
    def get_serial():
        data = LicenseStorage.load()
        return data.get('serial') if data else None

    @staticmethod
    def get_trial_start():
        data = LicenseStorage.load()
        return data.get('trial_start') if data else None

    @staticmethod
    def get_license_start():
        data = LicenseStorage.load()
        return data.get('license_start') if data else None

    @staticmethod
    def is_trial_valid():
        data = LicenseStorage.load()
        if not data or not data.get('trial_start'):
            return False
        try:
            start = datetime.datetime.fromisoformat(data['trial_start'])
            now = datetime.datetime.now()
            return (now - start).days < LicenseStorage.TRIAL_DAYS
        except Exception:
            return False

    @staticmethod
    def start_trial():
        now = datetime.datetime.now().isoformat()
        LicenseStorage.save(trial_start=now)

    @staticmethod
    def is_license_valid():
        data = LicenseStorage.load()
        if not data or not data.get('license_start'):
            return False
        try:
            start = datetime.datetime.fromisoformat(data['license_start'])
            now = datetime.datetime.now()
            return (now - start).days < LicenseStorage.LICENSE_DAYS
        except Exception:
            return False

    @staticmethod
    def activate_license(email, serial):
        now = datetime.datetime.now().isoformat()
        LicenseStorage.save(email=email, serial=serial, license_start=now)
