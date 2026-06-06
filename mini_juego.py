from manim import *

class MiniJuegoMatematico(Scene):
    def construct(self):
        # ================= CONFIGURACIÓN =================
        self.camera.background_color = WHITE
        puntuacion = 0
        
        # Panel de puntuación
        marcador = Text("Puntuación: 0 | Nivel: 1", font_size=24, color=BLACK)
        marcador.to_corner(UL)
        self.add(marcador)
        
        # ================= PROBLEMA 1 =================
        pregunta1 = Text("¿Cuánto es 2³?", font_size=48, color=BLUE)
        pregunta1.move_to(ORIGIN)
        self.play(Write(pregunta1))
        self.wait(0.5)
        
        opciones1 = VGroup(
            Text("6", font_size=40),
            Text("8", font_size=40),
            Text("10", font_size=40)
        ).arrange(RIGHT, buff=1.5)
        opciones1.next_to(pregunta1, DOWN, buff=0.8)
        self.play(Write(opciones1))
        self.wait(0.5)
        
        # Resaltar respuesta correcta
        self.play(opciones1[1].animate.set_color(GREEN))
        puntuacion = 10
        
        # Actualizar marcador
        nuevo_marcador = Text(f"Puntuación: {puntuacion} | Nivel: 1", 
                              font_size=24, color=BLACK)
        nuevo_marcador.to_corner(UL)
        self.play(Transform(marcador, nuevo_marcador))
        
        self.wait(1)
        self.play(FadeOut(pregunta1), FadeOut(opciones1))
        
        # ================= PROBLEMA 2 =================
        pregunta2 = Text("¿Cuál es la derivada de x²?", font_size=48, color=BLUE)
        pregunta2.move_to(ORIGIN)
        self.play(Write(pregunta2))
        self.wait(0.5)
        
        opciones2 = VGroup(
            MathTex("x", font_size=40),
            MathTex("2x", font_size=40),
            MathTex("x^2", font_size=40)
        ).arrange(RIGHT, buff=1.5)
        opciones2.next_to(pregunta2, DOWN, buff=0.8)
        self.play(Write(opciones2))
        self.wait(0.5)
        
        # Resaltar respuesta correcta
        self.play(opciones2[1].animate.set_color(GREEN))
        puntuacion = 20
        
        # Actualizar marcador
        nuevo_marcador = Text(f"Puntuación: {puntuacion} | Nivel: 2", 
                              font_size=24, color=BLACK)
        nuevo_marcador.to_corner(UL)
        self.play(Transform(marcador, nuevo_marcador))
        
        self.wait(1)
        self.play(FadeOut(pregunta2), FadeOut(opciones2))
        
        # ================= PROBLEMA 3 =================
        pregunta3 = Text("¿Cuánto es la raíz cuadrada de 64?", font_size=48, color=BLUE)
        pregunta3.move_to(ORIGIN)
        self.play(Write(pregunta3))
        self.wait(0.5)
        
        opciones3 = VGroup(
            Text("6", font_size=40),
            Text("7", font_size=40),
            Text("8", font_size=40)
        ).arrange(RIGHT, buff=1.5)
        opciones3.next_to(pregunta3, DOWN, buff=0.8)
        self.play(Write(opciones3))
        self.wait(0.5)
        
        # Resaltar respuesta correcta
        self.play(opciones3[2].animate.set_color(GREEN))
        puntuacion = 30
        
        # Actualizar marcador
        nuevo_marcador = Text(f"Puntuación: {puntuacion} | Nivel: 3", 
                              font_size=24, color=BLACK)
        nuevo_marcador.to_corner(UL)
        self.play(Transform(marcador, nuevo_marcador))
        
        self.wait(1)
        self.play(FadeOut(pregunta3), FadeOut(opciones3))
        
        # ================= RESULTADO FINAL =================
        resultado = Text(f"¡Juego completado! Puntuación final: {puntuacion}", 
                        font_size=40, color=GOLD)
        resultado.move_to(ORIGIN)
        self.play(Write(resultado))
        self.wait(3)
        
        # Animación final
        self.play(resultado.animate.scale(1.2))
        self.wait(1)
            # Mostrar pregunta
            pregunta = MathTex(problema["pregunta"], font_size=48, color=BLUE)
            pregunta.move_to(ORIGIN)
            self.play(Write(pregunta))
            self.wait(1)
            
            # Mostrar opciones
            opciones = VGroup()
            for j, opcion in enumerate(problema["opciones"]):
                texto = MathTex(opcion, font_size=36)
                opciones.add(texto)
            opciones.arrange(RIGHT, buff=1.5)
            opciones.next_to(pregunta, DOWN, buff=0.8)
            
            self.play(Write(opciones))
            
            # Resaltar respuesta correcta (simulando selección)
            respuesta_correcta = problema["respuesta"]
            for opcion in opciones:
                if opcion.get_tex_string() == respuesta_correcta:
                    self.play(opcion.animate.set_color(GREEN))
                    puntuacion += 10
                    break
            
            self.wait(1)
            
            # Actualizar marcador
            nuevo_marcador = Text(f"Puntuación: {puntuacion} | Nivel: {i+1}", 
                                  font_size=24, color=BLACK)
            nuevo_marcador.to_corner(UL)
            self.play(Transform(marcador, nuevo_marcador))
            
            # Limpiar para siguiente pregunta
            self.play(FadeOut(pregunta), FadeOut(opciones))
            
            if i < len(problemas) - 1:
                siguiente = Text(f"¡Siguiente nivel!", font_size=32, color=GREEN)
                self.play(Write(siguiente))
                self.wait(1)
                self.play(FadeOut(siguiente))
        
        # Resultado final
        resultado = Text(f"¡Juego completado! Puntuación final: {puntuacion}", 
                        font_size=40, color=GOLD)
        resultado.move_to(ORIGIN)
        self.play(Write(resultado))
        self.wait(3)