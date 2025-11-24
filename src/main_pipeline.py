# src/main_pipeline.py
import numpy as np
import trimesh
from parameterization import MeshParameterizer

class CurveUpToolchain:
    def __init__(self):
        self.input_mesh = None
        self.parameterized_mesh = None
        self.optimized_pattern = None
        self.parameterizer = None
        
    def load_mesh(self, filepath):
        """Load 3D mesh from file using trimesh"""
        try:
            if filepath.endswith(('.stl', '.obj', '.ply', '.off')):
                self.input_mesh = trimesh.load_mesh(filepath)
                
                # Validate mesh
                if not self.input_mesh.is_watertight:
                    return f"Loaded mesh: {len(self.input_mesh.vertices)} vertices (non-watertight)"
                
                self.parameterizer = MeshParameterizer(self.input_mesh)
                return f"✓ Loaded mesh: {len(self.input_mesh.vertices)} vertices, {len(self.input_mesh.faces)} faces"
            else:
                # Create demo mesh for unsupported formats
                self.input_mesh = self._create_demo_mesh()
                return "⚠ Created demo mesh (unsupported format)"
                
        except Exception as e:
            # Fallback to demo mesh
            self.input_mesh = self._create_demo_mesh()
            return f"⚠ Created demo mesh (error: {str(e)})"
    
    def _create_demo_mesh(self):
        """Create a UV sphere for demonstration"""
        return trimesh.creation.icosphere(subdivisions=2)
    
    def parameterize_mesh(self, method="conformal"):
        """Convert 3D mesh to 2D parameterization"""
        if self.input_mesh is None or self.parameterizer is None:
            return "✗ No mesh loaded or parameterizer not initialized"
        
        try:
            if method == "conformal":
                self.parameterized_mesh = self.parameterizer.conformal_parameterization()
            elif method == "lscm":
                self.parameterized_mesh = self.parameterizer.lscm_parameterization()
            else:
                return f"✗ Unknown method: {method}"
            
            return f"✓ Parameterized using {method} - {len(self.parameterized_mesh)} UV points"
            
        except Exception as e:
            return f"✗ Parameterization error: {str(e)}"
    
    def optimize_pattern(self, stretch_x=1.0, stretch_y=1.0):
        """Apply fabric stretch optimization based on CurveUp paper"""
        if self.parameterized_mesh is None:
            return "✗ No parameterized mesh available"
        
        try:
            # Apply anisotropic scaling for fabric stretch
            uv_coords = self.parameterized_mesh.copy()
            uv_coords[:, 0] *= stretch_x  # Scale U coordinate
            uv_coords[:, 1] *= stretch_y  # Scale V coordinate
            
            # Simple distortion minimization (placeholder for CurveUp algorithm)
            optimized_uv = self._minimize_distortion(uv_coords, stretch_x, stretch_y)
            self.optimized_pattern = optimized_uv
            
            return f"✓ Optimized with stretch factors ({stretch_x}, {stretch_y})"
            
        except Exception as e:
            return f"✗ Optimization error: {str(e)}"
    
    def _minimize_distortion(self, uv_coords, stretch_x, stretch_y):
        """Simple distortion minimization (placeholder for CurveUp algorithm)"""
        # This is a simplified version - real CurveUp uses more complex optimization
        # Normalize to unit area
        min_u, max_u = np.min(uv_coords[:, 0]), np.max(uv_coords[:, 0])
        min_v, max_v = np.min(uv_coords[:, 1]), np.max(uv_coords[:, 1])
        
        # Scale to account for stretch factors while maintaining proportions
        scale_u = 1.0 / (max_u - min_u) if (max_u - min_u) > 0 else 1.0
        scale_v = 1.0 / (max_v - min_v) if (max_v - min_v) > 0 else 1.0
        
        # Apply scaling with stretch factors
        uv_coords[:, 0] = (uv_coords[:, 0] - min_u) * scale_u * stretch_x
        uv_coords[:, 1] = (uv_coords[:, 1] - min_v) * scale_v * stretch_y
        
        return uv_coords
    
    def export_pattern(self, filepath):
        """Export 2D pattern to DXF file"""
        if self.optimized_pattern is None:
            return "✗ No optimized pattern to export"
        
        try:
            if filepath.endswith('.dxf'):
                self._export_dxf(filepath)
            elif filepath.endswith('.svg'):
                self._export_svg(filepath)
            else:
                return "✗ Unsupported file format. Use .dxf or .svg"
            
            return f"✓ Pattern exported to {filepath}"
            
        except Exception as e:
            return f"✗ Export error: {str(e)}"
    
    def _export_dxf(self, filepath):
        """Export pattern to DXF format"""
        import ezdxf
        from ezdxf import units
        
        doc = ezdxf.new('R2010')
        doc.units = units.MM
        msp = doc.modelspace()
        
        # Add pattern boundaries
        points = self.optimized_pattern * 1000  # Scale to mm
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            msp.add_line(start, end)
        
        doc.saveas(filepath)
    
    def _export_svg(self, filepath):
        """Export pattern to SVG format"""
        import svgwrite
        
        dwg = svgwrite.Drawing(filepath, profile='tiny')
        
        # Scale and center the pattern
        points = self.optimized_pattern * 100  # Scale for SVG
        min_x, min_y = np.min(points, axis=0)
        max_x, max_y = np.max(points, axis=0)
        
        # Create polygon
        polygon_points = [(float(x - min_x + 10), float(y - min_y + 10)) for x, y in points]
        dwg.add(dwg.polygon(polygon_points, fill='none', stroke='black', stroke_width=1))
        
        dwg.save()
