import pandas as pd

# Datos de la congregación basados en tus documentos
data = {
    "Nombre": [
        "Rafael Guanipa", "Javier Alvarado", "Gladys De Guanipa", "Yujeilin De Márquez", "María Márquez", "Luis Márquez", "Johan Decaro", "Maribel De Decaro", "Angel Decaro", "Margarita Robertis", "Juana Robertis", "Anel Rodríguez", "Nora De Rodríguez",
        "Gilmer González", "Gilmer de Jesús G.", "Rosangela De González", "Robert González", "Andy González", "Nellys De Pérez", "Yonnell Pérez", "Yohander Pérez", "Pastora De Fonseca", "Haydee Rangel", "Yesenia Rangel", "Yetzai Guaidó", "Yetzibe Guaidó",
        "Gonzalo Sayago", "Rafael Torrealba", "Jhon Hurtado", "Fabiana De Pineda", "Reymar Pineda", "Doralia Vazquez", "Luisa Castillo", "Jassiel Mendoza", "Roger Castillo", "Maritza De Torrealba", "Eleazar Saavedra", "Lida Cañizales", "Maryelis Godoy",
        "Engelberth Oviol", "Jhonny Adán", "Faviola De Oviol", "Fernando La Cruz", "Birlandy De Rojo", "Francis Rojo", "Gregoria Domoromo", "Zoila De Adán", "Claricza Adán", "Angeles Adán", "María Espinoza",
        "Jhovannys Suárez", "Alexis Contreras", "Yaritza De Contreras", "Yariannys Contreras", "Emilio Carreño", "Maria De Carreño", "Emelyn Carreño", "Eimy Vasquez", "Eleazar Carreño", "Petra Evies",
        "Raúl Cordero", "Jhonatan Goyo", "Alvaro Patiño", "Johana De Patiño", "Alvaro I Patiño", "Lorena De Patiño", "María Patiño", "Santiago Goyo", "Naiyolis De Rodríguez", "Enyelberth Rodríguez", "Kharla Rodríguez", "Damaris De Rodríguez", "Jeismarys Rodríguez", "Adriannys Parra", "Jeisimar Rodríguez",
        "David Cordero", "Engelberth Oviol M", "Nathalia Cordero", "Alexandra De Martinez", "Aleximar Cordero", "Diana De Oviol", "Sebastian Oviol", "Alis Fernández", "Rafael Suárez"
    ],
    "Grupo": [1]*13 + [2]*13 + [3]*13 + [4]*11 + [5]*10 + [6]*15 + [7]*9,
    "Privilegio": [
        "Anciano", "Siervo Min.", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Siervo Min.", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Siervo Min.", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador",
        "Anciano", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador", "Publicador"
    ],
    "Genero": ["M", "M", "F", "F", "F", "M", "M", "F", "M", "F", "F", "M", "F"] + 
              ["M", "M", "F", "M", "M", "F", "M", "M", "F", "F", "F", "F", "F"] +
              ["M", "M", "M", "F", "F", "F", "F", "M", "M", "F", "M", "F", "F"] +
              ["M", "M", "F", "M", "F", "F", "F", "F", "F", "F", "F"] +
              ["M", "M", "F", "F", "M", "F", "F", "F", "M", "F"] +
              ["M", "M", "M", "F", "M", "F", "F", "M", "F", "M", "F", "F", "F", "F", "F"] +
              ["M", "M", "F", "F", "F", "F", "M", "F", "M"],
    "Ultima_Participacion": ["2026-01-01"] * 84 
}

df = pd.DataFrame(data)
df.to_excel("Congregacion_Araguaney.xlsx", index=False)
print("ÉXITO: Se ha creado la lista de 84 hermanos.")