from manim import *

class IntegralPorPartes(Scene):
    def construct(self):
        # 1. Título y Problema inicial
        titulo = Text("Integración por Partes", color=BLUE).to_edge(UP)
        problema = MathTex(r"\int x \sin(2x) \, dx", color=WHITE).scale(1.2).shift(UP*1.5)
        
        # 2. Fórmula de Integración por Partes
        formula = MathTex(
            r"\int u \, dv = u v - \int v \, du", 
            color=YELLOW
        ).scale(0.8).next_to(problema, DOWN, buff=0.5)

        # 3. Elección de variables (u y dv)
        eleccion = MathTex(
            r"u = x \implies du = dx \\",
            r"dv = \sin(2x) dx \implies v = -\frac{1}{2}\cos(2x)",
            color=GREEN
        ).scale(0.8).shift(LEFT*3)

        # 4. Desarrollo del ejercicio
        paso1 = MathTex(
            r"= x \left( -\frac{1}{2}\cos(2x) \right) - \int -\frac{1}{2}\cos(2x) \, dx"
        ).scale(0.8).shift(RIGHT*2)
        
        paso2 = MathTex(
            r"= -\frac{x}{2}\cos(2x) + \frac{1}{2} \int \cos(2x) \, dx"
        ).scale(0.8).next_to(paso1, DOWN, aligned_edge=LEFT)
        
        resultado_final = MathTex(
            r"= -\frac{x}{2}\cos(2x) + \frac{1}{4}\sin(2x) + C",
            color=YELLOW
        ).scale(0.9).next_to(paso2, DOWN, aligned_edge=LEFT, buff=0.5)

        # --- SECUENCIA DE ANIMACIÓN ---
        
        # Presentación (5 segundos)
        self.play(Write(titulo))
        self.play(Write(problema))
        self.wait(1)
        self.play(FadeIn(formula))
        self.wait(2)

        # Elección de u y dv (8 segundos)
        self.play(Write(eleccion), run_time=4)
        self.wait(3)

        # Desarrollo paso a paso (12 segundos)
        self.play(Write(paso1), run_time=4)
        self.wait(2)
        self.play(TransformMatchingShapes(paso1.copy(), paso2), run_time=3)
        self.wait(2)
        
        # Resultado final (10 segundos)
        self.play(Write(resultado_final), run_time=3)
        self.play(RectangularBoundsCheck(resultado_final, color=BLUE)) # Resalta el resultado
        self.play(Indicate(resultado_final))
        
        self.wait(10) # Espacio para tu conclusión final en Lógica Vital