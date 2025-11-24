# Add this import at the top of gui_main.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Add this method to the MainWindow class:
def show_pattern_preview(self):
    """Show a simple preview of the generated pattern"""
    if self.toolchain.optimized_pattern is None:
        return
        
    try:
        fig = Figure(figsize=(5, 4))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        pattern = self.toolchain.optimized_pattern
        ax.plot(pattern[:, 0], pattern[:, 1], 'b-', linewidth=2)
        ax.plot(pattern[:, 0], pattern[:, 1], 'ro', markersize=3)
        ax.set_title('Generated 2D Pattern')
        ax.set_aspect('equal')
        ax.grid(True)
        
        # Create a new window for the preview
        preview_window = QMainWindow(self)
        preview_window.setWindowTitle("Pattern Preview")
        preview_window.setCentralWidget(canvas)
        preview_window.resize(600, 500)
        preview_window.show()
        
    except Exception as e:
        self.log_message(f"⚠ Could not generate preview: {e}")

# Add this button to the button_layout in init_ui():
self.btn_preview = QPushButton("Preview Pattern")
self.btn_preview.clicked.connect(self.show_pattern_preview)
self.btn_preview.setStyleSheet("QPushButton { background-color: #f39c12; color: white; padding: 10px; font-weight: bold; }")
button_layout.addWidget(self.btn_preview)
