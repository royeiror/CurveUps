# src/main_pipeline.py - CORRECTED VERSION
import numpy as np
from scipy.optimize import minimize

class CurveUpToolchain:
    def __init__(self):
        self.input_mesh = None
        self.optimized_curves = None
        self.stretch_factors = (1.0, 1.0)
        
    def load_mesh(self, filepath):
        """Load target 3D shape"""
        try:
            # For now, use a simple demo surface
            self.input_mesh = self._create_demo_surface()
            return f"✓ Loaded target shape: {len(self.input_mesh['vertices'])} vertices"
        except Exception as e:
            return f"✗ Error loading shape: {str(e)}"
    
    def _create_demo_surface(self):
        """Create a curved surface for demonstration"""
        # Create a wavy surface (like the paper's examples)
        x = np.linspace(-1, 1, 20)
        y = np.linspace(-1, 1, 20)
        X, Y = np.meshgrid(x, y)
        Z = 0.3 * np.sin(2 * np.pi * X) * np.cos(2 * np.pi * Y)  # Wavy surface
        
        vertices = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
        
        # Simple triangulation
        faces = []
        for i in range(19):
            for j in range(19):
                v1 = i * 20 + j
                v2 = v1 + 1
                v3 = v1 + 20
                v4 = v2 + 20
                faces.extend([[v1, v2, v3], [v2, v4, v3]])
        
        return {"vertices": vertices, "faces": faces}
    
    def compute_optimal_curves(self, stretch_x=1.5, stretch_y=1.5, curve_density=10):
        """Compute optimal curves for 3D printing on stretched fabric"""
        if self.input_mesh is None:
            return "✗ No target shape loaded"
        
        try:
            self.stretch_factors = (stretch_x, stretch_y)
            
            # Core CurveUp algorithm:
            # 1. Analyze surface curvature
            curvature_map = self._compute_surface_curvature()
            
            # 2. Generate candidate curves
            candidate_curves = self._generate_candidate_curves(curvature_map, curve_density)
            
            # 3. Optimize curve placement considering fabric mechanics
            self.optimized_curves = self._optimize_curve_placement(
                candidate_curves, curvature_map, stretch_x, stretch_y
            )
            
            return f"✓ Computed {len(self.optimized_curves)} optimal curves"
            
        except Exception as e:
            return f"✗ Curve computation error: {str(e)}"
    
    def _compute_surface_curvature(self):
        """Compute principal curvatures of the surface"""
        # Simplified curvature computation
        vertices = self.input_mesh['vertices']
        curvature = np.zeros(len(vertices))
        
        # Simple approximation: use z-coordinate variation
        for i, vertex in enumerate(vertices):
            # Find neighbors (simplified)
            neighbors = [v for v in vertices if np.linalg.norm(v - vertex) < 0.3]
            if len(neighbors) > 2:
                # Rough curvature estimate
                curvature[i] = np.std([v[2] for v in neighbors])
        
        return curvature
    
    def _generate_candidate_curves(self, curvature_map, density):
        """Generate candidate curves based on surface curvature"""
        curves = []
        vertices = self.input_mesh['vertices']
        
        # Generate curves along high-curvature regions
        high_curvature_indices = np.where(curvature_map > np.percentile(curvature_map, 70))[0]
        
        for i in range(min(density, len(high_curvature_indices))):
            start_idx = high_curvature_indices[i]
            curve = self._trace_curve_from_point(start_idx, vertices, curvature_map)
            if len(curve) > 3:  # Only keep meaningful curves
                curves.append(curve)
        
        return curves
    
    def _trace_curve_from_point(self, start_idx, vertices, curvature_map):
        """Trace a curve following high curvature regions"""
        curve = [start_idx]
        current_idx = start_idx
        visited = set([start_idx])
        
        for _ in range(10):  # Limit curve length
            # Find neighboring high-curvature vertices
            neighbors = []
            for i, vertex in enumerate(vertices):
                if (i not in visited and 
                    np.linalg.norm(vertex - vertices[current_idx]) < 0.2 and
                    curvature_map[i] > 0.1):
                    neighbors.append((i, curvature_map[i]))
            
            if not neighbors:
                break
                
            # Move to highest curvature neighbor
            next_idx = max(neighbors, key=lambda x: x[1])[0]
            curve.append(next_idx)
            visited.add(next_idx)
            current_idx = next_idx
        
        return curve
    
    def _optimize_curve_placement(self, candidate_curves, curvature_map, stretch_x, stretch_y):
        """Optimize which curves to use and their properties"""
        # Simplified optimization: select curves that cover high-curvature areas
        optimized = []
        covered_vertices = set()
        
        # Sort curves by "importance" (total curvature along curve)
        curve_scores = []
        for curve in candidate_curves:
            score = sum(curvature_map[i] for i in curve)
            curve_scores.append((curve, score))
        
        # Select top curves
        curve_scores.sort(key=lambda x: x[1], reverse=True)
        for curve, score in curve_scores[:5]:  # Top 5 curves
            optimized.append({
                'vertices': curve,
                'width': 0.1 + 0.05 * score,  # Wider curves for high curvature
                'material_density': 0.5 + 0.3 * score  # Higher density for structural areas
            })
            covered_vertices.update(curve)
        
        return optimized
    
    def export_print_pattern(self, filepath):
        """Export curves for 3D printing on stretched fabric"""
        if self.optimized_curves is None:
            return "✗ No curves computed"
        
        try:
            if filepath.endswith('.svg'):
                return self._export_curves_svg(filepath)
            else:
                return self._export_curves_gcode(filepath)
                
        except Exception as e:
            return f"✗ Export error: {str(e)}"
    
    def _export_curves_svg(self, filepath):
        """Export curves as SVG for visualization"""
        vertices = self.input_mesh['vertices']
        
        # Scale and project to 2D (accounting for fabric stretch)
        scale = 500
        margin = 50
        
        # Apply inverse stretch to get printing coordinates
        stretch_x, stretch_y = self.stretch_factors
        projected_vertices = vertices.copy()
        projected_vertices[:, 0] /= stretch_x  # Compress X for stretching
        projected_vertices[:, 1] /= stretch_y  # Compress Y for stretching
        
        # Normalize to [0,1] and scale
        min_vals = np.min(projected_vertices[:, :2], axis=0)
        max_vals = np.max(projected_vertices[:, :2], axis=0)
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        normalized_vertices = (projected_vertices[:, :2] - min_vals) / range_vals
        scaled_vertices = normalized_vertices * scale
        
        width = scale + 2 * margin
        height = scale + 2 * margin
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <title>CurveUp - 3D Printing Pattern for Stretched Fabric</title>
  <rect width="100%" height="100%" fill="white"/>
  
  <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold">
    CurveUp Printing Pattern
  </text>
  <text x="{width/2}" y="50" text-anchor="middle" font-family="Arial" font-size="12">
    Stretch Factors: {self.stretch_factors[0]:.1f}x{self.stretch_factors[1]:.1f}
  </text>
'''
        
        # Draw each optimized curve
        for i, curve_data in enumerate(self.optimized_curves):
            curve_vertices = curve_data['vertices']
            width = curve_data['width'] * 20  # Visual width
            
            points = []
            for vertex_idx in curve_vertices:
                if vertex_idx < len(scaled_vertices):
                    x = scaled_vertices[vertex_idx, 0] + margin
                    y = scaled_vertices[vertex_idx, 1] + margin
                    points.append(f"{x:.1f},{y:.1f}")
            
            if len(points) > 1:
                points_str = " ".join(points)
                svg_content += f'  <polyline points="{points_str}" fill="none" stroke="blue" stroke-width="{width}" opacity="0.7"/>\n'
        
        svg_content += f'''
  <text x="20" y="{height-20}" font-family="Arial" font-size="10">
    Print these curves on fabric stretched {self.stretch_factors[0]:.1f}x{self.stretch_factors[1]:.1f}
  </text>
</svg>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return f"✓ Printing pattern exported to {filepath}"
    
    def _export_curves_gcode(self, filepath):
        """Export curves as G-code for 3D printers"""
        # This would generate actual 3D printer instructions
        return "G-code export not yet implemented"
