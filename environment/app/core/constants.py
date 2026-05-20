"""
constants.py
============
System-wide physical and algorithmic constants.

These values are fixed across all configurations and are not
exposed as tunable parameters.
"""
from __future__ import annotations

# Physical constants
G: float = 9.81                  # Standard gravitational acceleration (m/s²)
TWO_PI: float = 6.283185307179586  # 2π

# Numerical thresholds
VELOCITY_ZERO_THRESHOLD: float = 1e-4   # Below this |x_dot|, Coulomb friction is zero
SINGULARITY_GUARD: float = 1e-12        # Minimum pivot magnitude in matrix inversion
FD_EPSILON: float = 1e-5                # Finite-difference step size for Jacobian

# Simulation limits
MAX_POLE_ANGLE_RAD: float = 1.2         # Emergency stop threshold (radians)
MAX_CART_DISPLACEMENT_M: float = 2.38   # Emergency stop threshold (metres)

# Filter constants
INNOVATION_ALPHA: float = 0.96          # EKF innovation energy EMA decay
INNOVATION_CAP: float = 50.0            # Maximum innovation energy for noise scaling
