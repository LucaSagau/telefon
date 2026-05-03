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

    # --- LOGICĂ DETECTARE CALE (Fix pentru ecran alb pe Android) ---
    if getattr(sys, 'frozen', False):
        # Rulează ca aplicație împachetată (APK)
        baza_proiect = os.path.dirname(sys.executable)
    else:
        # Rulează local în VS Code
        baza_proiect = os.path.dirname(__file__)
    
    # Construim calea către assets/database conform structurii tale
    cale_baza = os.path.join(baza_proiect, "assets", "database")

    # --- FUNCTII ---
    def incarca_modele(e):
        if not combo_cat.value:
            return
        cale_cat = os.path.join(cale_baza, combo_cat.value)
        if os.path.exists(cale_cat):
            fisiere = [f for f in os.listdir(cale_cat) if f.endswith('.json')]
            combo_mod.options = [ft.dropdown.Option(f) for f in sorted(fisiere)]
            if fisiere:
                combo_mod.value = fisiere[0]
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Eroare: Calea {cale_cat} nu există!"))
            page.snack_bar.open = True
            page.update()

    def adauga_corp(e):
        try:
            v_L = float(inp_L.value) if inp_L.value else 0
            v_H = float(inp_H.value) if inp_H.value else 0
            v_A = float(inp_A.value) if inp_A.value else 0
            v_HA = float(inp_HA.value) if inp_HA.value else 0
            v_S = float(combo_sina.value)

            ctx_n = {"L": v_L, "H": v_H, "A": v_A, "HA": v_HA, "S": v_S, "le": 1.5, "li": 2.0, "G": 18}
            ctx_f = {"floor": math.floor, "ceil": math.ceil, "round": round}

            cale_json = os.path.join(cale_baza, combo_cat.value, combo_mod.value)
            
            with open(cale_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                structura = data[list(data.keys())[0]]

            for p in structura.get("piese", []):
                vL_raw = simple_eval(str(p["L"]), names=ctx_n, functions=ctx_f)
                vl_raw = simple_eval(str(p["l"]), names=ctx_n, functions=ctx_f)
                vL, vl = math.floor(vL_raw), math.floor(vl_raw)
                
                if "front" in p["material"].lower() and radio_cant.value != "MDF":
                    v_c = 1 if radio_cant.value == "1mm" else 2
                    vL -= (v_c * 2); vl -= (v_c * 2)

                lista_vizuala.controls.insert(0,
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text(p["nume"], weight="bold"),
                                ft.Row([
                                    ft.Text(f"{vL} x {vl}", size=20, color="blue900", weight="bold"),
                                    ft.Text(f"{p['cantitate']} buc"),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ])
                        )
                    )
                )
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Eroare: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- COMPONENTE UI ---
    inp_L = ft.TextField(label="L", value="600", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_H = ft.TextField(label="H", value="760", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_A = ft.TextField(label="A", value="510", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_HA = ft.TextField(label="HA", value="820", expand=1, keyboard_type=ft.KeyboardType.NUMBER)

    # Incarcare categorii cu protectie la erori
    cats_options = []
    try:
        if os.path.exists(cale_baza):
            dir_list = [d for d in os.listdir(cale_baza) if os.path.isdir(os.path.join(cale_baza, d))]
            cats_options = [ft.dropdown.Option(d) for d in sorted(dir_list)]
        else:
            cats_options = [ft.dropdown.Option("Database negăsit")]
    except Exception as e:
        cats_options = [ft.dropdown.Option(f"Eroare: {str(e)}")]

    combo_cat = ft.Dropdown(label="Categorie", options=cats_options, on_change=incarca_modele)
    combo_mod = ft.Dropdown(label="Model Corp (JSON)")
    combo_sina = ft.Dropdown(label="Sina (S)", value="500", options=[ft.dropdown.Option(str(x)) for x in range(300, 650, 50)])
    
    radio_cant = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="MDF", label="MDF"), 
            ft.Radio(value="1mm", label="1mm"), 
            ft.Radio(value="2mm", label="2mm")
        ], alignment=ft.MainAxisAlignment.CENTER),
        value="MDF"
    )
    
    lista_vizuala = ft.Column()

    page.add(
        ft.Text("Mobipro Mobile v7.3", size=25, weight="bold"),
        ft.Row([inp_L, inp_H]),
        ft.Row([inp_A, inp_HA]),
        combo_cat,
        combo_mod,
        ft.Text("Tip Cant Front:", size=12),
        radio_cant,
        combo_sina,
        ft.Row([
            ft.ElevatedButton("ADĂUGĂ", icon=ft.Icons.ADD, on_click=adauga_corp, expand=True, 
                             style=ft.ButtonStyle(color="white", bgcolor="blue900")),
            ft.IconButton(icon=ft.Icons.DELETE_FOREVER, 
                         on_click=lambda _: [lista_vizuala.controls.clear(), page.update()], 
                         icon_color="red")
        ]),
        ft.Divider(),
        lista_vizuala
    )

# Pornire aplicatie cu folderul de resurse definit
ft.app(target=main, assets_dir="assets")