import base64
import hashlib
import sys

from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget


class LicenseKeyGenerator:
    SECRET = 'TuClaveSecretaFija'  # Usa la misma clave que en la app principal

    @staticmethod
    def generate_license_key(user_email):
        raw = f"{user_email}:{LicenseKeyGenerator.SECRET}"
        digest = hashlib.sha256(raw.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode()


class LicenseGeneratorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Serial para VPN")
        self.setGeometry(200, 200, 400, 180)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Introduce el email:"))
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)
        self.generate_button = QPushButton("Generar Serial")
        self.generate_button.clicked.connect(self.generate_serial)
        layout.addWidget(self.generate_button)
        self.serial_label = QLabel("")
        layout.addWidget(self.serial_label)
        self.copy_button = QPushButton("Copiar Serial al portapapeles")
        self.copy_button.clicked.connect(self.copy_serial)
        self.copy_button.setEnabled(False)
        layout.addWidget(self.copy_button)
        self.setLayout(layout)

    def generate_serial(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Error", "Introduce un email válido.")
            self.copy_button.setEnabled(False)
            self.serial_label.setText("")
            return
        serial = LicenseKeyGenerator.generate_license_key(email)
        self.serial_label.setText(f"Serial:\n{serial}")
        self.copy_button.setEnabled(True)

    def copy_serial(self):
        serial = self.serial_label.text().replace("Serial:\n", "").strip()
        if serial:
            clipboard = QApplication.clipboard()
            clipboard.setText(serial)
            QMessageBox.information(self, "Copiado", "Serial copiado al portapapeles.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LicenseGeneratorWindow()
    window.show()
    sys.exit(app.exec_())
