from manim import *

class RosaSimple(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Ecuación a la izquierda
        ecuacion = MathTex(r"r = 3\cos(2\theta)", font_size=48, color=BLUE)
        ecuacion.to_corner(UL, buff=0.5)
        self.play(Write(ecuacion))
        
        # Plano cartesiano a la derecha
        ejes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=5.5,
            y_length=5.5,
            axis_config={"color": GRAY}
        )
        ejes.shift(RIGHT * 2.5)
        ejes.to_edge(DOWN, buff=0.5)
        self.play(Create(ejes))
        
        # Función polar
        def polar_to_cartesian(r, theta):
            return np.array([r * np.cos(theta), r * np.sin(theta), 0])
        
        rosa = ParametricFunction(
            lambda t: polar_to_cartesian(3 * np.cos(2 * t), t),
            t_range=[0, 2 * PI],
            color=PURPLE,
            stroke_width=5
        )
        
        self.play(Create(rosa), run_time=3)
        self.wait(2)

# Render: manim -pql rosa_simple.py RosaSimple