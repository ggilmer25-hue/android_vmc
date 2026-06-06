import re

file_path = 'coordinacion_vmc.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modo oscuro
content = content.replace('ctk.set_appearance_mode("Light")', 'ctk.set_appearance_mode("Dark")')

# 2. Paleta de colores más moderna
content = re.sub(r'COLOR_TREASURES = ".*?"', 'COLOR_TREASURES = "#546E7A"', content)
content = re.sub(r'COLOR_MINISTRY = ".*?"', 'COLOR_MINISTRY = "#F57C00"', content)
content = re.sub(r'COLOR_LIFE = ".*?"', 'COLOR_LIFE = "#D32F2F"', content)
content = re.sub(r'COLOR_PURPLE = ".*?"', 'COLOR_PURPLE = "#512DA8"', content)
content = re.sub(r'COLOR_SUCCESS = ".*?"', 'COLOR_SUCCESS = "#00C853"', content)
content = re.sub(r'COLOR_ACCENT = ".*?"', 'COLOR_ACCENT = "#2962FF"', content)

# 3. Remover fondos blancos/grises que rompen el modo oscuro
content = content.replace('fg_color="white"', 'fg_color="transparent"')
content = content.replace("fg_color='white'", 'fg_color="transparent"')
content = content.replace('fg_color="#F9F9F9"', 'fg_color="transparent"')
content = content.replace('fg_color="#F5F5F5"', 'fg_color="transparent"')
content = content.replace('fg_color="#EEE"', 'fg_color="transparent"')
content = content.replace('fg_color="#F0F0F0"', 'fg_color="transparent"')

# 4. Ajustar text_color oscuro que no se vea en fondo oscuro
content = content.replace('text_color="black"', '')
content = content.replace('text_color="#333"', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("UI updated successfully.")
