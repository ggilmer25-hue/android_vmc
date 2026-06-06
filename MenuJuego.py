from manim import *

class DerivadaVisual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Función f(x) = x²
        ejes = Axes(x_range=[-3, 3], y_range=[-1, 9])
        funcion = ejes.plot(lambda x: x**2, color=BLUE)
        
        # Tangente en x=1
        tangente = ejes.get_secant_slope_group(1, funcion, dx=0.01)
        
        self.play(Create(ejes), Create(funcion))
        self.play(Create(tangente))
        self.wait(2)