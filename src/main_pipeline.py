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
        """Simple conformal-like parameterization"""
        # Use X,Y coordinates as UV coordinates (planar projection)
        uv_coords = vertices[:, :2].copy()
        
        # Normalize to [0,1] range
        min_vals = np.min(uv_coords, axis=0)
        max_vals = np.max(uv_coords, axis=0)
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1  # Avoid division by zero
        
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
    """Export pattern to proper SVG format with unfolded faces"""
    pattern = self.optimized_pattern
    
    # For a cube, we need to show the unfolded net (6 faces)
    # Let's arrange the faces in a cross pattern
    faces = self.input_mesh['faces']
    vertices_2d = pattern
    
    # Scale for better visibility in SVG (convert to pixels)
    scale = 100
    spacing = 20  # Space between faces
    
    # Calculate face positions in the unfolded net
    face_positions = []
    
    # Position the 6 faces in a cross pattern:
    #   [1]
    # [4][0][5]
    #   [2]
    #   [3]
    
    face_offsets = [
        (1, 1),  # Face 0: center (front)
        (1, 0),  # Face 1: top
        (1, 2),  # Face 2: bottom  
        (1, 3),  # Face 3: back (below bottom)
        (0, 1),  # Face 4: left
        (2, 1),  # Face 5: right
    ]
    
    # Calculate bounds for SVG
    max_faces_x = 3
    max_faces_y = 4
    face_width = 1.2 * scale  # Width of each face with margin
    face_height = 1.2 * scale
    
    svg_width = max_faces_x * face_width + spacing
    svg_height = max_faces_y * face_height + spacing
    
    # Create SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>CurveUp Pattern - Unfolded Cube</title>
  <desc>2D pattern generated from 3D mesh - Cube Unfolding</desc>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="white"/>
  
  <!-- Draw each face of the unfolded cube -->
'''
    
    # Draw each face
    for i, face in enumerate(faces):
        if i >= 6:  # Only draw first 6 faces for cube
            break
            
        offset_x, offset_y = face_offsets[i]
        base_x = offset_x * face_width + spacing/2
        base_y = offset_y * face_height + spacing/2
        
        # Get the 2D coordinates for this face's vertices
        face_points = []
        for vertex_idx in face:
            if vertex_idx < len(vertices_2d):
                x = vertices_2d[vertex_idx][0] * scale + base_x
                y = vertices_2d[vertex_idx][1] * scale + base_y
                face_points.append((x, y))
        
        if len(face_points) == 3:  # Triangle face
            points_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in face_points])
            
            # Add face polygon
            svg_content += f'  <polygon points="{points_str}" fill="lightblue" stroke="black" stroke-width="1" opacity="0.8"/>\n'
            
            # Add face number
            center_x = sum(x for x, y in face_points) / 3
            center_y = sum(y for x, y in face_points) / 3
            svg_content += f'  <text x="{center_x:.1f}" y="{center_y:.1f}" text-anchor="middle" font-family="Arial" font-size="10" fill="darkblue">Face {i}</text>\n'
            
            # Add vertices
            for j, (x, y) in enumerate(face_points):
                svg_content += f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="red"/>\n'
                svg_content += f'  <text x="{x+5:.1f}" y="{y-5:.1f}" font-family="Arial" font-size="8" fill="darkred">v{face[j]}</text>\n'
    
    # Add title and info
    svg_content += f'''
  <!-- Title -->
  <text x="{svg_width/2}" y="20" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="navy">
    CurveUp - Unfolded Cube Pattern
  </text>
  
  <!-- Info -->
  <text x="10" y="{svg_height-10}" font-family="Arial" font-size="10" fill="gray">
    Generated from {len(self.input_mesh['vertices'])} vertices, {len(faces)} faces
  </text>
</svg>'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return f"✓ SVG pattern exported to {filepath} (unfolded cube with {len(faces)} faces)"
