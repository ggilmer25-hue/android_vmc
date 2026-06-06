---
tags:
  - proyecto/vmc
  - registro/cambios
  - estado/activo
fecha_creacion: 2026-05-15
ultima_modificacion: 2026-05-15
---

# 📓 Bitácora de Desarrollo: Coordinación VMC

> [!NOTE] Propósito
> Este archivo centraliza el historial de cambios y la planificación del sistema de gestión de reuniones teocráticas para la congregación El Araguaney.

---

## 📅 [2026-05-15] - Actualización: Granularidad de Habilidades

### 🚀 Nuevas Funcionalidades
- **Estructura Detallada de Asignaciones**: Se ha pasado de un sistema de habilidades genéricas a uno específico por tipo de parte.
    - **Tesoros**: Discurso, Perlas, Lectura.
    - **Maestros**: Soporte para *Encargado* y *Ayudante* en Conversaciones, Revisitas, Discípulos y Escenificación.
    - **Vida Cristiana**: Desglosado en Parte 1, Parte 2 y Necesidades Locales.
- **Sugerencias Inteligentes**: El modal de "Añadir Publicador" ahora autocompleta los checks basándose en el privilegio, género y edad del hermano.

### 🛠️ Detalles Técnicos
> [!TIP] Optimización de Datos
> Se añadió lógica en `cargar_datos` para migrar automáticamente permisos de versiones anteriores al nuevo formato granular, evitando la pérdida de información previa.

- **UI Avanzada**: Rediseño de paneles en `customtkinter` con categorías visuales y scroll dinámico.
- **Lógica de Pool**: Actualización de `inicializar_listas_habilidades` para integración con la nueva base de datos.

### 📄 Archivos Afectados
- [[coordinacion_vmc.py]] (Clase Principal)
- [[Congregacion_Araguaney.xlsx]] (Estructura de Columnas)

---

## 📋 Próximos Pasos
- [x] **Asignación Lógica**: Implementar distinción real entre Encargado/Ayudante en el algoritmo.
- [x] **Exportación**: Adaptar plantillas de Excel y PDF a las nuevas categorías.
- [x] **WhatsApp**: Personalizar plantillas según el tipo específico de parte.

---

## 📅 [2026-05-21] - Actualización: Consolidación de WhatsApp, Firma y UI en Modo Oscuro

### 🚀 Nuevas Funcionalidades
- **Consolidación de WhatsApp**: En lugar de enviar un mensaje separado por cada asignación de un mismo hermano en el bimestre, ahora se agrupan de forma inteligente en un solo mensaje estructurado.
- **Firma Profesional del Desarrollador**: Se agregó el crédito "Desarrollado por Gilmer Gonzalez" integrado de manera elegante y discreta en la cabecera principal de la pestaña de Programación.
- **Interfaz Premium en Modo Oscuro (Dark Mode)**: Rediseño completo de la interfaz gráfica a modo oscuro nativo, cuidando el contraste de textos y botones.
- **Fix de Regeneración de Historial**: Se resolvió el bug donde los intentos de generación de bimestre no guardados se apilaban en memoria, afectando erróneamente las reglas de cooldown.

### 🛠️ Detalles Técnicos
- **Agrupamiento en `enviar_todos_whatsapp`**: Modificación de la función para recolectar las partes bimestrales en un diccionario indexado por nombre, concatenando las partes en un string con viñetas antes de llamar a la humanización.
- **Limpieza de Colores Hardcoded**: Eliminación de colores de fondo estáticos (`white`, `#EEE`, `#F5F5F5`) para permitir que CustomTkinter aplique su paleta oscura de forma limpia en toda la jerarquía de layouts.
- **Recarga de Historial en Generación**: Inclusión de `cargar_historial()` en el arranque de la función `generar_bimestre_completo()`.

### 📄 Archivos Afectados
- [[coordinacion_vmc.py]] (Lógica de agrupación de WhatsApp, reseteo de historial y UI)
- [[Guia_Usuario_VMC.md]] (Actualizada con los nuevos detalles de generación y UI)
- [[Bitacora_Desarrollo.md]] (Registro de cambios)
