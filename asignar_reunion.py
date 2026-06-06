import pandas as pd
from datetime import datetime

def generar_cuadro_semanal():
    # Leer la base de datos que acabas de crear
    df = pd.read_excel("Congregacion_Araguaney.xlsx")
    
    # Función interna para elegir al que tiene más tiempo sin participar
    def elegir_hermano(filtro_df):
        # Ordenamos por la fecha de participación más antigua
        candidatos = filtro_df.sort_values(by="Ultima_Participacion")
        if not candidatos.empty:
            return candidatos.iloc[0]['Nombre']
        return "No disponible"

    # --- LÓGICA DE ASIGNACIÓN ---
    
    # 1. Presidente (Solo los 7 Ancianos)
    ancianos = df[df['Privilegio'] == "Anciano"]
    presidente = elegir_hermano(ancianos)
    
    # 2. Perlas Escondidas (Ancianos o los 3 Siervos Ministeriales)
    nombrados = df[df['Privilegio'].isin(["Anciano", "Siervo Min."])]
    perlas = elegir_hermano(nombrados[nombrados['Nombre'] != presidente])
    
    # 3. Lectura de la Biblia (Cualquier varón, priorizando publicadores)
    varones = df[df['Genero'] == "M"]
    lectura = elegir_hermano(varones[~varones['Nombre'].isin([presidente, perlas])])

    # --- MOSTRAR RESULTADOS ---
    print("="*30)
    print(f"PROGRAMA SUGERIDO - SEMANA {datetime.now().strftime('%d/%m/%Y')}")
    print("="*30)
    print(f"Presidente: {presidente}")
    print(f"Perlas Escondidas: {perlas}")
    print(f"Lectura de la Biblia: {lectura}")
    print("="*30)

if __name__ == "__main__":
    generar_cuadro_semanal()