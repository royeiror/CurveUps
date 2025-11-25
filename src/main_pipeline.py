# src/main_pipeline.py
import numpy as np

class CurveUpToolchain:
    def __init__(self):
        self.input_mesh = None
        self.parameterized_mesh = None
        self.optimized_pattern = None
        self.parameterizer = None
        
    def load_mesh(self, filepath):
        """Load 3D mesh from file"""
        try:
            # For now, create a consistent demo mesh
            self.input_mesh = self._create_demo_mesh()
            self.parameterizer = None  # We'll handle parameterization directly
            
            return f"✓ Loaded demo mesh: {len(self.input_mesh['vertices'])} vertices, {len(self.input_mesh['faces'])} faces"
                
        except Exception as e:
            return f"✗ Error loading mesh: {str(e)}"
    
    def _create_demo_mesh(self):
        """Create a simple cube mesh for demonstration"""
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
            return "✗ No mesh loaded"
        
        try:
            vertices = self.input_mesh['vertices']
            faces = self.input_mesh['faces']
            
            if method == "conformal":
                self.parameterized_mesh = self._simple_conformal_parameterization(vertices, faces)
            elif method == "lscm":
                self.parameterized_mesh = self._simple_lscm_parameterization(vertices, faces)
            else:
                return f"✗ Unknown method: {method}"
            
            return f"✓ Parameterized using {method} - {len(self.parameterized_mesh)} UV points"
            
        except Exception as e:
            return f"✗ Parameterization error: {str(e)}"
    
def _simple_conformal_parameterization(self, vertices, faces):
    """Proper mesh unfolding for cube pattern generation"""
    # For a cube, we need to create an unfolded net (pattern pieces)
    # This will position each face separately in 2D space
    
    # We'll create UV coordinates that represent the unfolded cube
    uv_coords = np.zeros((len(vertices), 2))
    
    # Define the unfolded cube net layout:
    # Each face gets its own position in 2D space
    face_layout = {
        0: {'face': [0, 1, 2, 3], 'position': [1, 1], 'name': 'front'},    # Center
        1: {'face': [4, 5, 6, 7], 'position': [1, 0], 'name': 'top'},      # Above center
        2: {'face': [0, 1, 5, 4], 'position': [1, 2], 'name': 'bottom'},   # Below center  
        3: {'face': [2, 3, 7, 6], 'position': [1, 3], 'name': 'back'},     # Below bottom
        4: {'face': [0, 3, 7, 4], 'position': [0, 1], 'name': 'left'},     # Left of center
        5: {'face': [1, 2, 6, 5], 'position': [2, 1], 'name': 'right'},    # Right of center
    }
    
    # Size of each face in UV space
    face_size = 1.0
    
    # Assign UV coordinates based on face positions
    for face_id, layout in face_layout.items():
        face_vertices = layout['face']
        pos_x, pos_y = layout['position']
        
        # Map each vertex in this face to its position in the unfolded net
        for i, vertex_id in enumerate(face_vertices):
            if i == 0:  # bottom-left
                uv_coords[vertex_id] = [pos_x * face_size, (pos_y + 1) * face_size]
            elif i == 1:  # bottom-right
                uv_coords[vertex_id] = [(pos_x + 1) * face_size, (pos_y + 1) * face_size]
            elif i == 2:  # top-right
                uv_coords[vertex_id] = [(pos_x + 1) * face_size, pos_y * face_size]
            elif i == 3:  # top-left
                uv_coords[vertex_id] = [pos_x * face_size, pos_y * face_size]
    
    # Normalize to [0,1] range
    min_vals = np.min(uv_coords, axis=0)
    max_vals = np.max(uv_coords, axis=0)
    range_vals = max_vals - min_vals
    range_vals[range_vals == 0] = 1
    
    uv_coords = (uv_coords - min_vals) / range_vals
    return uv_coords
    
    def _simple_lscm_parameterization(self, vertices, faces):
        """Simple LSCM-like parameterization using X,Z coordinates"""
        # Use X,Z coordinates as UV coordinates
        uv_coords = vertices[:, [0, 2]].copy()
        
        # Normalize to [0,1] range
        min_vals = np.min(uv_coords, axis=0)
        max_vals = np.max(uv_coords, axis=0)
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1  # Avoid division by zero
        
        uv_coords = (uv_coords - min_vals) / range_vals
        return uv_coords
    
    def optimize_pattern(self, stretch_x=1.0, stretch_y=1.0):
        """Apply fabric stretch optimization"""
        if self.parameterized_mesh is None:
            return "✗ No parameterized mesh available"
        
        try:
            # Apply anisotropic scaling for fabric stretch
            uv_coords = self.parameterized_mesh.copy()
            
            # Center the pattern
            center = np.mean(uv_coords, axis=0)
            uv_coords = uv_coords - center
            
            # Apply stretch factors
            uv_coords[:, 0] *= stretch_x
            uv_coords[:, 1] *= stretch_y
            
            # Recenter
            uv_coords = uv_coords + center
            
            self.optimized_pattern = uv_coords
            
            return f"✓ Optimized with stretch factors ({stretch_x}, {stretch_y})"
            
        except Exception as e:
            return f"✗ Optimization error: {str(e)}"
    
    def export_pattern(self, filepath):
        """Export 2D pattern to file"""
        if self.optimized_pattern is None:
            return "✗ No optimized pattern to export"
        
        try:
            if filepath.endswith('.svg'):
                return self._export_svg(filepath)
            elif filepath.endswith('.txt'):
                return self._export_text(filepath)
            else:
                # Default to text export
                return self._export_text(filepath + '.txt')
            
        except Exception as e:
            return f"✗ Export error: {str(e)}"
    
    def _export_svg(self, filepath):
    """Export pattern showing individual fabric pieces"""
    pattern = self.optimized_pattern
    
    # Scale for better visibility
    scale = 300
    pattern_scaled = pattern * scale
    
    # Add generous margin
    margin = 80
    min_x, min_y = np.min(pattern_scaled, axis=0)
    max_x, max_y = np.max(pattern_scaled, axis=0)
    
    width = max_x - min_x + 2 * margin
    height = max_y - min_y + 2 * margin
    
    # Center the pattern
    pattern_centered = pattern_scaled.copy()
    pattern_centered[:, 0] = pattern_centered[:, 0] - min_x + margin
    pattern_centered[:, 1] = pattern_centered[:, 1] - min_y + margin
    
    # Define face colors for better visualization
    face_colors = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#FFCCFF', '#CCFFFF']
    face_names = ['Front', 'Top', 'Bottom', 'Back', 'Left', 'Right']
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <title>CurveUp Pattern - Fabric Pieces</title>
  
  <rect width="100%" height="100%" fill="white"/>
  
  <!-- Draw each face as a separate fabric piece -->
'''
    
    # Draw each face as a separate colored polygon
    faces = self.input_mesh['faces']
    for i, face in enumerate(faces):
        if i < len(face_colors):
            face_points = []
            for vertex_idx in face:
                if vertex_idx < len(pattern_centered):
                    x, y = pattern_centered[vertex_idx]
                    face_points.append((x, y))
            
            if len(face_points) >= 3:
                points_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in face_points])
                
                # Add the face polygon
                svg_content += f'  <polygon points="{points_str}" fill="{face_colors[i]}" stroke="black" stroke-width="2" opacity="0.7"/>\n'
                
                # Add face label
                center_x = sum(x for x, y in face_points) / len(face_points)
                center_y = sum(y for x, y in face_points) / len(face_points)
                svg_content += f'  <text x="{center_x:.1f}" y="{center_y:.1f}" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="black">{face_names[i] if i < len(face_names) else f"Face {i}"}</text>\n'
    
    # Draw vertices and edges
    svg_content += '  <!-- Draw edges -->\n'
    svg_content += '  <g stroke="black" stroke-width="1" fill="none">\n'
    
    for face in faces:
        if len(face) >= 3:
            for j in range(len(face)):
                v1 = face[j]
                v2 = face[(j + 1) % len(face)]
                if v1 < len(pattern_centered) and v2 < len(pattern_centered):
                    x1, y1 = pattern_centered[v1]
                    x2, y2 = pattern_centered[v2]
                    svg_content += f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'
    
    svg_content += '  </g>\n'
    
    # Draw vertices
    svg_content += '  <!-- Draw vertices -->\n'
    for i, (x, y) in enumerate(pattern_centered):
        svg_content += f'  <circle cx="{x}" cy="{y}" r="4" fill="red" stroke="darkred" stroke-width="1"/>\n'
        svg_content += f'  <text x="{x+8}" y="{y+4}" font-family="Arial" font-size="10" fill="darkred">V{i}</text>\n'
    
    # Add title and info
    svg_content += f'''
  <!-- Title and info -->
  <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="navy">
    CurveUp - Fabric Pattern Pieces
  </text>
  <text x="20" y="{height-20}" font-family="Arial" font-size="10" fill="gray">
    {len(pattern)} vertices, {len(faces)} fabric pieces - Ready for cutting and assembly
  </text>
</svg>'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return f"✓ SVG pattern exported to {filepath} ({len(faces)} fabric pieces)"
    
    def _export_text(self, filepath):
        """Export pattern to simple text format"""
        pattern = self.optimized_pattern
        
        with open(filepath, 'w') as f:
            f.write("# CurveUp Pattern Export\n")
            f.write(f"# Points: {len(pattern)}\n")
            f.write("# Format: X, Y (normalized coordinates)\n")
            for i, point in enumerate(pattern):
                f.write(f"{point[0]:.6f}, {point[1]:.6f}\n")
        
        return f"✓ Text pattern exported to {filepath} ({len(pattern)} points)"
