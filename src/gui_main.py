# src/gui_main.py
import sys
import os
import traceback

# Add the current directory to sys.path for PyInstaller
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

def main():
    """Main entry point for the application."""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        
        # Import our modules with proper error handling
        try:
            # These should work in both development and compiled mode
            import main_pipeline
            import parameterization
            from main_pipeline import CurveUpToolchain
            toolchain_available = True
        except ImportError as e:
            print(f"Import error: {e}")
            toolchain_available = False
            # Create minimal fallback
            class CurveUpToolchain:
                def __init__(self):
                    self.input_mesh = None
                    self.status = "Toolchain unavailable"
        
        app = QApplication(sys.argv)
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("CurveUp Toolchain")
        window.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Status information
        status_label = QLabel("CurveUp Toolchain - Running")
        status_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(status_label)
        
        toolchain_status = QLabel(f"Toolchain available: {toolchain_available}")
        layout.addWidget(toolchain_status)
        
        # Add some basic functionality test
        if toolchain_available:
            try:
                toolchain = CurveUpToolchain()
                test_label = QLabel("✓ Toolchain initialized successfully")
                test_label.setStyleSheet("color: green;")
            except Exception as e:
                test_label = QLabel(f"✗ Toolchain error: {e}")
                test_label.setStyleSheet("color: red;")
        else:
            test_label = QLabel("⚠ Toolchain modules not found")
            test_label.setStyleSheet("color: orange;")
        
        layout.addWidget(test_label)
        
        # Instructions
        instructions = QLabel(
            "Next steps:\n"
            "1. Implement mesh loading\n"
            "2. Add parameterization algorithms\n"
            "3. Create pattern export functionality"
        )
        layout.addWidget(instructions)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        
        print("Application started successfully!")
        if not toolchain_available:
            print("Warning: Toolchain modules not loaded")
        
        return app.exec_()
        
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
