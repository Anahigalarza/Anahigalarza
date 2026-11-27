#!/usr/bin/env python3
"""Generador de publicaciones de Legado Constructora (1080x1350, formato 4:5 para Instagram/Facebook).

Funciones:
  antes_despues(antes, despues, salida, titulo, subtitulo)
  foto(ruta, salida, titulo, subtitulo, recorte=None)     # recorte=(izq, arriba, der, abajo) en píxeles
  tarjeta(salida, titulo, lineas, pie=None)               # texto sobre fondo de marca
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VERDE = (46, 125, 50); VERDE_OSC = (27, 67, 30); NARANJA = (230, 126, 34); BLANCO = (255, 255, 255); OSCURO = (33, 33, 33)
MARCA = "LEGADO CONSTRUCTORA"; USUARIO = "@legadoconstructora"; WHATSAPP = "0987937294"
W, H, TOP, BOT = 1080, 1350, 120, 180

def f(path, size): return ImageFont.truetype(path, size)

def _abrir(ruta, recorte=None):
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    return im.crop(recorte) if recorte else im

def _centrar(d, y, texto, fuente, color, ancho=W):
    d.text(((ancho - d.textlength(texto, font=fuente)) / 2, y), texto, font=fuente, fill=color)

def _ajustar(d, texto, fuente, ancho):
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho: actual = prueba
        else: lineas.append(actual); actual = p
    return lineas + [actual] if actual else lineas

def _marco(lienzo, titulo, subtitulo):
    d = ImageDraw.Draw(lienzo)
    d.rectangle([0, 0, W, TOP], fill=VERDE)
    ft = f(B, 46)
    while d.textlength(titulo, font=ft) > W - 60: ft = f(B, ft.size - 2)
    _centrar(d, (TOP - ft.size) / 2 - 4, titulo, ft, BLANCO)
    d.rectangle([0, H - BOT, W, H], fill=BLANCO)
    logo = Image.open(RAIZ / "empresa/marca/logo-lg.png").convert("RGB"); logo.thumbnail((220, 100))
    lienzo.paste(logo, (30, H - BOT + (BOT - logo.height) // 2))
    x = 280; fs = f(B, 30)
    while d.textlength(subtitulo, font=fs) > W - x - 20: fs = f(B, fs.size - 1)
    d.text((x, H - BOT + 28), subtitulo, font=fs, fill=OSCURO)
    d.text((x, H - BOT + 78), MARCA + " · Ambato", font=f(R, 24), fill=OSCURO)
    d.text((x, H - BOT + 115), f"{USUARIO}  ·  WhatsApp {WHATSAPP}", font=f(B, 24), fill=VERDE)
    return d

def antes_despues(antes, despues, salida, titulo, subtitulo, recorte_antes=None, recorte_despues=None):
    lienzo = Image.new("RGB", (W, H), BLANCO); d = ImageDraw.Draw(lienzo); alto = H - TOP - BOT
    for i, (ruta, rc, rotulo) in enumerate([(antes, recorte_antes, "ANTES"), (despues, recorte_despues, "DESPUÉS")]):
        im = ImageOps.fit(_abrir(ruta, rc), (W // 2 - 3, alto)); x = i * (W // 2 + 3); lienzo.paste(im, (x, TOP))
        fr = f(B, 40); tw = d.textlength(rotulo, font=fr)
        d.rounded_rectangle([x + 20, TOP + 20, x + 50 + tw, TOP + 80], 12, fill=VERDE if i else OSCURO)
        d.text((x + 35, TOP + 26), rotulo, font=fr, fill=BLANCO)
    _marco(lienzo, titulo, subtitulo); lienzo.save(salida, quality=92); return salida

def foto(ruta, salida, titulo, subtitulo, recorte=None, etiqueta=None):
    lienzo = Image.new("RGB", (W, H), BLANCO)
    lienzo.paste(ImageOps.fit(_abrir(ruta, recorte), (W, H - TOP - BOT)), (0, TOP))
    d = _marco(lienzo, titulo, subtitulo)
    if etiqueta:
        fr = f(B, 34); tw = d.textlength(etiqueta, font=fr)
        d.rounded_rectangle([20, TOP + 20, 50 + tw, TOP + 76], 12, fill=NARANJA)
        d.text((35, TOP + 28), etiqueta, font=fr, fill=BLANCO)
    lienzo.save(salida, quality=92); return salida

def tarjeta(salida, titulo, lineas, pie=None, fondo=None, recorte_fondo=None):
    lienzo = Image.new("RGB", (W, H), VERDE_OSC)
    if fondo:
        bg = ImageOps.fit(_abrir(fondo, recorte_fondo), (W, H)).point(lambda v: int(v * 0.30)); lienzo.paste(bg, (0, 0))
    d = ImageDraw.Draw(lienzo)
    logo = Image.open(RAIZ / "empresa/marca/logo-lg.png").convert("RGB"); logo.thumbnail((300, 130))
    pad = Image.new("RGB", (logo.width + 30, logo.height + 20), BLANCO); pad.paste(logo, (15, 10))
    lienzo.paste(pad, ((W - pad.width) // 2, 70))
    y = 70 + pad.height + 50; ft = f(B, 60)
    for linea in _ajustar(d, titulo, ft, W - 120):
        _centrar(d, y, linea, ft, BLANCO); y += 74
    d.rectangle([W / 2 - 80, y + 15, W / 2 + 80, y + 21], fill=NARANJA); y += 60
    fl = f(R, 36)
    for item in lineas:
        for k, linea in enumerate(_ajustar(d, item, fl, W - 200)):
            d.text((100, y), ("•  " if k == 0 else "    ") + linea, font=fl, fill=BLANCO); y += 50
        y += 14
    d.rectangle([0, H - 130, W, H], fill=VERDE)
    _centrar(d, H - 112, pie or MARCA, f(B, 34), BLANCO)
    _centrar(d, H - 64, f"{USUARIO}  ·  WhatsApp {WHATSAPP}", f(R, 28), BLANCO)
    lienzo.save(salida, quality=92); return salida
