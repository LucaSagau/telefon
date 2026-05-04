import flet as ft
import json
import os
import math
from simpleeval import simple_eval

def main(page: ft.Page):
    page.title = "Mobipro v7.4"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"

    # Calea de baza
    cale_baza = "assets/database"

    # Functie pentru afisat mesaje jos pe ecran
    def log(mesaj):
        page.snack_bar = ft.SnackBar(ft.Text(mesaj))
        page.snack_bar.open = True
        page.update()

    # --- FUNCTII ---
    def incarca_modele(e):
        try:
            cale_cat = os.path.join(cale_baza, combo_cat.value)
            if os.path.exists(cale_cat):
                fisiere = [f for f in os.listdir(cale_cat) if f.endswith('.json')]
                combo_mod.options = [ft.dropdown.Option(f) for f in sorted(fisiere)]
                if fisiere:
                    combo_mod.value = fisiere[0]
                    log(f"Am gasit {len(fisiere)} modele.")
                else:
                    log("Folderul este gol (fara .json)")
            else:
                log(f"Calea nu exista: {cale_cat}")
            page.update()
        except Exception as ex:
            log(f"Eroare: {str(ex)}")

    def adauga_corp(e):
        try:
            # Daca nu e ales modelul, iesim
            if not combo_mod.value:
                log("Alege un model mai intai!")
                return

            v_L, v_H, v_A = float(inp_L.value or 0), float(inp_H.value or 0), float(inp_A.value or 0)
            v_HA, v_S = float(inp_HA.value or 0), float(combo_sina.value)

            ctx_n = {"L": v_L, "H": v_H, "A": v_A, "HA": v_HA, "S": v_S, "le": 1.5, "li": 2.0, "G": 18}
            ctx_f = {"floor": math.floor, "ceil": math.ceil, "round": round}

            cale_json = os.path.join(cale_baza, combo_cat.value, combo_mod.value)
            
            with open(cale_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                structura = data[list(data.keys())[0]]

            for p in structura.get("piese", []):
                vL = math.floor(simple_eval(str(p["L"]), names=ctx_n, functions=ctx_f))
                vl = math.floor(simple_eval(str(p["l"]), names=ctx_n, functions=ctx_f))
                
                if "front" in p["material"].lower() and radio_cant.value != "MDF":
                    v_c = 1 if radio_cant.value == "1mm" else 2
                    vL -= (v_c * 2); vl -= (v_c * 2)

                lista_vizuala.controls.insert(0, ft.Card(content=ft.Container(padding=10, content=ft.Column([
                    ft.Text(p["nume"], weight="bold"),
                    ft.Row([ft.Text(f"{vL} x {vl}", size=18, color="blue", weight="bold"), ft.Text(f"{p['cantitate']} buc")])
                ]))))
            page.update()
        except Exception as ex:
            log(f"Eroare calcul: {ex}")

    # --- UI COMPONENTS ---
    inp_L = ft.TextField(label="L", value="600", expand=1, keyboard_type="number")
    inp_H = ft.TextField(label="H", value="760", expand=1, keyboard_type="number")
    inp_A = ft.TextField(label="A", value="510", expand=1, keyboard_type="number")
    inp_HA = ft.TextField(label="HA", value="820", expand=1, keyboard_type="number")
    
    # Lista manuala de categorii
    categorii = ["Corpuri_baie", "Corpuri_custom", "Corpuri_dormitor", "Corpuri_hol", 
                 "Corpuri_inferioare", "CORPURI_INFERIOARE_GOLA", "Corpuri_living", 
                 "Corpuri_superioare", "Turnuri"]

    combo_cat = ft.Dropdown(label="Categorie", on_change=incarca_modele, 
                           options=[ft.dropdown.Option(c) for c in categorii])
    
    combo_mod = ft.Dropdown(label="Model (Alege categoria)")
    
    combo_sina = ft.Dropdown(label="Sina", value="500", 
                            options=[ft.dropdown.Option(str(x)) for x in range(300, 650, 50)])
    
    radio_cant = ft.RadioGroup(value="MDF", content=ft.Row([
        ft.Radio(value="MDF", label="MDF"), 
        ft.Radio(value="1mm", label="1mm"), 
        ft.Radio(value="2mm", label="2mm")
    ]))
    
    lista_vizuala = ft.Column()

    # Adaugam totul in pagina dintr-odata
    page.add(
        ft.Text("Mobipro v7.4", size=20, weight="bold"),
        ft.Row([inp_L, inp_H]),
        ft.Row([inp_A, inp_HA]),
        combo_cat,
        combo_mod,
        ft.Text("Tip Cant Front:"),
        radio_cant,
        combo_sina,
        ft.ElevatedButton("ADĂUGĂ CORP", on_click=adauga_corp, bgcolor="blue", color="white", height=50),
        ft.Divider(),
        lista_vizuala
    )

ft.app(target=main, assets_dir="assets")