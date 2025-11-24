# src/gui_main.py
import sys
import os
import traceback

def main():
    """Main entry point for the application."""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        
        # Import toolchain modules with fallback
        try:
            # Try to import our modules
            from main_pipeline import CurveUpToolchain
            from parameterization import MeshParameterizer
            toolchain = CurveUpToolchain()
            modules_loaded = True
            status_text = "✓ All modules loaded successfully!"
            status_color = "green"
        except ImportError as e:
            print(f"Module import error: {e}")
            # Fallback implementation
            class CurveUpToolchain:
                def __init__(self):
                    self.input_mesh = None
                def load_mesh(self, filepath):
                    return f"Would load: {filepath}"
            
            class MeshParameterizer:
                def __init__(self, mesh):
                    self.mesh = mesh
            
            toolchain = CurveUpToolchain()
            modules_loaded = False
            status_text = "⚠ Running in fallback mode (modules not found)"
            status_color = "orange"

        app = QApplication(sys.argv)
        
        # Create main window
        window = QMainWindow()
        window.setWindowTitle("CurveUp Toolchain")
        window.setGeometry(100, 100, 500, 300)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("CurveUp Fabric Pattern Generator")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Status
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; padding: 5px;")
        layout.addWidget(status_label)
        
        # Test functionality
        test_result = toolchain.load_mesh("test.stl")
        test_label = QLabel(f"Test: {test_result}")
        layout.addWidget(test_label)
        
        # Instructions
        instructions = QLabel(
            "Development Build\n"
            "• Load 3D models (STL/OBJ/PLY)\n"  
            "• Generate 2D patterns\n"
            "• Export to DXF/SVG"
        )
        layout.addWidget(instructions)
        
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
