# src/main_pipeline.py
import numpy as np

class CurveUpToolchain:
    def __init__(self):
        self.input_mesh = None
        self.parameterized_mesh = None
        self.optimized_pattern = None
        
    def load_mesh(self, filepath):
        """Load 3D mesh from file"""
        try:
            # For now, create a simple demo mesh
            self.input_mesh = self._create_demo_mesh()
            return f"Loaded mesh with {len(self.input_mesh['vertices'])} vertices"
        except Exception as e:
            return f"Error loading mesh: {e}"
    
    def _create_demo_mesh(self):
        """Create a simple cube for demonstration"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ])
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 5, 6], [4, 6, 7],  # top
            [0, 1, 5], [0, 5, 4],  # front
            [2, 3, 7], [2, 7, 6],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 2, 6], [1, 6, 5]   # right
        ])
        return {"vertices": vertices, "faces": faces}
    
    def parameterize_mesh(self, method="conformal"):
        """Convert 3D mesh to 2D parameterization"""
        if self.input_mesh is None:
            return "No mesh loaded"
        
        # Simple 2D projection for demo
        vertices_2d = self.input_mesh['vertices'][:, :2]  # Just use X,Y coordinates
        self.parameterized_mesh = vertices_2d
        return f"Parameterized using {method} - {len(vertices_2d)} points"
    
    def optimize_pattern(self, stretch_x=1.0, stretch_y=1.0):
        """Apply fabric stretch optimization"""
        if self.parameterized_mesh is None:
            return "No parameterized mesh"
        
        # Simple scaling for demo
        optimized = self.parameterized_mesh * [stretch_x, stretch_y]
        self.optimized_pattern = optimized
        return f"Optimized with stretch ({stretch_x}, {stretch_y})"
    
    def export_pattern(self, filepath):
        """Export 2D pattern to file"""
        if self.optimized_pattern is None:
            return "No optimized pattern"
        
        return f"Exported pattern to {filepath} ({len(self.optimized_pattern)} points)"
