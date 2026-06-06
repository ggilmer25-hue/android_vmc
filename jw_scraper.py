"""
jw_scraper.py - Módulo para obtener datos de la Guía de Actividades
para la reunión Vida y Ministerio Cristianos desde wol.jw.org
"""

import requests
import re
import json
import os
from datetime import datetime, timedelta, date


class JWScraper:
    """Scraper para obtener datos de la Guía de Actividades VMC desde wol.jw.org"""

    BASE_URL = "https://wol.jw.org"
    MEETINGS_PATH = "/es/wol/meetings/r4/lp-s"
    ARTICLE_PATH = "/es/wol/d/r4/lp-s"

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    CACHE_FILE = "jw_cache.json"

    def __init__(self, cache_path=None):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
        # Determinar ruta de cache
        if cache_path:
            self.cache_file = cache_path
        else:
            import sys
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            self.cache_file = os.path.join(base_dir, self.CACHE_FILE)
            
        self.cache = self._cargar_cache()

    # ── Cache ──────────────────────────────────────────────

    def _cargar_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _guardar_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar cache: {e}")

    # ── Obtener datos ─────────────────────────────────────

    def obtener_doc_id(self, year, week_number):
        """Obtiene el docId del artículo de la guía para una semana ISO."""
        url = f"{self.BASE_URL}{self.MEETINGS_PATH}/{year}/{week_number}"
        response = self.session.get(url, timeout=15)
        response.raise_for_status()

        # Buscar links al artículo de la guía (docIds largos, 9+ dígitos)
        pattern = r'/es/wol/d/r4/lp-s/(\d{9,})'
        matches = re.findall(pattern, response.text)
        if matches:
            return matches[0]

        # Fallback: cualquier docId
        pattern2 = r'/es/wol/d/r4/lp-s/(\d+)'
        matches2 = re.findall(pattern2, response.text)
        # Filtrar los que parecen ser de la guía (empiezan con 20)
        for m in matches2:
            if len(m) >= 9:
                return m
        return None

    def obtener_semana(self, year, week_number, usar_cache=True):
        """Obtiene datos completos de una semana."""
        cache_key = f"{year}_{week_number}"

        if usar_cache and cache_key in self.cache:
            return self.cache[cache_key]

        doc_id = self.obtener_doc_id(year, week_number)
        if not doc_id:
            raise Exception(f"No se encontró la guía para semana {week_number} de {year}")

        url = f"{self.BASE_URL}{self.ARTICLE_PATH}/{doc_id}"
        response = self.session.get(url, timeout=15)
        response.raise_for_status()

        datos = self._parsear_html(response.text, doc_id)

        self.cache[cache_key] = datos
        self._guardar_cache()

        return datos

    def obtener_rango_semanas(self, year, week_start, week_end, callback=None):
        """Obtiene datos de varias semanas consecutivas."""
        resultados = []
        total = week_end - week_start + 1

        for i, week in enumerate(range(week_start, week_end + 1)):
            try:
                datos = self.obtener_semana(year, week)
                resultados.append(datos)
                if callback:
                    callback(i + 1, total, datos.get('fecha', f'Semana {week}'))
            except Exception as e:
                resultados.append({
                    'error': str(e),
                    'week_number': week,
                    'fecha': f'Semana {week} (error)',
                    'lectura_biblica': '',
                    'maestros': [],
                })
                if callback:
                    callback(i + 1, total, f'Error semana {week}')

        return resultados

    # ── Parsing ───────────────────────────────────────────

    def _html_to_text(self, html):
        """Convierte HTML a texto plano."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            for el in soup(['script', 'style', 'nav', 'footer']):
                el.decompose()
            article = (soup.find('article')
                       or soup.find('div', id='article')
                       or soup.find('div', class_='article')
                       or soup)
            return article.get_text(separator='\n', strip=True)
        except ImportError:
            # Fallback sin BeautifulSoup
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', '\n', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            for entity, char in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                                  ('&quot;', '"'), ('&#39;', "'"), ('&nbsp;', ' '),
                                  ('&aacute;', 'á'), ('&eacute;', 'é'), ('&iacute;', 'í'),
                                  ('&oacute;', 'ó'), ('&uacute;', 'ú'), ('&ntilde;', 'ñ')]:
                text = text.replace(entity, char)
            return text

    def _parsear_html(self, html, doc_id):
        """Parsea el HTML del artículo y extrae todos los datos."""
        text = self._html_to_text(html)
        datos = {
            'doc_id': doc_id,
            'fecha': '',
            'lectura_biblica': '',
            'cancion_inicial': '',
            'cancion_intermedia': '',
            'cancion_final': '',
            'tesoros': [],
            'maestros': [],
            'vida_cristiana': [],
        }

        # ── Fecha ──
        meses = r'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre'
        fecha_pat = re.compile(
            rf'(\d{{1,2}}(?:\s*[-–]\s*\d{{1,2}})?\s+de\s+(?:{meses})'
            rf'(?:\s+a\s+\d{{1,2}}\s+de\s+(?:{meses}))?)',
            re.IGNORECASE
        )
        m = fecha_pat.search(text)
        if m:
            datos['fecha'] = m.group(1).strip()

        # ── Lectura bíblica ──
        # El texto comienza con: "4-10 DE MAYO\nISAÍAS 58,\n59\nCanción 21"
        # Extraer las líneas entre la fecha y la primera "Canción"
        lines = text.split('\n')
        lectura_lines = []
        found_date = False
        for line in lines[:15]:  # Solo buscar en las primeras 15 líneas
            stripped = line.strip()
            if not stripped:
                continue
            if not found_date:
                # Detectar la línea de fecha
                if re.search(rf'(?:{meses})', stripped, re.IGNORECASE):
                    found_date = True
                continue
            # Parar al encontrar la canción
            if re.search(r'[Cc]anci[oó]n', stripped):
                break
            lectura_lines.append(stripped)
        if lectura_lines:
            datos['lectura_biblica'] = ' '.join(lectura_lines)

        # ── Canciones ──
        canciones = re.findall(r'[Cc]anci[oó]n\s+(\d+)', text)
        if len(canciones) >= 1:
            datos['cancion_inicial'] = canciones[0]
        if len(canciones) >= 2:
            datos['cancion_intermedia'] = canciones[1]
        if len(canciones) >= 3:
            datos['cancion_final'] = canciones[-1]

        # ── Asignaciones numeradas ──
        asig_pat = re.compile(r'(\d+)\.\s+(.+?)\s*\((\d+)\s*mins?\.\)')
        for match in asig_pat.finditer(text):
            num = int(match.group(1))
            titulo = match.group(2).strip()
            # Limpiar título de caracteres extraños
            titulo = re.sub(r'\s+', ' ', titulo)
            mins = int(match.group(3))
            tipo = self._clasificar_asignacion(titulo)

            asignacion = {
                'numero': num,
                'titulo': titulo,
                'mins': mins,
                'tipo': tipo,
            }

            if num <= 3:
                datos['tesoros'].append(asignacion)
            elif num <= 7 and tipo in ['Empiece conversaciones', 'Haga revisitas', 'Haga discípulos', 'Explique sus creencias', 'Discurso']:
                datos['maestros'].append(asignacion)
            elif num <= 6: # Fallback para casos raros
                datos['maestros'].append(asignacion)
            else:
                datos['vida_cristiana'].append(asignacion)

        # ── Lectura de la Biblia (cita específica) ──
        lectura_cita = re.search(
            r'Lectura de la Biblia.*?\)\s*'
            r'([A-Za-záéíóúñÁÉÍÓÚÑ]+\.?\s+\d[\d:,\-–\s]*\d)',
            text
        )
        if lectura_cita:
            datos['lectura_cita'] = lectura_cita.group(1).strip()

        return datos

    def _clasificar_asignacion(self, titulo):
        """Clasifica el tipo de asignación basado en el título."""
        t = titulo.lower()
        if 'empiece conversacion' in t:
            return 'Empiece conversaciones'
        elif 'revisita' in t:
            return 'Haga revisitas'
        elif 'disc' in t and ('haga' in t or 'pulo' in t):
            return 'Haga discípulos'
        elif 'explique' in t and 'creencia' in t:
            return 'Explique sus creencias'
        elif t.startswith('discurso') or t == 'discurso':
            return 'Discurso'
        elif 'lectura de la biblia' in t:
            return 'Lectura de la Biblia'
        elif 'perlas escondidas' in t:
            return 'Busquemos perlas escondidas'
        elif 'estudio b' in t:
            return 'Estudio bíblico'
        elif 'necesidades' in t:
            return 'Necesidades de la congregación'
        return titulo

    # ── Utilidades de fechas ──────────────────────────────

    @staticmethod
    def calcular_semanas_bimestre(year, month_start):
        """Calcula los números de semana ISO para un bimestre (2 meses)."""
        start = date(year, month_start, 1)
        start_monday = start - timedelta(days=start.weekday())

        end_month = month_start + 1 if month_start < 12 else 1
        end_year = year if month_start < 12 else year + 1
        if end_month == 12:
            end_date = date(end_year, 12, 31)
        else:
            end_date = date(end_year, end_month + 1, 1) - timedelta(days=1)
        end_monday = end_date - timedelta(days=end_date.weekday())

        weeks = []
        current = start_monday
        while current <= end_monday:
            iso_year, iso_week, _ = current.isocalendar()
            weeks.append((iso_year, iso_week))
            current += timedelta(weeks=1)
        return weeks

    @staticmethod
    def get_bimestres():
        """Retorna lista de bimestres del año."""
        return [
            ("Enero-Febrero", 1),
            ("Marzo-Abril", 3),
            ("Mayo-Junio", 5),
            ("Julio-Agosto", 7),
            ("Septiembre-Octubre", 9),
            ("Noviembre-Diciembre", 11),
        ]

    @staticmethod
    def detectar_bimestre_actual():
        """Detecta el bimestre actual basado en la fecha."""
        mes = datetime.now().month
        for nombre, mes_inicio in JWScraper.get_bimestres():
            if mes in (mes_inicio, mes_inicio + 1 if mes_inicio < 12 else 1):
                return nombre, mes_inicio
        return "Mayo-Junio", 5


# ── Test rápido ───────────────────────────────────────────
if __name__ == "__main__":
    scraper = JWScraper()
    print("Probando scraper con semana actual...")
    try:
        datos = scraper.obtener_semana(2026, 19, usar_cache=False)
        print(f"\nFecha: {datos['fecha']}")
        print(f"Lectura: {datos['lectura_biblica']}")
        print(f"Canciones: {datos['cancion_inicial']}, {datos['cancion_intermedia']}, {datos['cancion_final']}")
        print(f"\nTesoros ({len(datos['tesoros'])}):")
        for a in datos['tesoros']:
            print(f"  {a['numero']}. [{a['tipo']}] {a['titulo']} ({a['mins']} min)")
        print(f"\nMaestros ({len(datos['maestros'])}):")
        for a in datos['maestros']:
            print(f"  {a['numero']}. [{a['tipo']}] {a['titulo']} ({a['mins']} min)")
        print(f"\nVida Cristiana ({len(datos['vida_cristiana'])}):")
        for a in datos['vida_cristiana']:
            print(f"  {a['numero']}. [{a['tipo']}] {a['titulo']} ({a['mins']} min)")
    except Exception as e:
        print(f"Error: {e}")
