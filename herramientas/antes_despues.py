#!/usr/bin/env python3
"""Arma una imagen ANTES / DESPUÉS para Instagram/Facebook (1080x1350, formato 4:5).

Uso: python3 herramientas/antes_despues.py antes.jpg despues.jpg salida.jpg "Título" "Subtítulo"
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VERDE = (46, 125, 50); BLANCO = (255, 255, 255); OSCURO = (33, 33, 33)

def main(antes, despues, salida, titulo, subtitulo, marca="@legadoconstructora"):
    W, H, top, bot = 1080, 1350, 110, 190
    lienzo = Image.new("RGB", (W, H), BLANCO); d = ImageDraw.Draw(lienzo)
    alto = H - top - bot
    for i, (ruta, rotulo) in enumerate([(antes, "ANTES"), (despues, "DESPUÉS")]):
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(ruta)).convert("RGB"), (W // 2 - 3, alto))
        x = i * (W // 2 + 3); lienzo.paste(im, (x, top))
        f = ImageFont.truetype(B, 40); tw = d.textlength(rotulo, font=f)
        d.rounded_rectangle([x + 20, top + 20, x + 50 + tw, top + 80], 12, fill=VERDE if i else OSCURO)
        d.text((x + 35, top + 26), rotulo, font=f, fill=BLANCO)
    d.rectangle([0, 0, W, top], fill=VERDE)
    ft = ImageFont.truetype(B, 44); d.text(((W - d.textlength(titulo, font=ft)) / 2, 30), titulo, font=ft, fill=BLANCO)
    logo = Image.open(RAIZ / "empresa/marca/logo-lg.png").convert("RGB"); logo.thumbnail((260, 120))
    lienzo.paste(logo, (30, H - bot + (bot - logo.height) // 2))
    d.text((320, H - bot + 40), subtitulo, font=ImageFont.truetype(B, 30), fill=OSCURO)
    d.text((320, H - bot + 90), "Construcción y reparación de obras civiles · Ambato", font=ImageFont.truetype(R, 24), fill=OSCURO)
    d.text((320, H - bot + 130), marca + "  ·  0998003983", font=ImageFont.truetype(B, 24), fill=VERDE)
    lienzo.save(salida, quality=92); print(salida)

if __name__ == "__main__":
    main(*sys.argv[1:6])
