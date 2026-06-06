import pandas as pd

def proponer_semana():
    # Leemos el Excel que creamos en el paso 1
    df = pd.read_excel("Congregacion_Araguaney.xlsx")
    
    # Buscamos al primer Anciano para Presidente
    ancianos = df[df['Privilegio'] == "Anciano"]
    presidente = ancianos.iloc[0]['Nombre']
    
    # Buscamos un varón para la Lectura de la Biblia
    varones = df[(df['Genero'] == "M") & (df['Nombre'] != presidente)]
    lector = varones.iloc[0]['Nombre']
    
    print("-" * 30)
    print(f"PROPUESTA PARA LA REUNIÓN:")
    print(f"Presidente: {presidente}")
    print(f"Lectura de la Biblia: {lector}")
    print("-" * 30)

proponer_semana()