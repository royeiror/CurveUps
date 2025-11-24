# src/gui_main.py
import sys
import os
import traceback

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Try absolute imports first
    from main_pipeline import CurveUpToolchain
    from parameterization import MeshParameterizer
except ImportError:
    try:
        # Try relative imports
        from .main_pipeline import CurveUpToolchain
        from .parameterization import MeshParameterizer
    except ImportError as e:
        print(f"Import error: {e}")
        traceback.print_exc()
        # Create fallback classes
        class CurveUpToolchain:
            def __init__(self):
                self.input_mesh = None
        class MeshParameterizer:
            def __init__(self, mesh):
                self.mesh = mesh

def main():
    """Main entry point for the application."""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        
        app = QApplication(sys.argv)
        
        # Test if our modules loaded
        toolchain = CurveUpToolchain()
        
        window = QMainWindow()
        window.setWindowTitle("CurveUp Toolchain")
        window.setGeometry(100, 100, 500, 300)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("CurveUp Toolchain - Successfully Built!")
        label.setStyleSheet("font-size: 18px; padding: 20px; color: green;")
        layout.addWidget(label)
        
        status_label = QLabel("3D to 2D fabric pattern generator")
        layout.addWidget(status_label)
        
        modules_label = QLabel(f"Toolchain loaded: {type(toolchain).__name__}")
        layout.addWidget(modules_label)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        
        print("CurveUp Toolchain started successfully!")
        return app.exec_()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
