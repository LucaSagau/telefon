import flet as ft
import json
import os
import math
from simpleeval import simple_eval

def main(page: ft.Page):
    # Setări de bază pentru a asigura randarea
    page.title = "Mobipro Diagnostic"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    def afiseaza_eroare(mesaj):
        page.add(ft.Text(f"LOG: {mesaj}", color="red", weight="bold"))
        page.update()

    try:
        # LISTA MANUALĂ - Singura cale sigură pe Android
        categorii = ["Corpuri_baie", "Corpuri_custom", "Corpuri_dormitor", "Corpuri_hol", 
                     "Corpuri_inferioare", "CORPURI_INFERIOARE_GOLA", "Corpuri_living", 
                     "Corpuri_superioare", "Turnuri"]

        # Componente UI
        combo_cat = ft.Dropdown(
            label="1. Alege Categoria",
            options=[ft.dropdown.Option(c) for c in categorii],
            width=300
        )
        
        lista_piese = ft.Column()

        # Interfața de bază care TREBUIE să apară
        page.add(
            ft.Text("Mobipro v7.3 - Versiune Stabilă", size=22, weight="bold"),
            combo_cat,
            ft.ElevatedButton("TESTARE ACCES FIȘIERE", 
                on_click=lambda _: afiseaza_eroare("Buton apăsat!"),
                bgcolor="blue", color="white"
            ),
            ft.Divider(),
            lista_piese
        )
        
    except Exception as e:
        afiseaza_eroare(f"Eroare fatală la start: {str(e)}")

ft.app(target=main, assets_dir="assets")