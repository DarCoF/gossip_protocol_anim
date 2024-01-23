from manim import *
import numpy as np

from manim import *
import numpy as np

from manim import *
import numpy as np

class Projectile(Scene):
    def __init__(self, start_obj, end_obj, **kwargs):
        super().__init__(**kwargs)
        self.start_obj = start_obj
        self.end_obj = end_obj

    def construct(self):
        # Create the projectile
        projectile = Dot(color=WHITE)
        projectile.move_to(self.start_obj.get_center())

        # Define the sinusoidal path function
        def sinusoidal_path(pos, amplitude=0.5, frequency=2, phase=0):
            # Apply a sinusoidal function to the y-coordinate
            sine_wave = amplitude * np.sin(frequency * pos[0] + phase) * UP
            return pos + sine_wave

        # Create a TracedPath with the sinusoidal path function
        # Using a lambda to make sure no arguments are passed
        trace = TracedPath(lambda: sinusoidal_path(projectile.get_center(), amplitude=projectile.radius, frequency=4), 
                           stroke_color=BLUE, stroke_width=2, stroke_opacity=[0.8, 0], dissipating_time=0.1)

        # Add the projectile and the trace to the scene
        self.add(trace, projectile)

        # Define the movement of the projectile along a straight line
        straight_path = Line(self.start_obj.get_center(), self.end_obj.get_center())

        # Animate the projectile movement
        self.play(MoveAlongPath(projectile, straight_path), run_time=0.75, rate_func=linear)



if __name__ == "__main__":
    start_circle = Circle(radius=0.2, color=BLUE).move_to(LEFT * 4)
    end_circle = Circle(radius=0.2, color=RED).move_to(RIGHT * 4)
    scene = Projectile(start_circle, end_circle)
    scene.render(preview=True)
