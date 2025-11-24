# src/gui_main.py - Enhanced version
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QComboBox, 
                             QDoubleSpinBox, QGroupBox, QTextEdit, QProgressBar)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolchain = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CurveUp Toolchain - 3D to 2D Pattern Generator")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        from PyQt5.QtWidgets import QWidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("CurveUp Fabric Pattern Generator")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # File operations
        file_group = QGroupBox("3D Model Input")
        file_layout = QVBoxLayout()
        
        self.btn_load = QPushButton("Load 3D Model (STL/OBJ/PLY)")
        self.btn_load.clicked.connect(self.load_model)
        file_layout.addWidget(self.btn_load)
        
        self.file_label = QLabel("No model loaded")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parameterization settings
        param_group = QGroupBox("Parameterization Settings")
        param_layout = QVBoxLayout()
        
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["Conformal", "LSCM", "ARAP"])
        param_layout.addWidget(QLabel("Parameterization Method:"))
        param_layout.addWidget(self.cmb_method)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Fabric properties
        fabric_group = QGroupBox("Fabric Properties")
        fabric_layout = QHBoxLayout()
        
        self.spin_stretch_x = QDoubleSpinBox()
        self.spin_stretch_x.setRange(0.1, 3.0)
        self.spin_stretch_x.setValue(1.2)
        fabric_layout.addWidget(QLabel("X Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_x)
        
        self.spin_stretch_y = QDoubleSpinBox()
        self.spin_stretch_y.setRange(0.1, 3.0)
        self.spin_stretch_y.setValue(1.2)
        fabric_layout.addWidget(QLabel("Y Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_y)
        
        fabric_group.setLayout(fabric_layout)
        layout.addWidget(fabric_group)
        
        # Process buttons
        self.btn_generate = QPushButton("Generate 2D Pattern")
        self.btn_generate.clicked.connect(self.generate_pattern)
        layout.addWidget(self.btn_generate)
        
        self.btn_export = QPushButton("Export Pattern (DXF/SVG)")
        self.btn_export.clicked.connect(self.export_pattern)
        layout.addWidget(self.btn_export)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Log output
        self.text_log = QTextEdit()
        self.text_log.setMaximumHeight(150)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.text_log)
        
        central_widget.setLayout(layout)
        
        # Initialize toolchain
        self.init_toolchain()
        
    def init_toolchain(self):
        try:
            from main_pipeline import CurveUpToolchain
            self.toolchain = CurveUpToolchain()
            self.log_message("Toolchain initialized successfully")
        except Exception as e:
            self.log_message(f"Error initializing toolchain: {e}")
            
    def load_model(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open 3D Model", "", 
            "3D Files (*.stl *.obj *.ply *.off)"
        )
        if filepath and self.toolchain:
            try:
                if self.toolchain.load_mesh(filepath):
                    self.file_label.setText(f"Loaded: {os.path.basename(filepath)}")
                    self.log_message(f"Successfully loaded: {filepath}")
                else:
                    self.log_message("Failed to load model")
            except Exception as e:
                self.log_message(f"Error loading model: {e}")
                
    def generate_pattern(self):
        if not self.toolchain:
            self.log_message("Toolchain not initialized")
            return
            
        try:
            self.progress.setVisible(True)
            method = self.cmb_method.currentText().lower()
            stretch_factors = (self.spin_stretch_x.value(), self.spin_stretch_y.value())
            
            self.log_message("Starting parameterization...")
            self.toolchain.parameterize_mesh(method)
            
            self.log_message("Optimizing pattern...")
            self.toolchain.optimize_pattern(stretch_factors)
            
            self.log_message("Pattern generation complete!")
            self.progress.setVisible(False)
            
        except Exception as e:
            self.log_message(f"Error generating pattern: {e}")
            self.progress.setVisible(False)
            
    def export_pattern(self):
        if not self.toolchain:
            self.log_message("Toolchain not initialized")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Pattern", "",
            "DXF Files (*.dxf);;SVG Files (*.svg)"
        )
        if filepath:
            try:
                if self.toolchain.export_pattern(filepath):
                    self.log_message(f"Pattern exported to: {filepath}")
                else:
                    self.log_message("Export failed")
            except Exception as e:
                self.log_message(f"Error exporting pattern: {e}")
                
    def log_message(self, message):
        self.text_log.append(message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
