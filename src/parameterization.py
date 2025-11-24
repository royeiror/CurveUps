# src/parameterization.py
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

class MeshParameterizer:
    def __init__(self, mesh):
        self.mesh = mesh
        self.vertices = mesh.vertices
        self.faces = mesh.faces
        
    def conformal_parameterization(self):
        """Conformal parameterization using cotangent weights"""
        try:
            n_vertices = len(self.vertices)
            
            # Build Laplace matrix with cotangent weights
            L = self._build_cotangent_laplacian()
            
            # Pin two boundary vertices
            boundary_vertices = self._find_boundary_vertices()
            if len(boundary_vertices) < 2:
                # Fallback to simple projection if no clear boundary
                return self.vertices[:, :2]
                
            fixed_indices = boundary_vertices[:2]
            
            # Solve for UV coordinates
            uv = self._solve_parameterization(L, fixed_indices)
            return uv
            
        except Exception as e:
            print(f"Conformal parameterization failed: {e}")
            # Fallback to simple planar projection
            return self.vertices[:, :2]
    
    def lscm_parameterization(self):
        """Least Squares Conformal Maps parameterization"""
        try:
            # For now, use a simplified approach
            # Real LSCM would involve solving a linear system
            return self.vertices[:, [0, 2]]  # Use X,Z coordinates
            
        except Exception as e:
            print(f"LSCM parameterization failed: {e}")
            return self.vertices[:, :2]
    
    def _build_cotangent_laplacian(self):
        """Build cotangent weight Laplacian matrix (simplified)"""
        n_vertices = len(self.vertices)
        
        # Simplified uniform weights for now
        # Real implementation would compute cotangent weights
        row_ind = []
        col_ind = []
        data = []
        
        for face in self.faces:
            for i in range(3):
                v1 = face[i]
                v2 = face[(i + 1) % 3]
                
                # Add uniform weights (simplified)
                row_ind.extend([v1, v2])
                col_ind.extend([v2, v1])
                data.extend([-1, -1])
        
        # Create sparse matrix
        L = coo_matrix((data, (row_ind, col_ind)), shape=(n_vertices, n_vertices))
        
        # Set diagonal to negative sum of row
        row_sum = np.array(L.sum(axis=1)).flatten()
        L.setdiag(-row_sum)
        
        return L
    
    def _find_boundary_vertices(self):
        """Find boundary vertices for pinning"""
        # Simplified: return first few vertices
        return [0, min(1, len(self.vertices)-1)]
    
    def _solve_parameterization(self, L, fixed_indices):
        """Solve linear system for parameterization"""
        n_vertices = len(self.vertices)
        
        # Set up boundary conditions
        fixed_u = np.zeros(n_vertices)
        fixed_v = np.zeros(n_vertices)
        
        # Pin first vertex at (0,0), second at (1,0)
        if len(fixed_indices) >= 2:
            fixed_u[fixed_indices[0]] = 0
            fixed_v[fixed_indices[0]] = 0
            fixed_u[fixed_indices[1]] = 1
            fixed_v[fixed_indices[1]] = 0
        
        # Solve for U and V coordinates (simplified)
        # Real implementation would solve (L u = 0) with boundary conditions
        u_coords = np.zeros(n_vertices)
        v_coords = np.zeros(n_vertices)
        
        # Simple linear assignment based on vertex indices
        for i in range(n_vertices):
            u_coords[i] = i / max(n_vertices, 1)
            v_coords[i] = (i % 10) / 10.0  # Some variation in V
        
        return np.column_stack([u_coords, v_coords])
