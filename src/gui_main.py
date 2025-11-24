# src/gui_main.py
import sys
import os
import traceback

def main():
    """Main entry point for the application."""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        
        # Import our modules - now they're proper packages
        try:
            from main_pipeline import CurveUpToolchain
            from parameterization import MeshParameterizer
            toolchain_available = True
            print("✓ All modules imported successfully!")
        except ImportError as e:
            print(f"Import error: {e}")
            traceback.print_exc()
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
        
        # Test toolchain functionality
        if toolchain_available:
            try:
                toolchain = CurveUpToolchain()
                test_result = toolchain.load_mesh("test.stl")
                test_label = QLabel("✓ Toolchain initialized and working!")
                test_label.setStyleSheet("color: green;")
            except Exception as e:
                test_label = QLabel(f"✗ Toolchain error: {e}")
                test_label.setStyleSheet("color: red;")
        else:
            test_label = QLabel("⚠ Toolchain modules not found")
            test_label.setStyleSheet("color: orange;")
        
        layout.addWidget(test_label)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        
        print("Application started successfully!")
        return app.exec_()
        
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
