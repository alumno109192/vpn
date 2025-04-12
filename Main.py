import sys
from PyQt5.QtWidgets import QApplication, QDialog  # Added QDialog import
from main_window import MainWindow
from setup_window import SetupWindow

def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        
        # Show setup window first
        setup_window = SetupWindow()
        result = setup_window.exec_()
        
        if result == QDialog.Accepted:
            # Setup successful, show main window
            window = MainWindow()
            window.show()
            return app.exec_()
        else:
            # Setup failed
            return 1
        
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())