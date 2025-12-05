import os
from pypdf import PdfReader

iskalna_beseda = "štab"
mapa = r"D:\simon\lok\LZS\io\stari zapisniki"

for ime in os.listdir(mapa):
    if ime.lower().endswith(".organi"):
        pot = os.path.join(mapa, ime)

        try:
            reader = PdfReader(pot)
            vsebina = ""

            for stran in reader.pages:
                tekst = stran.extract_text()
                if tekst:
                    vsebina += tekst.lower()

            if iskalna_beseda.lower() in vsebina:
                print(f"Najdeno v: {ime}")
        except Exception as e:
            print(f"Napaka pri branju {ime}: {e}")
