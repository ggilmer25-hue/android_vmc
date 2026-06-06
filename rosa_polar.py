from manim import *

class RosaCuatroPetalos(Scene):
    def construct(self):
        # Fondo blanco
        self.camera.background_color = WHITE
        
        # Título
        titulo = Text("Rosa de 4 Pétalos", font_size=48, color=BLUE, weight=BOLD)
        titulo.to_edge(UP, buff=0.5)
        self.play(Write(titulo))
        
        # Ecuación
        ecuacion = MathTex(r"r = a \cdot \cos(2\theta)", font_size=40, color=DARK_BROWN)
        ecuacion.next_to(titulo, DOWN, buff=0.4)
        self.play(Write(ecuacion))
        
        # Parámetro
        a_valor = MathTex(r"a = 3", font_size=36, color=BLACK)
        a_valor.next_to(ecuacion, DOWN, buff=0.2)
        self.play(Write(a_valor))
        
        self.wait(1)
        
        # Ejes
        ejes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=7,
            y_length=7,
            axis_config={"color": GRAY, "stroke_width": 2},
            tips=False
        )
        ejes.to_edge(DOWN, buff=0.5)
        
        # Etiquetas de ejes
        etiqueta_x = MathTex("x", font_size=30, color=BLACK).next_to(ejes.x_axis.get_end(), RIGHT)
        etiqueta_y = MathTex("y", font_size=30, color=BLACK).next_to(ejes.y_axis.get_end(), UP)
        
        self.play(Create(ejes), Write(etiqueta_x), Write(etiqueta_y))
        
        # Función polar a cartesiana
        a = 3
        
        def polar_to_cartesian(r, theta):
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            return np.array([x, y, 0])
        
        # Crear la rosa
        rosa = ParametricFunction(
            lambda t: polar_to_cartesian(a * np.cos(2 * t), t),
            t_range=[0, 2 * PI],
            color=PURPLE,
            stroke_width=4
        )
        
        # Animar trazado
        self.play(Create(rosa), run_time=3, rate_func=linear)
        self.wait(1)
        
        # Puntos de los pétalos
        puntos = VGroup()
        for theta in [0, PI/2, PI, 3*PI/2]:
            punto = polar_to_cartesian(a, theta)
            dot = Dot(punto, color=RED, radius=0.08)
            puntos.add(dot)
        
        self.play(
            LaggedStart(
                *[Create(dot) for dot in puntos],
                lag_ratio=0.3
            ),
            run_time=1.5
        )
        
        self.wait(1)
        
        # Explicación
        explicacion = Text("La rosa de 4 pétalos es una curva polar", font_size=28, color=BLACK)
        explicacion.to_corner(DR, buff=0.3)
        self.play(Write(explicacion))
        self.wait(2)
        
        # Resaltar ecuación
        self.play(
            ecuacion.animate.set_color(BLUE),
            a_valor.animate.set_color(BLUE),
            run_time=0.5
        )
        
        self.wait(1)
        
        # Limpiar
        self.play(FadeOut(explicacion))
        
        # Propiedades
        propiedades = Rectangle(
            width=5.5, height=2.8,
            color=GREEN,
            stroke_width=2,
            fill_opacity=0.1,
            fill_color=GREEN
        )
        propiedades.to_corner(UL, buff=0.3)
        
        texto_prop = VGroup(
            Text("Propiedades:", font_size=24, color=GREEN, weight=BOLD),
            Text("• 4 pétalos simétricos", font_size=22, color=BLACK),
            Text("• Longitud del pétalo: a = 3", font_size=22, color=BLACK),
            Text("• Simetría rotacional de 90°", font_size=22, color=BLACK),
            Text("• r = a·cos(nθ) → 2n pétalos", font_size=22, color=BLACK)
        )
        texto_prop.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        texto_prop.move_to(propiedades.get_center())
        
        self.play(Create(propiedades), Write(texto_prop))
        self.wait(2)
        
        # Mostrar resumen final
        self.play(
            FadeOut(propiedades), FadeOut(texto_prop),
            FadeOut(ejes), FadeOut(etiqueta_x), FadeOut(etiqueta_y),
            FadeOut(puntos)
        )
        
        # Ecuación final centrada
        self.play(
            rosa.animate.move_to(ORIGIN).scale(0.8),
            titulo.animate.scale(0.7).to_edge(UP),
            ecuacion.animate.scale(0.7).next_to(titulo, DOWN, buff=0.2),
            a_valor.animate.scale(0.7).next_to(ecuacion, DOWN, buff=0.1),
            run_time=1.5
        )
        
        # Recuadro final
        final_recuadro = SurroundingRectangle(rosa, color=GOLD, buff=0.3, stroke_width=4)
        self.play(Create(final_recuadro))
        self.wait(2)
        
        # Fundido final
        self.play(FadeOut(final_recuadro), FadeOut(rosa), FadeOut(titulo), 
                  FadeOut(ecuacion), FadeOut(a_valor))
        self.wait(0.5)