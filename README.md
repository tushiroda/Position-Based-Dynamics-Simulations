# Position Based Dynamics Simulations
By [tushiroda](https://github.com/tushiroda)

This project consists of a few particle simulations built using PBD, a unique approach to simulating objects. In extremely simplified terms, rather than calculating velocities and extrapolating the final positions, PBD does the reverse.

This repository consists of 4 simulations:
- `point.py` which demonstrates a point constraint.
- `rope.py` which shows series of particles simulating a rope.
- `environment_simulation` which simulates a 'jelly-like' cube. The user can click to cause explosions at the mouse position, breaking the cube apart.
- `crowd.py` which simulates a large crowd of uncontrolled particles and a user-controlled particle trying to navigate through it.
