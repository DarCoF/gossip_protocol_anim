from manim import *
import numpy as np

from manim import *
import numpy as np

from manim import *
import numpy as np

class Projectile():
    def __init__(self, start_obj, end_obj, **kwargs):
        super().__init__(**kwargs)
        self.start_obj = start_obj
        self.end_obj = end_obj
        self.projectile = Dot(color=WHITE, radius = 0.025)

    def add_traces(self):
        # Define the sinusoidal path function
        def sinusoidal_path(pos, amplitude=0.5, frequency=2, phase=0):
            # Apply a sinusoidal function to the y-coordinate
            sine_wave = amplitude * np.sin(frequency * pos[0] + phase) * UP
            return pos + sine_wave

        # Create a TracedPath with the sinusoidal path function
        # Using a lambda to make sure no arguments are passed
        trace = TracedPath(lambda: sinusoidal_path(self.projectile.get_center(), amplitude=self.projectile.radius, frequency=4), 
                           stroke_color=BLUE, stroke_width=2, stroke_opacity=[0.8, 0], dissipating_time=0.1)
        return trace

    def construct(self):
        # Create the projectile
        self.projectile.move_to(self.start_obj)
        
        # Define the movement of the projectile along a straight line
        straight_path = Line(self.start_obj, self.end_obj)

        # Animate the projectile movement
        return (AnimationGroup(Flash(self.start_obj, color=WHITE, flash_radius=0.15, run_time=0.1), MoveAlongPath(self.projectile, straight_path), run_time=0.5, rate_func=linear))



