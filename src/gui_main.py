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
        self.setWindowTitle("CurveUp - 3D Printing Pattern Generator for Stretched Fabric")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("CurveUp - 3D Printing on Stretched Fabric")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #2c3e50;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # File operations
        file_group = QGroupBox("1. Load Target 3D Shape")
        file_layout = QVBoxLayout()
        
        self.btn_load = QPushButton("Load 3D Shape (OBJ/STL)")
        self.btn_load.clicked.connect(self.load_model)
        self.btn_load.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        file_layout.addWidget(self.btn_load)
        
        self.file_label = QLabel("No shape loaded")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Curve settings
        curve_group = QGroupBox("2. Curve Settings")
        curve_layout = QVBoxLayout()
        
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["Auto Curvature", "Manual Placement"])
        curve_layout.addWidget(QLabel("Curve Generation:"))
        curve_layout.addWidget(self.cmb_method)
        
        curve_group.setLayout(curve_layout)
        layout.addWidget(curve_group)
        
        # Fabric properties
        fabric_group = QGroupBox("3. Fabric Stretch Properties")
        fabric_layout = QHBoxLayout()
        
        self.spin_stretch_x = QDoubleSpinBox()
        self.spin_stretch_x.setRange(1.0, 3.0)
        self.spin_stretch_x.setValue(1.5)
        self.spin_stretch_x.setSingleStep(0.1)
        fabric_layout.addWidget(QLabel("X Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_x)
        
        self.spin_stretch_y = QDoubleSpinBox()
        self.spin_stretch_y.setRange(1.0, 3.0)
        self.spin_stretch_y.setValue(1.5)
        self.spin_stretch_y.setSingleStep(0.1)
        fabric_layout.addWidget(QLabel("Y Stretch:"))
        fabric_layout.addWidget(self.spin_stretch_y)
        
        fabric_group.setLayout(fabric_layout)
        layout.addWidget(fabric_group)
        
        # Process buttons
        button_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("Compute Adaptive Triangles")
        self.btn_generate.clicked.connect(self.generate_pattern)
        self.btn_generate.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 10px; font-weight: bold; }")
        button_layout.addWidget(self.btn_generate)
        
        self.btn_export = QPushButton("Export Triangle Mesh")
        self.btn_export.clicked.connect(self.export_pattern)
        self.btn_export.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 10px; font-weight: bold; }")
        self.btn_export.setEnabled(False)
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
            self, "Open 3D Shape", "", 
            "3D Files (*.obj *.stl *.ply);;All Files (*.*)"
        )
        if filepath and self.toolchain:
            try:
                result = self.toolchain.load_mesh(filepath)
                self.file_label.setText(f"Loaded: {os.path.basename(filepath)}")
                self.log_message(f"✓ {result}")
            except Exception as e:
                self.log_message(f"✗ Error loading shape: {e}")
                
    def generate_pattern(self):
        if not self.toolchain:
            self.log_message("✗ Toolchain not initialized")
            return
            
        try:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            
            # Step 1: Compute optimal curves for 3D printing
            stretch_x = self.spin_stretch_x.value()
            stretch_y = self.spin_stretch_y.value()
            self.log_message("🔄 Computing optimal curves...")
            self.progress.setValue(50)
            
            result = self.toolchain.compute_optimal_curves(stretch_x, stretch_y)
            self.log_message(f"✓ {result}")
            
            self.progress.setValue(100)
            self.log_message("🎉 Curve computation complete!")
            
            # Enable export button if successful
            if "✓" in result:
                self.btn_export.setEnabled(True)
            
        except Exception as e:
            self.log_message(f"✗ Error computing curves: {e}")
        finally:
            self.progress.setVisible(False)
            
    def export_pattern(self):
        if not self.toolchain:
            self.log_message("✗ Toolchain not initialized")
            return
            
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Printing Pattern", "curveup_pattern",
            "SVG Files (*.svg);;All Files (*.*)"
        )
        
        if filepath:
            try:
                # Ensure correct file extension
                if selected_filter == "SVG Files (*.svg)" and not filepath.endswith('.svg'):
                    filepath += '.svg'
                    
                result = self.toolchain.export_print_pattern(filepath)
                self.log_message(f"✓ {result}")
                
                # Show success message
                QMessageBox.information(self, "Export Complete", 
                                      f"Printing pattern successfully exported!\n\n"
                                      f"File: {filepath}\n"
                                      f"Stretch Factors: {self.spin_stretch_x.value():.1f}x{self.spin_stretch_y.value():.1f}")
                
            except Exception as e:
                self.log_message(f"✗ Error exporting pattern: {e}")
                QMessageBox.critical(self, "Export Error", f"Failed to export pattern:\n{str(e)}")
                
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
