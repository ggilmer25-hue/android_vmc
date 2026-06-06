from manim import *

class IntegralExponencialSeno(Scene):
    def construct(self):
        # ================= CONFIGURACIÓN DE FONDO BLANCO =================
        self.camera.background_color = WHITE
        
        # Configuración de cámara
        self.camera.frame_height = 7.0
        self.camera.frame_width = 14.0
        
        # ================= COLUMNA IZQUIERDA (Solución) =================
        # Título lado izquierdo (azul oscuro para contraste)
        titulo_izq = Text("SOLUCIÓN", font_size=28, color=BLUE, weight=BOLD)
        titulo_izq.to_corner(UL, buff=0.3)
        self.play(Write(titulo_izq))
        
        # Integral original (negro para fondo blanco)
        integral_original = MathTex(
            r"\int e^x \sin(x) \, dx",
            font_size=40,
            color=BLACK
        )
        integral_original.next_to(titulo_izq, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(integral_original))
        
        # Espacio para la solución final
        solucion_final = MathTex(
            r"=",
            font_size=40,
            color=DARK_BROWN
        )
        solucion_final.next_to(integral_original, RIGHT, buff=0.3)
        
        # ================= COLUMNA DERECHA (Desarrollo) =================
        titulo_der = Text("DESARROLLO", font_size=28, color=BLUE, weight=BOLD)
        titulo_der.to_corner(UR, buff=0.3)
        self.play(Write(titulo_der))
        
        # Paso 1: Integración por partes
        # Mostrar fórmula
        formula = MathTex(
            r"\int u \, dv = uv - \int v \, du",
            font_size=32,
            color=DARK_BROWN
        )
        formula.next_to(titulo_der, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(formula))
        self.wait(0.5)
        
        # Línea separadora vertical
        linea = Line(
            start=UP * 3.5,
            end=DOWN * 3.5,
            color=GRAY,
            stroke_width=2
        )
        linea.move_to(ORIGIN)
        self.play(Create(linea))
        
        # Liberar espacio eliminando fórmula
        self.play(FadeOut(formula))
        
        # ================= PRIMERA INTEGRACIÓN POR PARTES =================
        paso1_title = Text("Paso 1:", font_size=24, color=DARK_BROWN)
        paso1_title.next_to(titulo_der, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(paso1_title))
        
        u1 = MathTex(r"u = e^x", font_size=32, color=BLACK)
        dv1 = MathTex(r"dv = \sin(x) \, dx", font_size=32, color=BLACK)
        
        u1.next_to(paso1_title, DOWN, buff=0.3, aligned_edge=LEFT)
        dv1.next_to(u1, DOWN, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(u1), Write(dv1))
        self.wait(0.5)
        
        du1 = MathTex(r"du = e^x \, dx", font_size=30, color=BLACK)
        v1 = MathTex(r"v = -\cos(x)", font_size=30, color=BLACK)
        
        du1.next_to(dv1, DOWN, buff=0.3, aligned_edge=LEFT)
        v1.next_to(du1, DOWN, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(du1), Write(v1))
        self.wait(0.5)
        
        aplicacion1 = MathTex(
            r"\int e^x \sin x \, dx = e^x(-\cos x) - \int(-\cos x)e^x dx",
            font_size=26,
            color=BLACK
        )
        aplicacion1.next_to(v1, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(aplicacion1))
        self.wait(0.8)
        
        simplif1 = MathTex(
            r"= -e^x \cos x + \int e^x \cos x \, dx",
            font_size=28,
            color=DARK_BROWN
        )
        simplif1.next_to(aplicacion1, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(Write(simplif1))
        self.wait(1)
        
        # Actualizar solución en columna izquierda
        solucion_parcial = MathTex(
            r"= -e^x \cos x + \int e^x \cos x \, dx",
            font_size=36,
            color=BLACK
        )
        solucion_parcial.move_to(solucion_final)
        self.play(Transform(solucion_final, solucion_parcial))
        
        # Limpiar desarrollo
        self.play(
            FadeOut(u1), FadeOut(dv1), FadeOut(du1), FadeOut(v1),
            FadeOut(aplicacion1), FadeOut(paso1_title)
        )
        
        # ================= SEGUNDA INTEGRACIÓN POR PARTES =================
        paso2_title = Text("Paso 2:", font_size=24, color=DARK_BROWN)
        paso2_title.next_to(simplif1, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(paso2_title))
        
        u2 = MathTex(r"u = e^x", font_size=32, color=BLACK)
        dv2 = MathTex(r"dv = \cos(x) \, dx", font_size=32, color=BLACK)
        
        u2.next_to(paso2_title, DOWN, buff=0.3, aligned_edge=LEFT)
        dv2.next_to(u2, DOWN, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(u2), Write(dv2))
        self.wait(0.5)
        
        du2 = MathTex(r"du = e^x \, dx", font_size=30, color=BLACK)
        v2 = MathTex(r"v = \sin(x)", font_size=30, color=BLACK)
        
        du2.next_to(dv2, DOWN, buff=0.3, aligned_edge=LEFT)
        v2.next_to(du2, DOWN, buff=0.15, aligned_edge=LEFT)
        
        self.play(Write(du2), Write(v2))
        self.wait(0.5)
        
        aplicacion2 = MathTex(
            r"\int e^x \cos x \, dx = e^x \sin x - \int e^x \sin x \, dx",
            font_size=26,
            color=BLACK
        )
        aplicacion2.next_to(v2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(aplicacion2))
        self.wait(0.8)
        
        self.play(
            FadeOut(u2), FadeOut(dv2), FadeOut(du2), FadeOut(v2),
            FadeOut(paso2_title)
        )
        
        # ================= SUSTITUCIÓN =================
        paso3_title = Text("Paso 3: Sustituir", font_size=24, color=DARK_BROWN)
        paso3_title.next_to(aplicacion2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(paso3_title))
        
        sustitucion = MathTex(
            r"\int e^x \sin x \, dx = -e^x \cos x + \left[ e^x \sin x - \int e^x \sin x \, dx \right]",
            font_size=24,
            color=BLACK
        )
        sustitucion.next_to(paso3_title, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(sustitucion))
        self.wait(0.8)
        
        simplif2 = MathTex(
            r"= -e^x \cos x + e^x \sin x - \int e^x \sin x \, dx",
            font_size=26,
            color=DARK_BROWN
        )
        simplif2.next_to(sustitucion, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(Write(simplif2))
        self.wait(1)
        
        self.play(
            FadeOut(paso3_title), FadeOut(aplicacion2), 
            FadeOut(sustitucion)
        )
        
        # ================= ÁLGEBRA FINAL =================
        paso4_title = Text("Paso 4: Despejar", font_size=24, color=DARK_BROWN)
        paso4_title.next_to(simplif2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(paso4_title))
        
        algebra1 = MathTex(
            r"\int e^x \sin x \, dx + \int e^x \sin x \, dx = e^x \sin x - e^x \cos x",
            font_size=26,
            color=BLACK
        )
        algebra1.next_to(paso4_title, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(algebra1))
        self.wait(0.5)
        
        algebra2 = MathTex(
            r"2\int e^x \sin x \, dx = e^x(\sin x - \cos x)",
            font_size=28,
            color=GREEN
        )
        algebra2.next_to(algebra1, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(Write(algebra2))
        self.wait(0.8)
        
        # ================= RESULTADO FINAL =================
        self.play(
            FadeOut(paso4_title), FadeOut(algebra1),
            simplif2.animate.scale(0.7).to_corner(DR, buff=0.3),
            algebra2.animate.scale(0.7).next_to(simplif2, DOWN, buff=0.1, aligned_edge=LEFT)
        )
        
        # Resultado final (negro o azul oscuro para fondo blanco)
        resultado = MathTex(
            r"\int e^x \sin x \, dx = \frac{e^x}{2}\left( \sin x - \cos x \right) + C",
            font_size=38,
            color=BLUE
        )
        resultado.move_to(integral_original.get_center() + RIGHT * 1.5)
        resultado.align_to(integral_original, LEFT)
        
        self.play(
            Transform(solucion_final, resultado),
            FadeOut(integral_original)
        )
        
        self.play(
            solucion_final.animate.move_to(LEFT * 3.5, aligned_edge=LEFT),
            run_time=0.8
        )
        
        self.wait(1.5)
        
        # ================= COMPROBACIÓN =================
        check_text = Text("✓ Comprobación:", font_size=24, color=BLUE)
        check_text.next_to(algebra2, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(check_text))
        
        derivada = MathTex(
            r"\frac{d}{dx}\left[\frac{e^x}{2}(\sin x - \cos x)\right] = e^x \sin x",
            font_size=24,
            color=BLACK
        )
        derivada.next_to(check_text, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(Write(derivada))
        
        check = MathTex(r"\checkmark", font_size=32, color=GREEN)
        check.next_to(derivada, RIGHT, buff=0.2)
        self.play(Write(check))
        self.wait(1)
        
        # ================= ENFOQUE FINAL =================
        self.play(
            FadeOut(check_text), FadeOut(derivada), FadeOut(check),
            FadeOut(simplif2), FadeOut(algebra2), FadeOut(titulo_der),
            FadeOut(linea)
        )
        
        # Centrar solución final
        self.play(
            self.camera.animate.scale(1.3),
            solucion_final.animate.move_to(ORIGIN).scale(1.1),
            titulo_izq.animate.move_to(UP * 3.5).scale(0.8),
            run_time=1.5
        )
        
        # Recuadro final azul (para fondo blanco)
        rect_final = SurroundingRectangle(
            solucion_final, 
            color=BLUE, 
            buff=0.2, 
            stroke_width=3,
            corner_radius=0.1
        )
        self.play(Create(rect_final))
        self.wait(2)
        
        self.play(FadeOut(rect_final), FadeOut(solucion_final), FadeOut(titulo_izq))
        self.wait(0.5)

# Renderizar: manim -pql integral_seno.py IntegralExponencialSeno