import flet as ft
import json
import os
import random
import urllib.parse
import sys
import threading
from datetime import datetime, date, timedelta

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from jw_scraper import JWScraper
    JW_AVAILABLE = True
except ImportError:
    JW_AVAILABLE = False


# ==========================================
# ALGORITMO Y CORE DE ASIGNACIONES (VMC)
# ==========================================
class AsignadorVMCMovil:
    def __init__(self, congregacion_data, historial_inicial=None):
        self.publicadores = congregacion_data
        self.historial_maestros = historial_inicial if historial_inicial else {}
        
        # Clasificar listas base
        self.ancianos = [p['Nombre'] for p in self.publicadores if p.get('Privilegio') == 'Anciano' and p.get('Genero') == 'M']
        self.siervos = [p['Nombre'] for p in self.publicadores if p.get('Privilegio') == 'Siervo Min.' and p.get('Genero') == 'M']
        self.todos_varones = [p['Nombre'] for p in self.publicadores if p.get('Genero') == 'M']
        self.hermanas = [p['Nombre'] for p in self.publicadores if p.get('Genero') == 'F']
        
        self.inicializar_pools()

    def inicializar_pools(self):
        # Exclusión de Rafael Torrealba de Tesoros y Vida Cristiana
        candidatos_tesoros = [v for v in self.todos_varones if v != 'Rafael Torrealba']
        random.shuffle(candidatos_tesoros)
        self.pool_tesoros = list(candidatos_tesoros)
        
        candidatos_vida = [v for v in (self.ancianos + self.siervos) if v != 'Rafael Torrealba']
        random.shuffle(candidatos_vida)
        self.pool_vida = list(candidatos_vida)

    def es_menor(self, nombre):
        for p in self.publicadores:
            if p['Nombre'] == nombre:
                return p.get('Es_Menor', 'No') == 'Si'
        return False
        
    def comparten_apellido(self, nombre1, nombre2):
        if not nombre1 or not nombre2 or "______" in nombre1 or "______" in nombre2:
            return False
        ap1 = nombre1.split()[-1].lower() if len(nombre1.split()) > 1 else nombre1.lower()
        ap2 = nombre2.split()[-1].lower() if len(nombre2.split()) > 1 else nombre2.lower()
        return ap1 == ap2

    def candidato_valido_maestros(self, persona, semana_num):
        ultima = self.historial_maestros.get(persona, -99)
        return (semana_num - ultima) >= 6

    def asignar_desde_pool(self, pool, lista_candidatos_base, asignados_semana, evitar=None):
        disponibles = [p for p in pool if p not in asignados_semana and p != evitar and p in lista_candidatos_base]
        if not disponibles:
            base = [v for v in lista_candidatos_base if v != 'Rafael Torrealba']
            random.shuffle(base)
            pool.extend(base)
            disponibles = [p for p in pool if p not in asignados_semana and p != evitar and p in lista_candidatos_base]
            
        if not disponibles:
            return "__________________"
            
        seleccionado = disponibles[0]
        pool.remove(seleccionado)
        asignados_semana.add(seleccionado)
        return seleccionado

    def asignar_persona(self, lista_candidatos, asignados_semana, evitar=None):
        disponibles = [p for p in lista_candidatos if p not in asignados_semana and p != evitar]
        if not disponibles:
            return "__________________"
        seleccionado = random.choice(disponibles)
        asignados_semana.add(seleccionado)
        return seleccionado

    def asignar_pareja_generica(self, asignados_semana, semana_num, pool_titulares, pool_ayudantes_base, permite_familiar_opuesto=False):
        titulares_disp = [t for t in pool_titulares if t not in asignados_semana and self.candidato_valido_maestros(t, semana_num)]
        if not titulares_disp:
            titulares_disp = [t for t in pool_titulares if t not in asignados_semana]
            
        if not titulares_disp: 
            return "__________________ // __________________"
        titular = random.choice(titulares_disp)
        
        pool_ayudantes = list(pool_ayudantes_base)
        if permite_familiar_opuesto and random.random() < 0.3:
            es_mujer = titular in self.hermanas
            pool_opuesto = self.todos_varones if es_mujer else self.hermanas
            fam_opuestos = [p for p in pool_opuesto if self.comparten_apellido(titular, p)]
            if fam_opuestos:
                pool_ayudantes.extend(fam_opuestos * 3)
        
        ayudantes_disp = [a for a in pool_ayudantes if a not in asignados_semana and a != titular and self.candidato_valido_maestros(a, semana_num)]
        if not ayudantes_disp:
            ayudantes_disp = [a for a in pool_ayudantes if a not in asignados_semana and a != titular]
            
        ayudantes_validos = []
        for a in ayudantes_disp:
            if self.es_menor(a) and not self.es_menor(titular):
                if not self.comparten_apellido(titular, a):
                    continue
            ayudantes_validos.append(a)
            
        if not ayudantes_validos:
            asignados_semana.add(titular)
            self.historial_maestros[titular] = semana_num
            return f"{titular} // __________________"
            
        ayudante = random.choice(ayudantes_validos)
        asignados_semana.add(titular)
        asignados_semana.add(ayudante)
        self.historial_maestros[titular] = semana_num
        self.historial_maestros[ayudante] = semana_num
        
        return f"{titular} // {ayudante}"

    def asignar_estudiante_solo_con_pool(self, asignados_semana, semana_num, pool):
        disp = [p for p in pool if p not in asignados_semana and self.candidato_valido_maestros(p, semana_num)]
        if not disp:
            disp = [p for p in pool if p not in asignados_semana]
        if not disp: 
            return "__________________"
        p = random.choice(disp)
        asignados_semana.add(p)
        self.historial_maestros[p] = semana_num
        return p

    def generar_semana(self, index_semana, fecha, lectura, asigs_maestros):
        asignados = set()
        
        # PRESIDENTE & ORACIÓN
        presidente = self.asignar_persona(self.ancianos, asignados)
        
        list_oracion = [p['Nombre'] for p in self.publicadores if p.get('Hab_Oracion') == 'Si' and p.get('Genero') == 'M']
        oracion = self.asignar_persona(list_oracion if list_oracion else self.todos_varones, asignados)
        
        # TESOROS
        list_tes_discurso = [p['Nombre'] for p in self.publicadores if p.get('Hab_Tes_Discurso') == 'Si' and p.get('Genero') == 'M']
        list_tes_perlas = [p['Nombre'] for p in self.publicadores if p.get('Hab_Tes_Perlas') == 'Si' and p.get('Genero') == 'M']
        list_lectores_biblia = [p['Nombre'] for p in self.publicadores if p.get('Hab_Lectura') == 'Si']
        
        num1_tesoros = self.asignar_desde_pool(self.pool_tesoros, list_tes_discurso if list_tes_discurso else self.pool_tesoros, asignados)
        num2_tesoros = self.asignar_desde_pool(self.pool_tesoros, list_tes_perlas if list_tes_perlas else self.pool_tesoros, asignados)
        lectura_biblia = self.asignar_desde_pool(self.pool_tesoros, list_lectores_biblia if list_lectores_biblia else self.pool_tesoros, asignados)
        
        # MAESTROS
        maestros_asignaciones = []
        for asig in asigs_maestros:
            asig_lower = asig.lower()
            
            if "convers" in asig_lower:
                p_enc = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Conversacion_Enc') == 'Si']
                p_ayu = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Conversacion_Ayu') == 'Si']
            elif "revisita" in asig_lower:
                p_enc = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Revisita_Enc') == 'Si']
                p_ayu = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Revisita_Ayu') == 'Si']
            elif "discipulo" in asig_lower or "discípulo" in asig_lower:
                p_enc = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Discipulos_Enc') == 'Si']
                p_ayu = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Discipulos_Ayu') == 'Si']
            elif "escenificaci" in asig_lower or "creencias" in asig_lower:
                p_enc = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Creencias_Esc_Enc') == 'Si']
                p_ayu = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Creencias_Esc_Ayu') == 'Si']
            else:
                p_enc, p_ayu = None, None

            if p_enc:
                usar_hermanas = (random.random() < 0.8) and bool(self.hermanas)
                f_enc = [n for n in p_enc if (n in self.hermanas if usar_hermanas else n in self.todos_varones)]
                f_ayu = [n for n in p_ayu if (n in self.hermanas if usar_hermanas else n in self.todos_varones)]
                if not f_enc: f_enc = p_enc
                if not f_ayu: f_ayu = p_ayu
                
                res = self.asignar_pareja_generica(asignados, index_semana, f_enc, f_ayu, permite_familiar_opuesto=True)
                maestros_asignaciones.append([asig, res])
            elif "creencias" in asig_lower:
                pool = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Creencias_Dis') == 'Si']
                res = self.asignar_estudiante_solo_con_pool(asignados, index_semana, pool if pool else self.todos_varones)
                maestros_asignaciones.append([asig, res])
            else:
                pool = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mae_Discurso') == 'Si']
                res = self.asignar_estudiante_solo_con_pool(asignados, index_semana, pool if pool else self.todos_varones)
                maestros_asignaciones.append([asig, res])
                
        # VIDA CRISTIANA
        list_vida_p1 = [p['Nombre'] for p in self.publicadores if p.get('Hab_Vida_Parte1') == 'Si']
        num1_vida = self.asignar_desde_pool(self.pool_vida, list_vida_p1 if list_vida_p1 else self.pool_vida, asignados)
        
        list_estudio_cond = [p['Nombre'] for p in self.publicadores if p.get('Hab_Estudio_Conductor') == 'Si']
        list_estudio_lect = [p['Nombre'] for p in self.publicadores if p.get('Hab_Estudio_Lector') == 'Si' and p.get('Genero') == 'M']
        
        estudio_biblico = self.asignar_persona(list_estudio_cond if list_estudio_cond else self.ancianos, asignados)
        lector = self.asignar_persona(list_estudio_lect if list_estudio_lect else self.todos_varones, asignados, evitar=estudio_biblico)
        presidencia_aux = self.asignar_persona(self.ancianos, asignados)
        
        # SERVICIOS
        list_sonido = [p['Nombre'] for p in self.publicadores if p.get('Hab_Sonido') == 'Si' and p.get('Genero') == 'M']
        list_plat = [p['Nombre'] for p in self.publicadores if p.get('Hab_Plataforma') == 'Si' and p.get('Genero') == 'M']
        list_mics = [p['Nombre'] for p in self.publicadores if p.get('Hab_Mics') == 'Si' and p.get('Genero') == 'M']
        list_acom = [p['Nombre'] for p in self.publicadores if p.get('Hab_Acomodador') == 'Si' and p.get('Genero') == 'M']
        
        sonido1 = self.asignar_persona(list_sonido if list_sonido else self.todos_varones, asignados)
        sonido2 = self.asignar_persona(list_sonido if list_sonido else self.todos_varones, asignados, evitar=sonido1)
        plataforma = self.asignar_persona(list_plat if list_plat else self.todos_varones, asignados)
        mic1 = self.asignar_persona(list_mics if list_mics else self.todos_varones, asignados)
        mic2 = self.asignar_persona(list_mics if list_mics else self.todos_varones, asignados, evitar=mic1)
        acom1 = self.asignar_persona(list_acom if list_acom else self.todos_varones, asignados)
        acom2 = self.asignar_persona(list_acom if list_acom else self.todos_varones, asignados, evitar=acom1)
        
        return {
            'fecha': fecha,
            'lectura': lectura,
            'presidente': presidente,
            'oracion': oracion,
            'num1_tesoros': num1_tesoros,
            'num2_tesoros': num2_tesoros,
            'lectura_biblia': lectura_biblia,
            'maestros': maestros_asignaciones,
            'partes_vida': [["Parte 1", num1_vida]],
            'estudio_biblico': estudio_biblico,
            'lector': lector,
            'presidencia_aux': presidencia_aux,
            'sonido': f"{sonido1} / {sonido2}" if sonido2 != "__________________" else sonido1,
            'plataforma': plataforma,
            'microfonos': f"{mic1} / {mic2}",
            'acomodadores': f"{acom1} / {acom2}",
            'no_reunion': False
        }


# ==========================================
# MOTOR DE HUMANIZACIÓN DE MENSAJES
# ==========================================
def humanizar_mensaje_movil(nombre, parte, fecha, seccion):
    saludos = [
        "Hola {nombre}, 🙂",
        "Hola, hermano {nombre}. Espero que te encuentres muy bien. 🌟",
        "Saludos, {nombre} 👋",
        "¡Hola, {nombre}! Qué gusto saludarte. 😊",
        "Buen día, {nombre}. ✨",
        "Hola {nombre}, ¿cómo estás? Espero que todo esté excelente. 🤗",
        "Estimado {nombre}, un saludo muy cordial. 🌸",
        "Hola {nombre}. ¡Espero que tengas un feliz día! ☀️",
        "Saludos cariñosos, {nombre}. ❤️"
    ]
    introducciones = [
        "Te informamos que tienes la siguiente asignación para la reunión:",
        "Te escribo para comentarte que tienes la siguiente asignación:",
        "Paso por aquí a recordarte tu asignación programada:",
        "Te comparto los detalles de tu asignación para esta semana:",
        "Aquí tienes la información sobre tu parte en la reunión:",
        "Queremos notificarte de tu participación para la reunión de esta semana:",
        "Te dejamos por acá los detalles de tu asignación VMC:"
    ]
    despedidas = [
        "¡Muchas gracias por tu servicio! 🙏",
        "¡Muchas gracias por tu excelente disposición de siempre! 🙏",
        "Que Jehová bendiga mucho tu buena actitud y tus esfuerzos. ✨",
        "Agradecemos de corazón tu valioso apoyo. ¡Un gran abrazo! 🤗",
        "Gracias por tu buena disposición de siempre. 👍",
        "¡Que tengas una bendecida y excelente semana! Saludos. 😊",
        "Agradecemos mucho tu valioso servicio a favor de la congregación. 🤝",
        "Que Jehová te acompañe en tu preparación. ¡Saludos! 📖"
    ]
    
    saludo = random.choice(saludos).format(nombre=nombre)
    intro = random.choice(introducciones)
    despedida = random.choice(despedidas)
    
    disenos = [
        f"{saludo}\n\n{intro}\n\n📋 *{parte}*\n📅 *{fecha}*\n📖 Sección: {seccion}\n\n{despedida}",
        f"{saludo}\n\n{intro}\n\n👉 *{parte}*\n📅 _Fecha: {fecha}_\n📌 Sección: {seccion}\n\n{despedida}",
        f"{saludo}\n\n{intro}\n\n✨ Asignación: *{parte}*\n📅 Semana: *{fecha}*\n📖 Sección: *{seccion}*\n\n{despedida}"
    ]
    return random.choice(disenos)

def obtener_seccion_parte_movil(parte):
    parte_lower = parte.lower()
    if any(x in parte_lower for x in ["tesoro", "perlas", "lectura de la biblia", "num 1", "num 2", "num 3", "lectura biblia"]):
        return "💎 Tesoros de la Biblia"
    elif any(x in parte_lower for x in ["convers", "revis", "discip", "creencia", "discurso", "num 4", "num 5", "num 6", "maestro"]):
        return "🤝 Seamos Mejores Maestros"
    else:
        return "🏠 Nuestra Vida Cristiana"


# ==========================================
# APLICACIÓN PRINCIPAL FLET PARA ANDROID
# ==========================================
class ClientStorageSync:
    def __init__(self, filepath):
        self.filepath = filepath
        self._load()
    def _load(self):
        import json, os
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = {}
        else:
            self.data = {}
    def _save(self):
        import json
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f)
    def get(self, key):
        return self.data.get(key)
    def set(self, key, value):
        self.data[key] = value
        self._save()
    def contains_key(self, key):
        return key in self.data
    def remove(self, key):
        if key in self.data:
            del self.data[key]
            self._save()

class VMCAndroidApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Coordinación VMC"
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.page.client_storage = ClientStorageSync(os.path.join(self.base_dir, "client_storage.json"))
        
        # Recuperar tema guardado del almacenamiento o usar LIGHT por defecto
        theme_mode_str = self.page.client_storage.get("theme_mode")
        self.page.theme_mode = ft.ThemeMode.DARK if theme_mode_str == "dark" else ft.ThemeMode.LIGHT
        

        self.page.bgcolor = ft.Colors.SURFACE

        self.archivo_excel   = os.path.join(self.base_dir, "Congregacion_Araguaney.xlsx")
        self.estado_bimestre = os.path.join(self.base_dir, "vmc_estado_bimestre.json")
        self.estado_movil    = os.path.join(self.base_dir, "vmc_datos_movil.json")
        self.historial_file  = os.path.join(self.base_dir, "vmc_historial.json")

        self.bimestre_data = []
        self.congregacion_data = []
        self.source_info = ""
        self.dirty = False  # Cambios locales no guardados

        # Registrar FilePicker para importación de datos
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self.on_file_picked
        self.page.overlay.append(self.file_picker)

        # Botón flotante para guardar cambios interactivamente
        self.save_fab = ft.FloatingActionButton(
            icon=ft.Icons.SAVE,
            text="Guardar Cambios",
            bgcolor="#4CAF50",
            color="white",
            on_click=self.guardar_cambios_locales,
            visible=False
        )
        self.page.floating_action_button = self.save_fab

        self.cargar_datos()
        self.setup_ui()

    def show_message(self, message, is_error=False):
        color = "#C62828" if is_error else "#2E7D32"
        snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white", weight="bold"),
            bgcolor=color,
            duration=4000
        )
        self.page.open(snack_bar)

    def mark_dirty(self):
        self.dirty = True
        self.save_fab.visible = True
        self.page.update()

    def cargar_datos(self):
        # 1. Intentar cargar desde el almacenamiento del cliente
        try:
            if self.page.client_storage.contains_key("vmc_data"):
                raw_data = self.page.client_storage.get("vmc_data")
                data = json.loads(raw_data)
                self.bimestre_data = data.get("bimestre", [])
                self.congregacion_data = data.get("congregacion", [])
                self.source_info = "Importado"
                self.cargar_datos_excel_habilidades()
                return
        except Exception as e:
            print(f"Error cargando desde client_storage: {e}")

        # 2. Intentar cargar desde vmc_datos_movil.json
        if os.path.exists(self.estado_movil):
            try:
                with open(self.estado_movil, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bimestre_data = data.get("bimestre", [])
                    self.congregacion_data = data.get("congregacion", [])
                    self.source_info = "Sincronizado"
                    self.cargar_datos_excel_habilidades()
                    return
            except Exception as e:
                print(f"Error cargando vmc_datos_movil.json: {e}")

        # 3. Fallback: cargar vmc_estado_bimestre.json y Excel
        self.source_info = "Desarrollo"
        self.bimestre_data = []
        self.congregacion_data = []

        try:
            if os.path.exists(self.estado_bimestre):
                with open(self.estado_bimestre, 'r', encoding='utf-8') as f:
                    self.bimestre_data = json.load(f)
        except Exception as e:
            print(f"Error al cargar estado_bimestre: {e}")

        self.cargar_datos_excel_habilidades()

    def cargar_datos_excel_habilidades(self):
        """Lee el Excel cargando todas las columnas de habilidades si pandas está listo"""
        if HAS_PANDAS and os.path.exists(self.archivo_excel):
            try:
                df = pd.read_excel(self.archivo_excel)
                df = df[~df['Nombre'].str.contains('Spolzino|Saucedo', case=False, na=False)]
                
                # Asegurar columnas esenciales
                columnas_hab = [
                    'Hab_Tes_Discurso', 'Hab_Tes_Perlas', 'Hab_Lectura',
                    'Hab_Mae_Conversacion_Enc', 'Hab_Mae_Conversacion_Ayu',
                    'Hab_Mae_Revisita_Enc', 'Hab_Mae_Revisita_Ayu',
                    'Hab_Mae_Discipulos_Enc', 'Hab_Mae_Discipulos_Ayu',
                    'Hab_Mae_Creencias_Esc_Enc', 'Hab_Mae_Creencias_Esc_Ayu',
                    'Hab_Mae_Creencias_Dis', 'Hab_Mae_Discurso',
                    'Hab_Oracion', 'Hab_Vida_Parte1', 'Hab_Vida_Parte2', 'Hab_Vida_Locales',
                    'Hab_Estudio_Conductor', 'Hab_Estudio_Lector',
                    'Hab_Sonido', 'Hab_Mics', 'Hab_Plataforma', 'Hab_Acomodador'
                ]
                
                for col in columnas_hab + ['Es_Menor', 'Telefono', 'Privilegio', 'Genero']:
                    if col not in df.columns:
                        df[col] = 'No' if col in columnas_hab + ['Es_Menor'] else ''
                
                # Convertir a tipos seguros
                df['Es_Menor'] = df['Es_Menor'].astype(str).str.strip().str.title()
                df['Telefono'] = df['Telefono'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                
                excel_dict = df.to_dict(orient='records')
                
                # Fusionar o usar el Excel como roster principal
                if not self.congregacion_data:
                    self.congregacion_data = excel_dict
                else:
                    # Enriquecer datos existentes con las habilidades del Excel
                    excel_map = {row['Nombre']: row for row in excel_dict}
                    for p in self.congregacion_data:
                        n = p.get('Nombre')
                        if n in excel_map:
                            p.update(excel_map[n])
            except Exception as e:
                print(f"Error cargando habilidades desde Excel: {e}")

    def on_file_picked(self, e):
        if not e.files:
            return
        picked_file = e.files[0]
        try:
            path = picked_file.path
            if path:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                data = json.loads(content)
                if "bimestre" in data and "congregacion" in data:
                    self.page.client_storage.set("vmc_data", content)
                    # Intentar escribir también localmente
                    with open(self.estado_movil, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.cargar_datos()
                    self.recargar()
                    self.show_message("✅ ¡Datos importados correctamente!")
                else:
                    self.show_message("❌ El JSON debe contener 'bimestre' y 'congregacion'.", is_error=True)
        except Exception as err:
            self.show_message(f"❌ Error al importar: {err}", is_error=True)

    def borrar_datos_importados(self, e):
        try:
            if self.page.client_storage.contains_key("vmc_data"):
                self.page.client_storage.remove("vmc_data")
            if os.path.exists(self.estado_movil):
                os.remove(self.estado_movil)
            self.cargar_datos()
            self.recargar()
            self.show_message("🗑️ Datos eliminados. Restablecido estado por defecto.")
        except Exception as err:
            self.show_message(f"❌ Error al borrar: {err}", is_error=True)

    def guardar_changes_to_file(self):
        try:
            data = {
                "bimestre": self.bimestre_data,
                "congregacion": self.congregacion_data
            }
            raw = json.dumps(data, ensure_ascii=False, indent=2)
            self.page.client_storage.set("vmc_data", raw)
            
            with open(self.estado_movil, 'w', encoding='utf-8') as f:
                f.write(raw)
            return True
        except Exception as err:
            print(f"Error escribiendo cambios: {err}")
            return False

    def guardar_cambios_locales(self, e):
        if self.guardar_changes_to_file():
            self.dirty = False
            self.save_fab.visible = False
            self.show_message("💾 ¡Todos los cambios han sido guardados con éxito!")
            self.recargar()
        else:
            self.show_message("❌ Error al guardar los cambios en el archivo.", is_error=True)

    def recargar(self, e=None):
        self.cargar_datos()
        idx = self.nav_bar.selected_index
        if idx == 0:
            self._mostrar_bimestre()
        elif idx == 1:
            self._mostrar_congregacion()
        else:
            self._mostrar_notificaciones()
            
        if e:
            self.show_message(f"✅ Datos actualizados ({self.source_info})")

    def toggle_theme_mode(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.client_storage.set("theme_mode", "dark")
            e.control.icon = ft.Icons.LIGHT_MODE
            e.control.tooltip = "Modo Claro"
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.client_storage.set("theme_mode", "light")
            e.control.icon = ft.Icons.DARK_MODE
            e.control.tooltip = "Modo Oscuro"
        self.page.update()

    def setup_ui(self):
        # Header premium con degradado morado y controles
        current_theme_icon = ft.Icons.LIGHT_MODE if self.page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE
        
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column([
                        ft.Text("Coordinación VMC", size=18, weight="bold", color="white"),
                        ft.Text("El Araguaney • Móvil", size=11, color="#E0D7FF"),
                    ], expand=True, spacing=1),
                    ft.IconButton(
                        icon=current_theme_icon,
                        icon_color="white",
                        tooltip="Cambiar Modo de Tema",
                        on_click=self.toggle_theme_mode,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.AUTO_AWESOME,
                        icon_color="#FFD54F",
                        tooltip="Sincronizar y Generar Bimestre",
                        on_click=self.abrir_dialogo_generar,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.FILE_OPEN,
                        icon_color="white",
                        tooltip="Importar datos (.json)",
                        on_click=lambda _: self.file_picker.pick_files(
                            allowed_extensions=["json"]
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP,
                        icon_color="#FFCDD2",
                        tooltip="Restablecer datos locales",
                        on_click=self.borrar_datos_importados,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_color="white",
                        tooltip="Recargar datos",
                        on_click=self.recargar,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor="#4A148C",
            padding=ft.Padding(left=14, right=4, top=10, bottom=10),
            border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12)
        )

        self.content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.CALENDAR_VIEW_MONTH),
                    label="Bimestre"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.PEOPLE),
                    label="Congregación"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icon(ft.Icons.SEND),
                    label="Notificaciones"
                ),
            ],
            selected_index=0,
            on_change=self._on_nav_change,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            indicator_color="#EDE7F6",
        )

        self.page.add(
            ft.Column(
                controls=[
                    header,
                    ft.Container(content=self.content_area, expand=True, padding=ft.Padding(left=10, right=10, top=5, bottom=5)),
                    self.nav_bar,
                ],
                expand=True,
                spacing=0,
            )
        )
        self._mostrar_bimestre()

    def _on_nav_change(self, e):
        idx = e.control.selected_index
        if idx == 0:
            self._mostrar_bimestre()
        elif idx == 1:
            self._mostrar_congregacion()
        else:
            self._mostrar_notificaciones()

    # ==========================================
    # MODAL DE CONFIGURACIÓN & GENERACIÓN AUTÓNOMA
    # ==========================================
    def abrir_dialogo_generar(self, e):
        # Crear los combos y campos para el diálogo de generación
        current_year = datetime.now().year
        year_dropdown = ft.Dropdown(
            label="Año",
            options=[ft.dropdown.Option(str(y)) for y in [current_year-1, current_year, current_year+1]],
            value=str(current_year),
            width=120
        )
        
        bimestres = ["Enero-Febrero", "Marzo-Abril", "Mayo-Junio", "Julio-Agosto", "Septiembre-Octubre", "Noviembre-Diciembre"]
        # Detectar actual
        mes = datetime.now().month
        bimestre_def = bimestres[(mes-1)//2]
        
        bimestre_dropdown = ft.Dropdown(
            label="Bimestre",
            options=[ft.dropdown.Option(b) for b in bimestres],
            value=bimestre_def,
            width=220
        )

        dialog_content = ft.Column([
            ft.Text("Descarga el programa oficial de JW.org y genera las asignaciones balanceadas de forma circular.", size=13),
            ft.Divider(height=10),
            year_dropdown,
            bimestre_dropdown,
            ft.Text("Esto sobrescribirá el programa actual. Asegúrate de guardar los cambios antes.", size=11, color="red")
        ], spacing=10, height=220, width=320)

        def on_generar_click(ev):
            self.page.close(dialog_sync)
            self._ejecutar_sincronizacion_y_generacion(year_dropdown.value, bimestre_dropdown.value)

        dialog_sync = ft.AlertDialog(
            title=ft.Text("🔄 Sincronizar y Generar"),
            content=dialog_content,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page.close(dialog_sync)),
                ft.ElevatedButton("Comenzar", bgcolor="#4A148C", color="white", on_click=on_generar_click)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dialog_sync)

    def _ejecutar_sincronizacion_y_generacion(self, año, bimestre_nombre):
        # Mostrar diálogo de progreso
        progreso_ring = ft.ProgressRing()
        progreso_text = ft.Text("Conectando con wol.jw.org...", size=14)
        
        self.loading_dialog = ft.AlertDialog(
            title=ft.Text("Procesando..."),
            content=ft.Row([progreso_ring, progreso_text], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            modal=True
        )
        self.page.open(self.loading_dialog)

        def background_task():
            try:
                # 1. Scraping desde JW.org si el scraper está activo
                if not JW_AVAILABLE:
                    self.page.close(self.loading_dialog)
                    self.show_message("❌ Módulo de scraper jw_scraper no disponible.", is_error=True)
                    return
                
                scraper = JWScraper()
                meses_map = {"Enero-Febrero":1, "Marzo-Abril":3, "Mayo-Junio":5, "Julio-Agosto":7, "Septiembre-Octubre":9, "Noviembre-Diciembre":11}
                mes_inicio = meses_map.get(bimestre_nombre, 5)
                
                semanas_iso = JWScraper.calcular_semanas_bimestre(int(año), mes_inicio)
                total_semanas = len(semanas_iso)
                
                resultados_guia = []
                for i, (iso_year, iso_week) in enumerate(semanas_iso):
                    progreso_text.value = f"Descargando semana {i+1}/{total_semanas}..."
                    self.page.update()
                    
                    try:
                        datos = scraper.obtener_semana(iso_year, iso_week)
                        resultados_guia.append(datos)
                    except Exception as ex:
                        # Fallback en caso de error de red
                        resultados_guia.append({
                            'fecha': f"Semana {i+1}",
                            'lectura_biblica': "Lectura bíblica",
                            'maestros': [{'tipo': 'Conversación', 'numero': 4}],
                            'no_reunion': False
                        })
                
                # 2. Inicializar el asignador teocrático
                progreso_text.value = "Generando asignaciones balanceadas..."
                self.page.update()
                
                # Cargar historial anterior para respetar reglas
                historial_maestros = {}
                if os.path.exists(self.historial_file):
                    try:
                        with open(self.historial_file, 'r', encoding='utf-8') as f:
                            historial_maestros = json.load(f)
                    except:
                        pass
                
                asignador = AsignadorVMCMovil(self.congregacion_data, historial_maestros)
                
                nuevas_semanas = []
                for idx, r in enumerate(resultados_guia):
                    # Extraer las partes de maestros que tocan
                    maestros_parts = []
                    for m in r.get('maestros', []):
                        maestros_parts.append(f"{m['tipo']} (Enc./Ayu.)")
                    
                    if not maestros_parts:
                        maestros_parts = ["Conversación (Enc./Ayu.)", "Revisita (Enc./Ayu.)", "Discipulado (Enc./Ayu.)"]
                        
                    res_semana = asignador.generar_semana(
                        index_semana=idx+1,
                        fecha=r.get('fecha', f"Semana {idx+1}"),
                        lectura=r.get('lectura_biblica', 'Lectura Semanal'),
                        asigs_maestros=maestros_parts
                    )
                    nuevas_semanas.append(res_semana)
                
                # Guardar en variables de estado
                self.bimestre_data = nuevas_semanas
                
                # Guardar el historial de maestros actualizado
                with open(self.historial_file, 'w', encoding='utf-8') as f:
                    json.dump(asignador.historial_maestros, f, ensure_ascii=False, indent=2)
                
                # Guardar los datos del bimestre
                self.dirty = True
                self.guardar_changes_to_file()
                self.dirty = False
                
                self.page.close(self.loading_dialog)
                self.show_message("🎉 ¡Bimestre e Historial generados con éxito!")
                self.recargar()
                
            except Exception as e:
                self.page.close(self.loading_dialog)
                self.show_message(f"❌ Error al generar: {e}", is_error=True)
        
        threading.Thread(target=background_task).start()


    # ==========================================
    # DETALLE DE LA PESTAÑA 1: VISTA DE SEMANAS
    # ==========================================
    def _mostrar_bimestre(self):
        self.content_area.controls.clear()

        if not self.bimestre_data:
            self.content_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.EVENT_BUSY, size=64, color="#BDBDBD"),
                        ft.Text("Sin bimestre generado", size=16, weight="bold", color="#9E9E9E", text_align=ft.TextAlign.CENTER),
                        ft.Text("Pulsa el botón de varita mágica (Sincronizar) arriba para importar de JW.org o importa un JSON teocrático.",
                                size=13, color="#BDBDBD", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                )
            )
            self.page.update()
            return

        for sem_idx, semana in enumerate(self.bimestre_data):
            if semana.get('no_reunion', False):
                motivo = semana.get('motivo', 'Semana cancelada')
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.BLOCK, color="red"),
                            ft.Column([
                                ft.Text(motivo.upper(), weight="bold", color="red", size=14),
                                ft.Text(semana.get('fecha',''), size=12, color="#9E9E9E"),
                            ])
                        ]),
                        padding=15,
                    ),
                    color="#FFEBEE",
                )
            else:
                # Contenedor de la semana
                week_title_bg = "#4A148C" if not self.page.theme_mode == ft.ThemeMode.DARK else "#311B92"
                
                card_content = ft.Column(spacing=0)
                
                # Encabezado de la semana
                card_content.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(semana.get('fecha','').upper(), size=14, weight="bold", color="white"),
                            ft.Text(semana.get('lectura',''), size=11, color="#E0D7FF", italic=True),
                        ], spacing=1),
                        bgcolor=week_title_bg,
                        padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    )
                )

                # Cuerpo de asignaciones de la semana
                cuerpo = ft.Column(spacing=6)
                
                # Presidente y Oración
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Presidente", semana.get('presidente',''), 'presidente', 'Anciano'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Oración", semana.get('oracion',''), 'oracion', 'Hab_Oracion'))
                cuerpo.controls.append(ft.Divider(height=1, color="#E0E0E0"))

                # Sección TESOROS
                cuerpo.controls.append(self._subcabecera_seccion("💎 TESOROS", "#546E7A"))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "1. Discurso", semana.get('num1_tesoros',''), 'num1_tesoros', 'Hab_Tes_Discurso'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "2. Perlas", semana.get('num2_tesoros',''), 'num2_tesoros', 'Hab_Tes_Perlas'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "L. Lectura Biblia", semana.get('lectura_biblia',''), 'lectura_biblia', 'Hab_Lectura'))
                cuerpo.controls.append(ft.Divider(height=1, color="#E0E0E0"))

                # Sección MAESTROS (Dinámica)
                cuerpo.controls.append(self._subcabecera_seccion("🤝 MAESTROS", "#E65100"))
                for m_idx, (tipo, valor) in enumerate(semana.get('maestros', [])):
                    cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, tipo, valor, ("maestros", m_idx), f"Hab_Mae_{tipo.split(' ')[0]}"))
                cuerpo.controls.append(ft.Divider(height=1, color="#E0E0E0"))

                # Sección VIDA CRISTIANA
                cuerpo.controls.append(self._subcabecera_seccion("🏠 VIDA CRISTIANA", "#B71C1C"))
                for v_idx, (tipo, valor) in enumerate(semana.get('partes_vida', [])):
                    cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, tipo, valor, ("partes_vida", v_idx), 'Hab_Vida_Parte1'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Estudio Bíblico", semana.get('estudio_biblico',''), 'estudio_biblico', 'Hab_Estudio_Conductor'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Lector", semana.get('lector',''), 'lector', 'Hab_Estudio_Lector'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Con. Auxiliar", semana.get('presidencia_aux',''), 'presidencia_aux', 'Anciano'))
                cuerpo.controls.append(ft.Divider(height=1, color="#E0E0E0"))

                # Sección SERVICIOS
                cuerpo.controls.append(self._subcabecera_seccion("🔧 SERVICIOS DE SALÓN", "#616161"))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Sonido", semana.get('sonido',''), 'sonido', 'Hab_Sonido'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Plataforma", semana.get('plataforma',''), 'plataforma', 'Hab_Plataforma'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Micrófonos", semana.get('microfonos',''), 'microfonos', 'Hab_Mics'))
                cuerpo.controls.append(self._fila_asignacion_interactiva(sem_idx, "Acomodadores", semana.get('acomodadores',''), 'acomodadores', 'Hab_Acomodador'))

                card_content.controls.append(
                    ft.Container(content=cuerpo, padding=12)
                )
                
                card = ft.Card(
                    content=card_content,
                    elevation=3,
                    margin=ft.Margin(0, 0, 0, 16)
                )

            self.content_area.controls.append(card)

        self.page.update()

    def _subcabecera_seccion(self, titulo, color):
        return ft.Container(
            content=ft.Text(titulo, size=11, weight="bold", color="white"),
            bgcolor=color,
            padding=ft.Padding(left=8, right=8, top=2, bottom=2),
            border_radius=4,
            margin=ft.Margin(0, 2, 0, 2)
        )

    # ==========================================
    # CREADOR DE FILA INTERACTIVA (CLICK TO EDIT)
    # ==========================================
    def _fila_asignacion_interactiva(self, semana_idx, rol, valor, campo_json, skill_col):
        # Manejar la división inteligente si hay "/" (ej: Yohander Pérez / Luis Márquez)
        if "/" in str(valor):
            parts = [p.strip() for p in str(valor).split("/")]
            rows_container = ft.Column(spacing=2)
            for sub_idx, sub_val in enumerate(parts):
                lbl = f"{rol} ({sub_idx + 1})"
                rows_container.controls.append(
                    self._construir_subfila_tactual(semana_idx, lbl, sub_val, campo_json, skill_col, sub_idx)
                )
            return rows_container
        else:
            return self._construir_subfila_tactual(semana_idx, rol, valor, campo_json, skill_col)

    def _construir_subfila_tactual(self, semana_idx, rol, valor, campo_json, skill_col, sub_idx=None):
        name_color = "#3949AB" if not self.page.theme_mode == ft.ThemeMode.DARK else "#8C9EFF"
        icon_color = ft.Colors.ON_SURFACE_VARIANT
        
        # Botones adicionales
        action_buttons = []
        
        # Icono de WhatsApp individual
        if valor and valor != "__________________" and "______" not in str(valor):
            tel = self._buscar_telefono(valor)
            if tel:
                action_buttons.append(
                    ft.IconButton(
                        icon=ft.Icons.WHATSAPP,
                        icon_color="#25D366",
                        icon_size=16,
                        padding=0,
                        tooltip=f"Notificar a {valor}",
                        on_click=lambda _: self._enviar_whatsapp_individual(valor, tel, rol, semana_idx)
                    )
                )

        # Nombre táctil para abrir selector
        interactive_name = ft.GestureDetector(
            content=ft.Text(
                str(valor), 
                size=12, 
                color=name_color, 
                weight="bold",
                decoration=ft.TextDecoration.UNDERLINE,
                decoration_style=ft.TextDecorationStyle.DASHED
            ),
            on_tap=lambda _: self.abrir_selector_candidato(semana_idx, rol, valor, campo_json, skill_col, sub_idx)
        )

        return ft.Row(
            controls=[
                ft.Text(f"{rol}:", size=12, weight="bold", color=ft.Colors.ON_SURFACE, width=105),
                ft.Row([
                    interactive_name,
                    ft.Icon(ft.Icons.EDIT, size=11, color=icon_color),
                ], spacing=4, expand=True),
                ft.Row(action_buttons, spacing=2)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _buscar_telefono(self, nombre):
        for p in self.congregacion_data:
            # Match aproximado de nombre
            if p.get('Nombre') == nombre or nombre in p.get('Nombre', ''):
                t = str(p.get('Telefono', '')).strip()
                if t and t.lower() not in ['nan', 'none', '']:
                    return "".join(filter(str.isdigit, t))
        return None

    def _enviar_whatsapp_individual(self, nombre, telefono, rol, semana_idx):
        semana = self.bimestre_data[semana_idx]
        fecha = semana.get('fecha', '')
        secc = obtener_seccion_parte_movil(rol)
        
        msg = humanizar_mensaje_movil(nombre, rol, fecha, secc)
        encoded_text = urllib.parse.quote(msg)
        
        url = f"whatsapp://send?phone={telefono}&text={encoded_text}"
        self.page.launch_url(url)
        self.show_message(f"📱 Abriendo chat con {nombre}...")

    # ==========================================
    # SELECTOR DE CANDIDATOS (BOTTOM SHEET INTELIGENTE)
    # ==========================================
    def abrir_selector_candidato(self, semana_idx, rol, valor_actual, campo_json, skill_col, sub_idx=None):
        semana = self.bimestre_data[semana_idx]
        
        # 1. Analizar elegibilidad y clasificar sugerencias inteligentes
        sugerencias = []
        todos = []
        
        # Colección de ocupados en esa misma semana
        ocupados = set()
        for k, v in semana.items():
            if k in ['fecha', 'lectura', 'no_reunion', 'motivo']:
                continue
            if k == 'maestros' or k == 'partes_vida':
                for t, name in v:
                    for name_part in [n.strip() for n in str(name).split("/")]:
                        ocupados.add(name_part)
            else:
                for name_part in [n.strip() for n in str(v).split("/")]:
                    ocupados.add(name_part)

        # Filtrar candidatos
        for p in self.congregacion_data:
            nombre = p.get('Nombre', '')
            if not nombre:
                continue
            
            es_sugerido = True
            
            # Restricciones por Privilegio / Habilidad específica
            if skill_col == 'Anciano':
                if p.get('Privilegio') != 'Anciano' or p.get('Genero') != 'M':
                    es_sugerido = False
            elif skill_col:
                # Comprobación de habilidad (Hab_*)
                if p.get(skill_col, 'No') != 'Si':
                    es_sugerido = False
            
            # Validar Género si la habilidad no lo define implícitamente
            if "hermana" in rol.lower() or "conversación (ayu.)" in rol.lower():
                if p.get('Genero') != 'F':
                    es_sugerido = False
            elif "presidente" in rol.lower() or "oración" in rol.lower() or "lector" in rol.lower() or "sonido" in rol.lower() or "mics" in rol.lower() or "plataforma" in rol.lower() or "acomodador" in rol.lower():
                if p.get('Genero') != 'M':
                    es_sugerido = False

            item_data = {
                "Nombre": nombre,
                "Privilegio": p.get('Privilegio', 'Publicador'),
                "Telefono": p.get('Telefono', ''),
                "Ocupado": nombre in ocupados,
                "Genero": p.get('Genero', 'M')
            }

            if es_sugerido:
                sugerencias.append(item_data)
            else:
                todos.append(item_data)

        # Ordenar listas
        sugerencias.sort(key=lambda x: (x['Ocupado'], x['Nombre']))
        todos.sort(key=lambda x: (x['Ocupado'], x['Nombre']))

        # Elementos de UI
        search_field = ft.TextField(
            label="Buscar publicador...",
            prefix_icon=ft.Icons.SEARCH,
            size=14,
            height=45,
            content_padding=10,
        )

        sugerencias_col = ft.Column(spacing=5)
        todos_col = ft.Column(spacing=5)

        def realizar_cambio(nombre_nuevo):
            # Lógica de reemplazo en el JSON
            if sub_idx is not None:
                # Caso de múltiples personas con "/"
                old_val = semana[campo_json]
                parts = [p.strip() for p in old_val.split("/")]
                parts[sub_idx] = nombre_nuevo
                semana[campo_json] = " / ".join(parts)
            else:
                if isinstance(campo_json, tuple):
                    # Es una sección dinámica (maestros o partes_vida)
                    campo, sub_idx_dinamico = campo_json
                    semana[campo][sub_idx_dinamico][1] = nombre_nuevo
                else:
                    # Campo estático
                    semana[campo_json] = nombre_nuevo
            
            self.page.close(self.current_bottom_sheet)
            self.mark_dirty()
            self.show_message(f"🔄 Asignado: {nombre_nuevo}")
            self._mostrar_bimestre()

        def build_tiles(filter_text=""):
            sugerencias_col.controls.clear()
            todos_col.controls.clear()
            
            f = filter_text.lower()
            
            # 1. Agregar opción especial de dejar en blanco
            if not f or "vacío" in f or "___" in f:
                btn_clear = ft.ListTile(
                    leading=ft.Icon(ft.Icons.CLEAR, color="red"),
                    title=ft.Text("Vaciar asignación", color="red", weight="bold"),
                    on_click=lambda _: realizar_cambio("__________________")
                )
                sugerencias_col.controls.append(btn_clear)

            # Sugerencias
            for item in sugerencias:
                if f and f not in item['Nombre'].lower():
                    continue
                
                badge_occup = " • [Ocupado]" if item['Ocupado'] else ""
                color_bg = "#FFE0B2" if item['Ocupado'] else "#E8F5E9" if item['Privilegio'] == 'Anciano' else "white" if not self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.SURFACE_CONTAINER_HIGHEST
                
                ic = ft.Icons.PERSON if item['Genero'] == 'M' else ft.Icons.PERSON_2
                
                sugerencias_col.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ic, color="#4A148C" if item['Genero'] == 'M' else "#E91E63"),
                            title=ft.Text(f"{item['Nombre']}{badge_occup}", weight="bold" if not item['Ocupado'] else "normal", size=13),
                            subtitle=ft.Text(f"{item['Privilegio']} {item['Telefono']}", size=11),
                            on_click=lambda _, name=item['Nombre']: realizar_cambio(name)
                        ),
                        bgcolor=color_bg,
                        border_radius=8,
                        margin=ft.Margin(0, 2, 0, 2)
                    )
                )

            # Todos
            for item in todos:
                if f and f not in item['Nombre'].lower():
                    continue
                
                badge_occup = " • [Ocupado]" if item['Ocupado'] else ""
                color_bg = "#FFE0B2" if item['Ocupado'] else "white" if not self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.SURFACE
                
                todos_col.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON_OUTLINE, color="#9E9E9E"),
                            title=ft.Text(f"{item['Nombre']}{badge_occup}", size=13),
                            subtitle=ft.Text(item['Privilegio'], size=11),
                            on_click=lambda _, name=item['Nombre']: realizar_cambio(name)
                        ),
                        bgcolor=color_bg,
                        border_radius=8,
                        margin=ft.Margin(0, 2, 0, 2)
                    )
                )
            self.page.update()

        # Input de búsqueda dinámico
        search_field.on_change = lambda e: build_tiles(e.control.value)
        build_tiles()

        selector_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Reasignar: {rol}", size=15, weight="bold"),
                    ft.IconButton(ft.Icons.CLOSE, on_click=lambda _: self.page.close(self.current_bottom_sheet))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(f"Valor actual: {valor_actual}", size=11, color="#757575"),
                search_field,
                ft.Tabs(
                    destinations=[
                        ft.Tab(
                            text="Elegibles / Sugerencias",
                            content=ft.Container(
                                content=ft.Column([sugerencias_col], scroll=ft.ScrollMode.AUTO),
                                padding=5,
                                height=280
                            )
                        ),
                        ft.Tab(
                            text="Todos los Publicadores",
                            content=ft.Container(
                                content=ft.Column([todos_col], scroll=ft.ScrollMode.AUTO),
                                padding=5,
                                height=280
                            )
                        )
                    ],
                    expand=True
                )
            ], spacing=10),
            padding=16,
            height=480,
            border_radius=ft.border_radius.only(top_left=16, top_right=16),
            bgcolor=ft.Colors.SURFACE
        )

        self.current_bottom_sheet = ft.BottomSheet(
            content=selector_container,
            is_dismissible=True
        )
        self.page.open(self.current_bottom_sheet)

    # ==========================================
    # DETALLE DE LA PESTAÑA 2: CONGREGACIÓN (PERFILES)
    # ==========================================
    def _mostrar_congregacion(self):
        self.content_area.controls.clear()

        if not self.congregacion_data:
            self.content_area.controls.append(
                ft.Container(
                    content=ft.Text("No hay datos de la congregación.", size=14, text_align=ft.TextAlign.CENTER, color="#9E9E9E"),
                    padding=40,
                )
            )
            self.page.update()
            return

        datos_ordenados = sorted(self.congregacion_data, key=lambda x: (
            {"Anciano": 0, "Siervo Min.": 1}.get(x.get("Privilegio", ""), 2),
            x.get("Privilegio", ""),
            x.get("Nombre", "")
        ))

        search_bar = ft.TextField(
            label="Buscar hermano(a)...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: filter_roster(e.control.value),
            height=45,
            content_padding=10
        )
        self.content_area.controls.append(search_bar)

        roster_list_container = ft.Column(spacing=2)
        self.content_area.controls.append(roster_list_container)

        def show_publisher_profile(p):
            # Construir la lista de habilidades configuradas
            habilidades_si = []
            for k, v in p.items():
                if k.startswith("Hab_") and v == "Si":
                    nombre_corto = k.replace("Hab_", "").replace("_", " ")
                    habilidades_si.append(nombre_corto)

            habs_chips = []
            if habilidades_si:
                for h in habilidades_si:
                    habs_chips.append(
                        ft.Container(
                            content=ft.Text(h, size=10, color="white", weight="bold"),
                            bgcolor="#673AB7",
                            padding=ft.Padding(6, 3, 6, 3),
                            border_radius=4
                        )
                    )
            else:
                habs_chips.append(ft.Text("Sin habilidades asignadas en la matriz", size=11, italic=True))

            dialog_profile = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.Icons.PERSON if p.get('Genero') == 'M' else ft.Icons.PERSON_2, color="#4A148C"),
                    ft.Text(p.get('Nombre','')),
                ], spacing=10),
                content=ft.Column([
                    ft.Row([ft.Text("Privilegio:", weight="bold", size=12), ft.Text(p.get('Privilegio',''))]),
                    ft.Row([ft.Text("Teléfono:", weight="bold", size=12), ft.Text(p.get('Telefono',''))]),
                    ft.Row([ft.Text("Es Menor:", weight="bold", size=12), ft.Text(p.get('Es_Menor','No'))]),
                    ft.Divider(height=10),
                    ft.Text("Habilidades Autorizadas:", weight="bold", size=12),
                    ft.Row(habs_chips, wrap=True, spacing=4)
                ], spacing=6, height=220, width=320),
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda _: self.page.close(dialog_profile))
                ]
            )
            self.page.open(dialog_profile)

        def filter_roster(query=""):
            roster_list_container.controls.clear()
            q = query.lower()
            prev_priv = None
            
            for row in datos_ordenados:
                nombre = str(row.get('Nombre', ''))
                priv = str(row.get('Privilegio', 'Publicador'))
                
                if q and q not in nombre.lower():
                    continue

                if priv != prev_priv and not q:
                    color_bg = "#EDE7F6" if not self.page.theme_mode == ft.ThemeMode.DARK else "#311B92"
                    text_color = "#4A148C" if not self.page.theme_mode == ft.ThemeMode.DARK else "#E0D7FF"
                    roster_list_container.controls.append(
                        ft.Container(
                            content=ft.Text(priv.upper(), size=11, weight="bold", color=text_color),
                            bgcolor=color_bg,
                            padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                            border_radius=4,
                            margin=ft.Margin(0, 6, 0, 2)
                        )
                    )
                    prev_priv = priv

                color_icon = {"Anciano": "#4A148C", "Siervo Min.": "#2E7D32"}.get(priv, "#757575")
                icon = ft.Icons.PERSON if row.get('Genero', 'M') == 'M' else ft.Icons.PERSON_2

                roster_list_container.controls.append(
                    ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(icon, color=color_icon, size=22),
                            title=ft.Text(nombre, size=13, weight="bold"),
                            subtitle=ft.Text(str(row.get('Telefono', '')), size=11, color="#757575"),
                            on_click=lambda _, r=row: show_publisher_profile(r)
                        ),
                        bgcolor=ft.Colors.SURFACE,
                        border_radius=8,
                        margin=ft.Margin(0, 1, 0, 1)
                    )
                )
            self.page.update()

        filter_roster()

    # ==========================================
    # DETALLE DE LA PESTAÑA 3: WHATSAPP CONSOLIDADO
    # ==========================================
    def _mostrar_notificaciones(self):
        self.content_area.controls.clear()

        if not self.bimestre_data:
            self.content_area.controls.append(
                ft.Container(
                    content=ft.Text("Genera un bimestre primero para poder notificar.", size=14, text_align=ft.TextAlign.CENTER, color="#9E9E9E"),
                    padding=40,
                )
            )
            self.page.update()
            return

        # 1. Agrupar asignaciones del bimestre por persona
        agenda_personal = {}
        
        for sem in self.bimestre_data:
            fecha = sem.get('fecha', '')
            lectura = sem.get('lectura', '')
            
            def add_to_agenda(nombre, rol):
                if not nombre or nombre == "__________________" or "______" in str(nombre):
                    return
                # Si hay varios separados por "/"
                if "/" in str(nombre):
                    for idx, part in enumerate([p.strip() for p in str(nombre).split("/")]):
                        add_to_agenda(part, f"{rol} (Duo {idx+1})")
                    return
                
                if nombre not in agenda_personal:
                    agenda_personal[nombre] = []
                agenda_personal[nombre].append({
                    "fecha": fecha,
                    "lectura": lectura,
                    "rol": rol
                })

            add_to_agenda(sem.get('presidente'), "Presidente")
            add_to_agenda(sem.get('oracion'), "Oración")
            add_to_agenda(sem.get('num1_tesoros'), "Discurso (Tesoros)")
            add_to_agenda(sem.get('num2_tesoros'), "Perlas (Tesoros)")
            add_to_agenda(sem.get('lectura_biblia'), "Lectura Biblia")
            
            for tipo, val in sem.get('maestros', []):
                add_to_agenda(val, tipo)
                
            for tipo, val in sem.get('partes_vida', []):
                add_to_agenda(val, tipo)
                
            add_to_agenda(sem.get('estudio_biblico'), "Conductor Estudio")
            add_to_agenda(sem.get('lector'), "Lector Estudio")
            add_to_agenda(sem.get('sonido'), "Sonido")
            add_to_agenda(sem.get('plataforma'), "Plataforma")
            add_to_agenda(sem.get('microfonos'), "Micrófonos")
            add_to_agenda(sem.get('acomodadores'), "Acomodadores")

        # 2. Renderizar la lista de notificaciones pendientes
        if not agenda_personal:
            self.content_area.controls.append(
                ft.Container(
                    content=ft.Text("No hay asignaciones válidas cargadas.", size=14, text_align=ft.TextAlign.CENTER, color="#9E9E9E"),
                    padding=40,
                )
            )
            self.page.update()
            return

        self.content_area.controls.append(
            ft.Text(f"Total personas asignadas: {len(agenda_personal)}", size=13, weight="bold", color="#757575")
        )

        for nombre_hermano, partes in sorted(agenda_personal.items()):
            telefono = self._buscar_telefono(nombre_hermano)
            
            # Generar listado con viñetas del cronograma
            lista_partes_str = ""
            list_widgets = []
            
            for p in partes:
                lista_partes_str += f"• *{p['rol']}* — 📅 *{p['fecha']}* (Lectura: _{p['lectura']}_)\n"
                list_widgets.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color="#4CAF50", size=14),
                            ft.Column([
                                ft.Text(p['rol'], size=12, weight="bold"),
                                ft.Text(f"📅 {p['fecha']} ({p['lectura']})", size=11, color="#757575")
                            ], spacing=1, expand=True)
                        ], spacing=8),
                        margin=ft.Margin(0, 2, 0, 2)
                    )
                )

            # Botón de envío
            action_buttons = []
            if telefono:
                def click_envio(e, name=nombre_hermano, tel=telefono, parts_str=lista_partes_str):
                    saludos = [
                        f"Hola {name}, 🙂",
                        f"Hola, hermano {name}. Espero que te encuentres muy bien. 🌟",
                        f"Saludos cariñosos, {name}. 🤗",
                        f"¡Hola, {name}! Qué gusto saludarte. 😊"
                    ]
                    intro = "Te compartimos los detalles de tus asignaciones teocráticas en la reunión VMC para este bimestre:"
                    despedida = "Agradecemos de todo corazón tu valiosa y excelente disposición para servir a favor de la congregación. ¡Que Jehová bendiga tu preparación! 🙏📖"
                    
                    msg = f"{random.choice(saludos)}\n\n{intro}\n\n{parts_str}\n{despedida}"
                    encoded = urllib.parse.quote(msg)
                    
                    self.page.launch_url(f"whatsapp://send?phone={tel}&text={encoded}")
                    self.show_message(f"📱 Abriendo chat consolidado de {name}...")

                def click_web(e, name=nombre_hermano, tel=telefono, parts_str=lista_partes_str):
                    saludos = [
                        f"Hola {name}, 🙂",
                        f"Hola, hermano {name}. Espero que te encuentres muy bien. 🌟",
                        f"Saludos cariñosos, {name}. 🤗"
                    ]
                    intro = "Te compartimos los detalles de tus asignaciones teocráticas en la reunión VMC para este bimestre:"
                    despedida = "Agradecemos de todo corazón tu valiosa disposición. ¡Que Jehová bendiga tu preparación! 🙏"
                    
                    msg = f"{random.choice(saludos)}\n\n{intro}\n\n{parts_str}\n{despedida}"
                    encoded = urllib.parse.quote(msg)
                    
                    self.page.launch_url(f"https://web.whatsapp.com/send?phone={tel}&text={encoded}")

                action_buttons.append(
                    ft.ElevatedButton(
                        text="📱 WhatsApp App",
                        icon=ft.Icons.WHATSAPP,
                        bgcolor="#25D366",
                        color="white",
                        on_click=click_envio,
                        height=35
                    )
                )
                action_buttons.append(
                    ft.TextButton(
                        text="💻 Web",
                        icon=ft.Icons.WEB,
                        on_click=click_web,
                        height=35
                    )
                )
            else:
                action_buttons.append(
                    ft.Text("⚠️ Sin teléfono", color="red", size=12, weight="bold")
                )

            card_persona = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="#4A148C"),
                            ft.Text(nombre_hermano, size=14, weight="bold", expand=True),
                            ft.Container(
                                content=ft.Text(f"{len(partes)} partes", size=10, color="white", weight="bold"),
                                bgcolor="#546E7A",
                                padding=ft.Padding(5, 2, 5, 2),
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=4),
                        ft.Column(list_widgets, spacing=2),
                        ft.Divider(height=4),
                        ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END, spacing=4)
                    ], spacing=8),
                    padding=14
                ),
                elevation=2,
                margin=ft.Margin(0, 0, 0, 10)
            )
            self.content_area.controls.append(card_persona)

        self.page.update()


def main(page: ft.Page):
    try:
        VMCAndroidApp(page)
    except Exception as e:
        import traceback
        page.scroll = ft.ScrollMode.AUTO
        page.add(
            ft.Text("❌ CRITICAL ERROR ON STARTUP:", color="red", weight="bold", size=18),
            ft.Text(str(e), color="red"),
            ft.Text(traceback.format_exc(), size=10)
        )
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
