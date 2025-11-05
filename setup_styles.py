import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self):
        self.colors = {
            "primary": "#2C3E50",
            "secondary": "#3498DB",
            "accent": "#E74C3C",
            "success": "#27AE60",
            "warning": "#F39C12",
            "info": "#2980B9",
            "white": "#FFFFFF"
        }

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        c = self.colors

        # Frames / fondo
        style.configure("TFrame", background=c["white"])

        # Botones
        style.configure("Primary.TButton",
                        background=c["secondary"],
                        foreground="white",
                        padding=(10, 5))
        style.map("Primary.TButton",
                  foreground=[('active', 'white')],
                  background=[('active', c["info"])])

        style.configure("Success.TButton",
                        background=c["success"],
                        foreground="white")
        style.configure("Warning.TButton",
                        background=c["warning"],
                        foreground="white")
        style.configure("Danger.TButton",
                        background=c["accent"],
                        foreground="white")

        # Labels
        style.configure("Header.TLabel",
                        font=('Arial', 16, 'bold'),
                        foreground=c["primary"],
                        background=c["white"])
        style.configure("Secondary.TLabel",
                        foreground=c["primary"],
                        background=c["white"])

# Instancia global para usar desde main
style_manager = StyleManager()
