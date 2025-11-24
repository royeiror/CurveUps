# src/gui_main.py
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QComboBox, 
                             QDoubleSpinBox, QGroupBox, QTextEdit, QProgressBar,
                             QWidget, QMessageBox)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolchain = None
        self.init_ui()
        self.init_toolchain()
        
    def init_ui(self):
        self.setWindowTitle("CurveUp - 3D to 2D Fabric Pattern Generator")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("CurveUp Fabric Pattern Generator")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #2c3e50;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # File operations
        file_group = QGroupBox("1. Load 3D Model")
        file_layout = QVBoxLayout()
        
        self.btn_load = QPushButton("Load 3D Model (STL/OBJ/PLY)")
        self.btn_load.clicked.connect(self.load_model)
        self.btn_load.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        file_layout.addWidget(self.btn_load)
        
        self.file_label = QLabel("No model loaded")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parameterization settings
        param_group = QGroupBox("2. Parameterization Settings")
        param_layout = QVBoxLayout()
        
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["Conformal", "LSCM"])
        param_layout.addWidget(QLabel("Parameterization Method:"))
        param_layout.addWidget(self.cmb_method)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Fabric properties
        fabric_group = QGroupBox("3. Fabric Properties")
        fabric_layout = QHBoxLayout()
        
        self.spin_stretch_x = QDoubleSpinBox()
        self.spin_stretch_x.setRange(0.1, 3.0)
        self.spin_stretch_x.setValue(1.2)
        self.spin_stretch_x.setSingleStep(0.1)
        fabric_layout.addWidget(QLabel("X Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_x)
        
        self.spin_stretch_y = QDoubleSpinBox()
        self.spin_stretch_y.setRange(0.1, 3.0)
        self.spin_stretch_y.setValue(1.2)
        self.spin_stretch_y.setSingleStep(0.1)
        fabric_layout.addWidget(QLabel("Y Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_y)
        
        fabric_group.setLayout(fabric_layout)
        layout.addWidget(fabric_group)
        
        # Process buttons
        button_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Generate 2D Pattern")
        self.btn_generate.clicked.connect(self.generate_pattern)
        self.btn_generate.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 10px; font-weight: bold; }")
        button_layout.addWidget(self.btn_generate)
        
        self.btn_export = QPushButton("Export Pattern")
        self.btn_export.clicked.connect(self.export_pattern)
        self.btn_export.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 10px; font-weight: bold; }")
        button_layout.addWidget(self.btn_export)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Log output
        self.text_log = QTextEdit()
        self.text_log.setMaximumHeight(150)
        self.text_log.setPlaceholderText("Operation log will appear here...")
        layout.addWidget(QLabel("Operation Log:"))
        layout.addWidget(self.text_log)
        
        central_widget.setLayout(layout)
        
    def init_toolchain(self):
        try:
            from main_pipeline import CurveUpToolchain
            self.toolchain = CurveUpToolchain()
            self.log_message("✓ Toolchain initialized successfully")
        except Exception as e:
            self.log_message(f"✗ Error initializing toolchain: {e}")
            
    def load_model(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open 3D Model", "", 
            "3D Files (*.stl *.obj *.ply *.off);;All Files (*.*)"
        )
        if filepath and self.toolchain:
            try:
                result = self.toolchain.load_mesh(filepath)
                self.file_label.setText(f"Loaded: {os.path.basename(filepath)}")
                self.log_message(f"✓ {result}")
            except Exception as e:
                self.log_message(f"✗ Error loading model: {e}")
                
    def generate_pattern(self):
        if not self.toolchain:
            self.log_message("✗ Toolchain not initialized")
            return
            
        try:
            self.progress.setVisible(True)
            
            # Step 1: Parameterize
            method = self.cmb_method.currentText().lower()
            self.log_message("🔄 Parameterizing mesh...")
            result1 = self.toolchain.parameterize_mesh(method)
            self.log_message(f"✓ {result1}")
            
            # Step 2: Optimize
            stretch_x = self.spin_stretch_x.value()
            stretch_y = self.spin_stretch_y.value()
            self.log_message("🔄 Optimizing pattern...")
            result2 = self.toolchain.optimize_pattern(stretch_x, stretch_y)
            self.log_message(f"✓ {result2}")
            
            self.log_message("🎉 Pattern generation complete!")
            self.progress.setVisible(False)
            
        except Exception as e:
            self.log_message(f"✗ Error generating pattern: {e}")
            self.progress.setVisible(False)
            
    def export_pattern(self):
        if not self.toolchain:
            self.log_message("✗ Toolchain not initialized")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Pattern", "pattern.dxf",
            "DXF Files (*.dxf);;SVG Files (*.svg);;All Files (*.*)"
        )
        if filepath:
            try:
                result = self.toolchain.export_pattern(filepath)
                self.log_message(f"✓ {result}")
                QMessageBox.information(self, "Export Complete", f"Pattern exported to:\n{filepath}")
            except Exception as e:
                self.log_message(f"✗ Error exporting pattern: {e}")
                
    def log_message(self, message):
        self.text_log.append(message)
        # Auto-scroll to bottom
        self.text_log.verticalScrollBar().setValue(self.text_log.verticalScrollBar().maximum())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
