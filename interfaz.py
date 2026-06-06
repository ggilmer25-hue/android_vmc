import customtkinter as ctk
import pandas as pd
import random

def generar_cuadro_completo():
    try:
        df = pd.read_excel("Congregacion_Araguaney.xlsx")
        
        # --- SELECCIÓN LÓGICA POR PRIVILEGIOS ---
        ancianos = df[df['Privilegio'] == "Anciano"]
        nombrados = df[df['Privilegio'].isin(["Anciano", "Siervo Min."])]
        varones = df[df['Genero'] == "M"]
        hermanas = df[df['Genero'] == "F"]

        # Asignaciones Principales
        presi = random.choice(ancianos['Nombre'].tolist())
        oracion = random.choice(nombrados[nombrados['Nombre'] != presi]['Nombre'].tolist())
        
        # Tesoros (Num 1, 2, 3)
        num1 = random.choice(ancianos['Nombre'].tolist())
        num2 = random.choice(nombrados['Nombre'].tolist())
        num3 = random.choice(varones['Nombre'].tolist())
        
        # Maestros (Num 4, 5, 6) - Parejas de estudio
        h_estud = random.sample(hermanas['Nombre'].tolist(), 6) # 3 parejas de hermanas
        num4 = f"{h_estud[0]} // {h_estud[1]}"
        num5 = f"{h_estud[2]} // {h_estud[3]}"
        num6 = f"{h_estud[4]} // {h_estud[5]}"
        
        # Vida Cristiana (Num 7, 8 y Estudio)
        num7 = random.choice(varones['Nombre'].tolist())
        estudio_biblico = random.choice(ancianos['Nombre'].tolist())
        lector_biblico = random.choice(varones[varones['Nombre'] != estudio_biblico]['Nombre'].tolist())

        # --- FORMATO VISUAL ESTILO CUADRO ---
        cuadro = (
            f"VIDA Y MINISTERIO CRISTIANOS\n"
            f"PRESIDENTE: {presi} | ORACIÓN: {oracion}\n"
            f"{'-'*60}\n"
            f"TESOROS DE LA BIBLIA          | SEAMOS MEJORES MAESTROS      | NUESTRA VIDA CRISTIANA\n"
            f"\n"
            f"NUM 1: {num1[:18]:<18} | NUM 4: {num4[:22]:<22} | NUM 7: {num7}\n"
            f"NUM 2: {num2[:18]:<18} | NUM 5: {num5[:22]:<22} | NUM 8:\n"
            f"NUM 3: {num3[:18]:<18} | NUM 6: {num6[:22]:<22} | ESTUDIO: {estudio_biblico}\n"
            f"{' '*45} | LECTURA: {lector_biblico}\n"
            f"{'-'*60}\n"
            f"Sonido:            Plataforma:            Microfonos:            Acomodadores:"
        )
        
        label_resultado.configure(text=cuadro)
    except Exception as e:
        label_resultado.configure(text=f"Error al leer Excel: {e}")

# --- INTERFAZ GRÁFICA ---
ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Generador de Cuadro - El Araguaney")
app.geometry("850x600")

ctk.CTkLabel(app, text="VIDA Y MINISTERIO CRISTIANOS", font=("Arial", 24, "bold")).pack(pady=20)

btn = ctk.CTkButton(app, text="GENERAR CUADRO SEMANAL", command=generar_cuadro_completo, 
                     height=50, width=300, font=("Arial", 16, "bold"))
btn.pack(pady=10)

# Usamos fuente 'Courier' o 'Consolas' para que las columnas queden alineadas
label_resultado = ctk.CTkLabel(app, text="Presiona el botón para generar el formato", 
                                font=("Consolas", 14), justify="left", 
                                anchor="w", compound="left")
label_resultado.pack(pady=30, padx=20, fill="both")

app.mainloop()