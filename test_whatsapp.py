"""
🧪 Test de Integración WhatsApp - Coordinación VMC
Prueba rápida para verificar que el envío de mensajes funciona correctamente.
"""
import urllib.parse
import webbrowser
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("Light")

def test_whatsapp():
    root = ctk.CTk()
    root.title("🧪 Test WhatsApp - VMC")
    root.geometry("550x500")
    root.resizable(False, False)

    # Header
    header = ctk.CTkFrame(root, fg_color="#25D366", height=60, corner_radius=0)
    header.pack(fill="x")
    header.pack_propagate(False)
    ctk.CTkLabel(header, text="🧪 PRUEBA DE WHATSAPP", font=("Segoe UI", 20, "bold"), text_color="white").pack(expand=True)

    # Contenido
    content = ctk.CTkFrame(root, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=25, pady=15)

    # Teléfono
    ctk.CTkLabel(content, text="📱 Número de teléfono (con código de país):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5,2))
    e_tel = ctk.CTkEntry(content, width=400, height=35, placeholder_text="Ej: +584121234567")
    e_tel.pack(anchor="w", pady=(0,10))

    # Nombre
    ctk.CTkLabel(content, text="👤 Nombre del hermano (para la plantilla):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5,2))
    e_nombre = ctk.CTkEntry(content, width=400, height=35)
    e_nombre.insert(0, "Hermano de Prueba")
    e_nombre.pack(anchor="w", pady=(0,10))

    # Método
    ctk.CTkLabel(content, text="🔀 Método de envío:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5,2))
    metodo = ctk.CTkComboBox(content, values=["WhatsApp Desktop (App)", "WhatsApp Web (Navegador)"], width=300)
    metodo.set("WhatsApp Desktop (App)")
    metodo.pack(anchor="w", pady=(0,10))

    # Status
    status_frame = ctk.CTkFrame(content, fg_color="#F0F0F0", corner_radius=8)
    status_frame.pack(fill="x", pady=10)
    status_label = ctk.CTkLabel(status_frame, text="⏳ Esperando prueba...", font=("Arial", 11), text_color="gray")
    status_label.pack(pady=10)

    def enviar_prueba():
        telefono = e_tel.get().strip()
        nombre = e_nombre.get().strip()

        if not telefono:
            messagebox.showwarning("Falta teléfono", "Ingresa un número de teléfono para la prueba.")
            return

        # Limpiar teléfono
        tel_clean = "".join(filter(str.isdigit, telefono))
        if not tel_clean.startswith("58"):
            tel_clean = "58" + tel_clean

        # Mensaje de prueba usando la plantilla real del programa
        mensaje = (
            f"Hola {nombre}, 🙂\n\n"
            f"Te informamos que tienes la siguiente asignación:\n\n"
            f"📋 *Empiece conversaciones (5 min.)*\n"
            f"📅 *19 de mayo de 2026*\n"
            f"📖 Sección: Seamos Mejores Maestros\n\n"
            f"¡Muchas gracias por tu servicio! 🙏\n\n"
            f"--- 🧪 ESTO ES UNA PRUEBA ---"
        )

        texto_encoded = urllib.parse.quote(mensaje)

        if "Desktop" in metodo.get():
            url = f"whatsapp://send?phone={tel_clean}&text={texto_encoded}"
            metodo_txt = "WhatsApp Desktop"
        else:
            url = f"https://web.whatsapp.com/send?phone={tel_clean}&text={texto_encoded}"
            metodo_txt = "WhatsApp Web"

        # Copiar al portapapeles
        root.clipboard_clear()
        root.clipboard_append(mensaje)
        root.update()

        status_label.configure(
            text=f"✅ Abriendo {metodo_txt} para +{tel_clean}...\n📋 Mensaje copiado al portapapeles",
            text_color="#25D366"
        )

        # Abrir WhatsApp
        webbrowser.open(url)

        print(f"\n{'='*50}")
        print(f"📱 URL generada: {url[:80]}...")
        print(f"📞 Teléfono: +{tel_clean}")
        print(f"👤 Nombre: {nombre}")
        print(f"🔀 Método: {metodo_txt}")
        print(f"{'='*50}\n")

    def solo_copiar():
        nombre = e_nombre.get().strip()
        mensaje = (
            f"Hola {nombre}, 🙂\n\n"
            f"Te informamos que tienes la siguiente asignación:\n\n"
            f"📋 *Empiece conversaciones (5 min.)*\n"
            f"📅 *19 de mayo de 2026*\n"
            f"📖 Sección: Seamos Mejores Maestros\n\n"
            f"¡Muchas gracias por tu servicio! 🙏"
        )
        root.clipboard_clear()
        root.clipboard_append(mensaje)
        root.update()
        status_label.configure(text="📋 Mensaje copiado al portapapeles.\nPégalo manualmente en cualquier chat.", text_color="#1565C0")

    # Botones
    btn_frame = ctk.CTkFrame(content, fg_color="transparent")
    btn_frame.pack(fill="x", pady=10)

    ctk.CTkButton(btn_frame, text="📱 ENVIAR PRUEBA", command=enviar_prueba,
                  fg_color="#25D366", hover_color="#128C7E", font=("Arial", 14, "bold"),
                  height=45, width=220).pack(side="left", padx=5)

    ctk.CTkButton(btn_frame, text="📋 SOLO COPIAR", command=solo_copiar,
                  fg_color="#1565C0", hover_color="#0D47A1", font=("Arial", 14, "bold"),
                  height=45, width=220).pack(side="left", padx=5)

    root.mainloop()

if __name__ == "__main__":
    test_whatsapp()
