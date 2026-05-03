import flet as ft
import json
import math
import os
import sys
from simpleeval import simple_eval

def main(page: ft.Page):
    page.title = "Mobipro v7.3 Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"
    page.padding = 20

    # --- CONFIGURARE CĂI ---
    # Pe Android, folderul assets este accesat relativ la rădăcina APK-ului
    cale_baza = "assets/database"

    # --- LISTĂ MANUALĂ CATEGORII (Previne ecranul alb) ---
    # Numele trebuie să fie IDENTICE cu folderele tale de pe GitHub
    categorii_manuale = [
        "Corpuri_baie", 
        "Corpuri_custom", 
        "Corpuri_dormitor", 
        "Corpuri_hol", 
        "Corpuri_inferioare", 
        "CORPURI_INFERIOARE_GOLA", 
        "Corpuri_living", 
        "Corpuri_superioare", 
        "Turnuri"
    ]

    # --- FUNCTII ---
    def incarca_modele(e):
        if not combo_cat.value:
            return
        
        # Construim calea către categoria selectată
        cale_cat = os.path.join(cale_baza, combo_cat.value)
        
        try:
            if os.path.exists(cale_cat):
                fisiere = [f for f in os.listdir(cale_cat) if f.endswith('.json')]
                combo_mod.options = [ft.dropdown.Option(f) for f in sorted(fisiere)]
                if fisiere:
                    combo_mod.value = fisiere[0]
                else:
                    combo_mod.options = [ft.dropdown.Option("Niciun JSON găsit")]
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Folder negăsit: {cale_cat}"))
                page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Eroare la citire modele: {ex}"))
            page.snack_bar.open = True
            page.update()

    def adauga_corp(e):
        try:
            # Preluare valori și conversie
            v_L = float(inp_L.value) if inp_L.value else 0
            v_H = float(inp_H.value) if inp_H.value else 0
            v_A = float(inp_A.value) if inp_A.value else 0
            v_HA = float(inp_HA.value) if inp_HA.value else 0
            v_S = float(combo_sina.value)

            # Context pentru calculele din JSON
            ctx_n = {"L": v_L, "H": v_H, "A": v_A, "HA": v_HA, "S": v_S, "le": 1.5, "li": 2.0, "G": 18}
            ctx_f = {"floor": math.floor, "ceil": math.ceil, "round": round}

            cale_json = os.path.join(cale_baza, combo_cat.value, combo_mod.value)
            
            with open(cale_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Luăm prima cheie din JSON (numele obiectului)
                nume_obiect = list(data.keys())[0]
                structura = data[nume_obiect]

            # Procesare piese
            for p in structura.get("piese", []):
                vL_raw = simple_eval(str(p["L"]), names=ctx_n, functions=ctx_f)
                vl_raw = simple_eval(str(p["l"]), names=ctx_n, functions=ctx_f)
                vL, vl = math.floor(vL_raw), math.floor(vl_raw)
                
                # Ajustare cant dacă nu e MDF
                if "front" in p["material"].lower() and radio_cant.value != "MDF":
                    v_c = 1 if radio_cant.value == "1mm" else 2
                    vL -= (v_c * 2)
                    vl -= (v_c * 2)

                # Adăugare în listă (cele noi apar sus)
                lista_vizuala.controls.insert(0,
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(f"{p['nume']} ({nume_obiect})", weight="bold"),
                                ft.Row([
                                    ft.Text(f"{vL} x {vl}", size=20, color="blue900", weight="bold"),
                                    ft.Text(f"{p['cantitate']} buc", weight="w500"),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ])
                        )
                    )
                )
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Eroare calcul: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- COMPONENTE UI ---
    inp_L = ft.TextField(label="Lățime (L)", value="600", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_H = ft.TextField(label="Înălțime (H)", value="760", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_A = ft.TextField(label="Adâncime (A)", value="510", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_HA = ft.TextField(label="Înălțime Ansamblu (HA)", value="820", expand=1, keyboard_type=ft.KeyboardType.NUMBER)

    # Opțiuni Dropdown categorii (din lista manuală)
    cats_options = [ft.dropdown.Option(c) for c in categorii_manuale]

    combo_cat = ft.Dropdown(label="Categorie", options=cats_options, on_change=incarca_modele)
    combo_mod = ft.Dropdown(label="Model Corp (JSON)")
    combo_sina = ft.Dropdown(
        label="Lungime Șină (S)", 
        value="500", 
        options=[ft.dropdown.Option(str(x)) for x in range(300, 650, 50)]
    )
    
    radio_cant = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="MDF", label="MDF"), 
            ft.Radio(value="1mm", label="1mm"), 
            ft.Radio(value="2mm", label="2mm")
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="MDF"
    )
    
    lista_vizuala = ft.Column()

    # --- LAYOUT PAGINĂ ---
    page.add(
        ft.Text("Mobipro Mobile v7.3", size=25, weight="bold", color="blue900"),
        ft.Row([inp_L, inp_H]),
        ft.Row([inp_A, inp_HA]),
        combo_cat,
        combo_mod,
        ft.Text("Tip Cant Front (scade din dimensiune):", size=12),
        radio_cant,
        combo_sina,
        ft.Row([
            ft.ElevatedButton(
                "ADĂUGĂ", 
                icon=ft.Icons.ADD, 
                on_click=adauga_corp, 
                expand=True, 
                style=ft.ButtonStyle(color="white", bgcolor="blue900")
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_FOREVER, 
                on_click=lambda _: [lista_vizuala.controls.clear(), page.update()], 
                icon_color="red"
            )
        ]),
        ft.Divider(),
        lista_vizuala
    )

# Pornire aplicație
# assets_dir="assets" este critic pentru ca APK-ul să includă fișierele tale
ft.app(target=main, assets_dir="assets")