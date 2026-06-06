from manim import *

class Test(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        texto = Text("Hola Mundo", font_size=48, color=BLUE)
        self.play(Write(texto))
        self.wait(2)