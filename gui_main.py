# gui_main.py - PyQt5 based GUI
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, 
                             QFileDialog, QComboBox, QDoubleSpinBox,
                             QSlider, QGroupBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt
import pyvistaqt as pvqt
from main_pipeline import CurveUpToolchain

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toolchain = CurveUpToolchain()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CurveUp Fabric Pattern Generator")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        central_widget.addWidget(left_panel)
        
        # Right panel - 3D/2D visualization
        right_panel = self.create_visualization_panel()
        central_widget.addWidget(right_panel)
        
        central_widget.setSizes([400, 1000])
        self.setCentralWidget(central_widget)
        
    def create_control_panel(self):
        panel = QGroupBox("Controls")
        layout = QVBoxLayout()
        
        # File operations
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        
        self.btn_load = QPushButton("Load 3D Model")
        self.btn_load.clicked.connect(self.load_model)
        file_layout.addWidget(self.btn_load)
        
        self.btn_export = QPushButton("Export Pattern")
        self.btn_export.clicked.connect(self.export_pattern)
        file_layout.addWidget(self.btn_export)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parameterization settings
        param_group = QGroupBox("Parameterization Settings")
        param_layout = QVBoxLayout()
        
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["Conformal", "LSCM", "ARAP"])
        param_layout.addWidget(QLabel("Parameterization Method:"))
        param_layout.addWidget(self.cmb_method)
        
        self.spin_resolution = QDoubleSpinBox()
        self.spin_resolution.setRange(0.1, 5.0)
        self.spin_resolution.setValue(1.0)
        param_layout.addWidget(QLabel("Resolution:"))
        param_layout.addWidget(self.spin_resolution)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Fabric properties
        fabric_group = QGroupBox("Fabric Properties")
        fabric_layout = QVBoxLayout()
        
        self.spin_stretch_x = QDoubleSpinBox()
        self.spin_stretch_x.setRange(0.1, 3.0)
        self.spin_stretch_x.setValue(1.2)
        fabric_layout.addWidget(QLabel("X Stretch Factor:"))
        fabric_layout.addWidget(self.spin_stretch_x)
        
        self.spin_stretch_y = QDoubleSpinBox()
        self.spin_stretch_y.setRange(0.1, 3.0)
        self.spin_stretch_y.setValue(1.2)
        fabric_layout.addWidget(QLabel("Y Stretch Factor:"))
        fabric_layout.addWidget(self.spin_stretch_y)
        
        fabric_group.setLayout(fabric_layout)
        layout.addWidget(fabric_group)
        
        # Process buttons
        self.btn_process = QPushButton("Generate Pattern")
        self.btn_process.clicked.connect(self.generate_pattern)
        layout.addWidget(self.btn_process)
        
        # Log output
        self.text_log = QTextEdit()
        self.text_log.setMaximumHeight(200)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.text_log)
        
        panel.setLayout(layout)
        return panel
        
    def create_visualization_panel(self):
        panel = QGroupBox("Visualization")
        layout = QVBoxLayout()
        
        # 3D view
        self.plotter_3d = pvqt.BackgroundPlotter()
        layout.addWidget(self.plotter_3d.interactor)
        
        # 2D pattern view
        self.plotter_2d = pvqt.BackgroundPlotter()
        layout.addWidget(self.plotter_2d.interactor)
        
        panel.setLayout(layout)
        return panel
        
    def load_model(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open 3D Model", "", 
            "3D Files (*.stl *.obj *.ply *.off)"
        )
        if filepath:
            try:
                self.toolchain.load_mesh(filepath)
                self.update_3d_view()
                self.log_message(f"Loaded: {os.path.basename(filepath)}")
            except Exception as e:
                self.log_message(f"Error loading file: {str(e)}")
                
    def generate_pattern(self):
        try:
            # Get parameters from UI
            method = self.cmb_method.currentText().lower()
            stretch_factors = (self.spin_stretch_x.value(), 
                             self.spin_stretch_y.value())
            
            # Run pipeline
            self.toolchain.preprocess_mesh()
            self.toolchain.parameterize_mesh(method)
            self.toolchain.optimize_pattern(stretch_factors, {})
            
            self.update_2d_view()
            self.log_message("Pattern generated successfully")
            
        except Exception as e:
            self.log_message(f"Error generating pattern: {str(e)}")
            
    def export_pattern(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Pattern", "",
            "DXF Files (*.dxf);;SVG Files (*.svg)"
        )
        if filepath:
            self.toolchain.export_pattern(filepath)
            self.log_message(f"Exported pattern to: {filepath}")
            
    def update_3d_view(self):
        # Update 3D plotter with loaded mesh
        pass
        
    def update_2d_view(self):
        # Update 2D plotter with generated pattern
        pass
        
    def log_message(self, message):
        self.text_log.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
