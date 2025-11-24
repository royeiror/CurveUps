import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

def main():
    try:
        # Try to import our modules
        try:
            from main_pipeline import CurveUpToolchain
            from parameterization import MeshParameterizer
            modules_loaded = True
            status_text = "✓ All modules loaded successfully!"
            status_color = "green"
        except ImportError:
            modules_loaded = False
            status_text = "⚠ Running in fallback mode"
            status_color = "orange"

        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("CurveUp Toolchain")
        window.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        header = QLabel("CurveUp Toolchain")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; padding: 5px;")
        layout.addWidget(status_label)
        
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        window.show()
        return app.exec_()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
