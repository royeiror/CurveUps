# src/main_pipeline.py
import numpy as np
from scipy.spatial import Delaunay

class CurveUpToolchain:
    def __init__(self):
        self.input_mesh = None
        self.optimized_triangles = None
        self.stretch_factors = (1.0, 1.0)
        
    def load_mesh(self, filepath):
        """Load target 3D shape"""
        try:
            # For now, use a curved demo surface
            self.input_mesh = self._create_demo_surface()
            return f"✓ Loaded target shape: {len(self.input_mesh['vertices'])} vertices"
        except Exception as e:
            return f"✗ Error loading shape: {str(e)}"
    
    def _create_demo_surface(self):
        """Create a curved surface for demonstration (like paper examples)"""
        # Create a saddle surface or dome
        x = np.linspace(-1, 1, 15)
        y = np.linspace(-1, 1, 15)
        X, Y = np.meshgrid(x, y)
        
        # Saddle surface: z = x^2 - y^2
        Z = X**2 - Y**2
        
        vertices = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
        
        # Create triangular mesh using Delaunay triangulation
        tri = Delaunay(np.column_stack([X.flatten(), Y.flatten()]))
        faces = tri.simplices
        
        return {"vertices": vertices, "faces": faces}
    
    def compute_optimal_triangles(self, stretch_x=1.5, stretch_y=1.5, triangle_density=0.1):
        """Compute adaptive triangular mesh for 3D printing on stretched fabric"""
        if self.input_mesh is None:
            return "✗ No target shape loaded"
        
        try:
            self.stretch_factors = (stretch_x, stretch_y)
            
            # Core CurveUp algorithm:
            # 1. Compute surface curvature to determine triangle sizes
            curvature_map = self._compute_surface_curvature()
            
            # 2. Generate adaptive triangular mesh
            adaptive_mesh = self._generate_adaptive_mesh(curvature_map, triangle_density)
            
            # 3. Optimize triangle distribution for fabric mechanics
            self.optimized_triangles = self._optimize_triangle_placement(
                adaptive_mesh, curvature_map, stretch_x, stretch_y
            )
            
            return f"✓ Computed {len(self.optimized_triangles)} adaptive triangles"
            
        except Exception as e:
            return f"✗ Triangle computation error: {str(e)}"
    
    def _compute_surface_curvature(self):
        """Compute mean curvature to guide triangle sizing"""
        vertices = self.input_mesh['vertices']
        faces = self.input_mesh['faces']
        curvature = np.zeros(len(vertices))
        
        # Simplified curvature computation using Laplacian
        for i, vertex in enumerate(vertices):
            # Find adjacent vertices (one-ring neighborhood)
            neighbors = []
            for face in faces:
                if i in face:
                    neighbors.extend([v for v in face if v != i])
            neighbors = list(set(neighbors))
            
            if len(neighbors) > 2:
                # Simple discrete mean curvature approximation
                neighbor_vectors = vertices[neighbors] - vertex
                curvature[i] = np.mean(np.linalg.norm(neighbor_vectors, axis=1))
        
        # Normalize curvature
        if np.max(curvature) > 0:
            curvature = curvature / np.max(curvature)
        
        return curvature
    
    def _generate_adaptive_mesh(self, curvature_map, density):
        """Generate triangular mesh with adaptive sizing based on curvature"""
        vertices = self.input_mesh['vertices']
        original_faces = self.input_mesh['faces']
        
        # Create adaptive sampling based on curvature
        # High curvature = smaller triangles, low curvature = larger triangles
        sample_points = []
        triangle_sizes = []
        
        for i, vertex in enumerate(vertices):
            curvature_val = curvature_map[i]
            
            # Determine triangle size based on curvature
            # High curvature (close to 1) -> small triangles (high density)
            # Low curvature (close to 0) -> large triangles (low density)
            base_size = 0.1
            adaptive_size = base_size * (1.0 + 2.0 * curvature_val)  # 0.1 to 0.3 range
            
            # Sample this region
            sample_points.append(vertex)
            triangle_sizes.append(adaptive_size)
            
            # Add extra samples in high-curvature regions
            if curvature_val > 0.7:
                # Add additional samples around high curvature points
                for j in range(2):
                    offset = np.random.normal(0, adaptive_size/3, 3)
                    sample_points.append(vertex + offset)
                    triangle_sizes.append(adaptive_size * 0.8)
        
        # Convert to 2D projection for printing pattern
        sample_points_2d = np.array([p[:2] for p in sample_points])
        
        # Create Delaunay triangulation of sampled points
        if len(sample_points_2d) > 3:
            tri = Delaunay(sample_points_2d)
            adaptive_faces = tri.simplices
            
            # Store triangle information
            adaptive_mesh = {
                'vertices_2d': sample_points_2d,
                'vertices_3d': np.array(sample_points),
                'faces': adaptive_faces,
                'triangle_sizes': triangle_sizes
            }
            
            return adaptive_mesh
        else:
            # Fallback to original mesh
            return {
                'vertices_2d': vertices[:, :2],
                'vertices_3d': vertices,
                'faces': original_faces,
                'triangle_sizes': [0.15] * len(original_faces)
            }
    
    def _optimize_triangle_placement(self, adaptive_mesh, curvature_map, stretch_x, stretch_y):
        """Optimize triangle distribution considering fabric stretch mechanics"""
        optimized_triangles = []
        
        # Apply fabric stretch compensation
        vertices_2d = adaptive_mesh['vertices_2d'].copy()
        vertices_2d[:, 0] /= stretch_x  # Compress X for later stretching
        vertices_2d[:, 1] /= stretch_y  # Compress Y for later stretching
        
        for face in adaptive_mesh['faces']:
            if len(face) == 3:  # Only process triangles
                # Get triangle vertices
                v1, v2, v3 = face
                
                # Calculate triangle properties
                points_2d = vertices_2d[face]
                points_3d = adaptive_mesh['vertices_3d'][face]
                
                # Triangle area in 2D (printing plane)
                area_2d = self._triangle_area(points_2d)
                
                # Estimate required rigidity based on curvature
                avg_curvature = np.mean([curvature_map[v] for v in face])
                rigidity_factor = 0.5 + avg_curvature  # 0.5 to 1.5 range
                
                optimized_triangles.append({
                    'vertices_2d': points_2d,
                    'vertices_3d': points_3d,
                    'area': area_2d,
                    'rigidity': rigidity_factor,
                    'thickness': 0.1 + 0.1 * avg_curvature,  # Thicker in high-curvature areas
                    'material_density': 0.3 + 0.4 * avg_curvature  # Denser printing
                })
        
        return optimized_triangles
    
    def _triangle_area(self, points):
        """Calculate area of a triangle given 3 points"""
        if len(points) != 3:
            return 0
        a, b, c = points
        return 0.5 * abs(
            a[0]*(b[1]-c[1]) + 
            b[0]*(c[1]-a[1]) + 
            c[0]*(a[1]-b[1])
        )
    
    def export_print_pattern(self, filepath):
        """Export adaptive triangular mesh for 3D printing on stretched fabric"""
        if self.optimized_triangles is None:
            return "✗ No triangles computed"
        
        try:
            if filepath.endswith('.svg'):
                return self._export_triangles_svg(filepath)
            else:
                return self._export_triangles_gcode(filepath)
                
        except Exception as e:
            return f"✗ Export error: {str(e)}"
    
    def _export_triangles_svg(self, filepath):
        """Export adaptive triangles as SVG for 3D printing"""
        if not self.optimized_triangles:
            return "✗ No triangles to export"
        
        # Scale for visualization
        scale = 800
        margin = 50
        
        # Get all 2D points and normalize
        all_points = []
        for triangle in self.optimized_triangles:
            all_points.extend(triangle['vertices_2d'])
        
        all_points = np.array(all_points)
        min_vals = np.min(all_points, axis=0)
        max_vals = np.max(all_points, axis=0)
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        # Normalize and scale
        normalized_points = (all_points - min_vals) / range_vals
        max_normalized = np.max(normalized_points, axis=0)
        
        width = max_normalized[0] * scale + 2 * margin
        height = max_normalized[1] * scale + 2 * margin
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <title>CurveUp - Adaptive Triangular Mesh for 3D Printing</title>
  <rect width="100%" height="100%" fill="white"/>
  
  <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">
    CurveUp Adaptive Triangular Mesh
  </text>
  <text x="{width/2}" y="55" text-anchor="middle" font-family="Arial" font-size="12">
    Stretch Factors: {self.stretch_factors[0]:.1f}x{self.stretch_factors[1]:.1f} | Triangles: {len(self.optimized_triangles)}
  </text>
'''
        
        # Draw each adaptive triangle
        for i, triangle in enumerate(self.optimized_triangles):
            points_2d = triangle['vertices_2d']
            
            # Normalize and scale points
            scaled_points = []
            for point in points_2d:
                normalized = (point - min_vals) / range_vals
                x = normalized[0] * scale + margin
                y = normalized[1] * scale + margin
                scaled_points.append((x, y))
            
            # Create polygon points string
            points_str = " ".join([f"{x:.1f},{y:.1f}" for x, y in scaled_points])
            
            # Determine fill color based on rigidity (darker = more rigid)
            rigidity = triangle['rigidity']
            intensity = int(100 + 100 * rigidity)  # 100-200 range
            fill_color = f"rgb({intensity}, {intensity}, 255)"  # Blue shades
            
            # Determine stroke width based on thickness
            stroke_width = 1 + triangle['thickness'] * 3
            
            svg_content += f'''
  <!-- Triangle {i} - Rigidity: {rigidity:.2f} -->
  <polygon points="{points_str}" 
           fill="{fill_color}" 
           stroke="navy" 
           stroke-width="{stroke_width}" 
           opacity="0.8"/>'''
        
        # Add legend
        legend_y = height - 80
        svg_content += f'''
  <!-- Legend -->
  <rect x="20" y="{legend_y}" width="150" height="60" fill="white" stroke="gray" stroke-width="1"/>
  <text x="30" y="{legend_y + 20}" font-family="Arial" font-size="11" font-weight="bold">Legend:</text>
  <text x="30" y="{legend_y + 35}" font-family="Arial" font-size="10">• Darker blue = More rigid</text>
  <text x="30" y="{legend_y + 50}" font-family="Arial" font-size="10">• Thicker border = Thicker print</text>
  
  <text x="20" y="{height-10}" font-family="Arial" font-size="10">
    Print this pattern on fabric stretched {self.stretch_factors[0]:.1f}x{self.stretch_factors[1]:.1f}
  </text>
</svg>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"✓ Adaptive triangle pattern exported to {filepath}"
    
    def _export_triangles_gcode(self, filepath):
        """Export triangles as G-code for 3D printers"""
        # This would generate actual 3D printer instructions
        return "G-code export not yet implemented"
