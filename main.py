import flet as ft
import json
import math
import os
from simpleeval import simple_eval

def main(page: ft.Page):
    page.title = "Mobipro v7.3 Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"
    page.padding = 20
    
    # IMPORTANTE: Calea trebuie să coincidă cu structura de pe GitHub
    # Dacă în GitHub ai assets/database/bucatarii/...
    cale_baza = "assets/database" 

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
            # Debug: afișează o eroare în pagină dacă nu găsește folderul
            print(f"Calea nu există: {cale_cat}")

    def adauga_corp(e):
        try:
            v_L, v_H, v_A = float(inp_L.value), float(inp_H.value), float(inp_A.value)
            v_HA = float(inp_HA.value)
            v_S = float(combo_sina.value)

            ctx_n = {"L": v_L, "H": v_H, "A": v_A, "HA": v_HA, "S": v_S, "le": 1.5, "li": 2.0, "G": 18}
            ctx_f = {"floor": math.floor, "ceil": math.ceil, "round": round}

            cale_json = os.path.join(cale_baza, combo_cat.value, combo_mod.value)
            
            with open(cale_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Luăm prima cheie (numele corpului)
                structura = data[list(data.keys())[0]]

            for p in structura.get("piese", []):
                vL_raw = simple_eval(str(p["L"]), names=ctx_n, functions=ctx_f)
                vl_raw = simple_eval(str(p["l"]), names=ctx_n, functions=ctx_f)
                vL, vl = math.floor(vL_raw), math.floor(vl_raw)
                
                if "front" in p["material"].lower() and radio_cant.value != "MDF":
                    v_c = 1 if radio_cant.value == "1mm" else 2
                    vL -= (v_c * 2); vl -= (v_c * 2)

                lista_vizuala.controls.append(
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
            # Snackbar pentru erori pe telefon
            page.snack_bar = ft.SnackBar(ft.Text(f"Eroare: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- COMPONENTE UI ---
    inp_L = ft.TextField(label="L", value="600", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_H = ft.TextField(label="H", value="760", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_A = ft.TextField(label="A", value="510", expand=1, keyboard_type=ft.KeyboardType.NUMBER)
    inp_HA = ft.TextField(label="HA", value="820", expand=1, keyboard_type=ft.KeyboardType.NUMBER)

    cats = []
    if os.path.exists(cale_baza):
        cats = [ft.dropdown.Option(d) for d in os.listdir(cale_baza) if os.path.isdir(os.path.join(cale_baza, d))]

    combo_cat = ft.Dropdown(label="Categorie", options=cats, on_change=incarca_modele)
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

ft.app(target=main, assets_dir="assets") # Foarte important assets_dir