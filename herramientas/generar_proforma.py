#!/usr/bin/env python3
"""Genera una proforma profesional en PDF a partir de un archivo JSON.

Uso:  python3 herramientas/generar_proforma.py proformas/datos/1047.json
Salida: proformas/emitidas/<numero>_<cliente>.pdf
"""
import json, sys, re, unicodedata
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle,
                                Spacer, Image, KeepTogether)

RAIZ = Path(__file__).resolve().parent.parent
VERDE = colors.HexColor("#2E7D32"); VERDE_CLARO = colors.HexColor("#E8F5E9")
GRIS = colors.HexColor("#555555"); AZUL = colors.HexColor("#1565C0")
IVA = 0.15

def money(x):
    s = f"{x:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

UNI = ["", "UNO", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ",
       "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE", "DIECIOCHO",
       "DIECINUEVE", "VEINTE", "VEINTIUNO", "VEINTIDÓS", "VEINTITRÉS", "VEINTICUATRO",
       "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
DEC = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
CEN = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS",
       "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

def _menor_mil(n):
    if n == 0: return ""
    if n == 100: return "CIEN"
    c, r = divmod(n, 100); out = [CEN[c]] if c else []
    if r < 30: out.append(UNI[r])
    else:
        d, u = divmod(r, 10); out.append(DEC[d] + (f" Y {UNI[u]}" if u else ""))
    return " ".join(x for x in out if x)

def en_letras(valor):
    entero = int(valor); cent = round((valor - entero) * 100)
    if cent == 100: entero, cent = entero + 1, 0
    millones, resto = divmod(entero, 1_000_000); miles, unidades = divmod(resto, 1000)
    partes = []
    if millones: partes.append("UN MILLÓN" if millones == 1 else _menor_mil(millones) + " MILLONES")
    if miles: partes.append("MIL" if miles == 1 else _menor_mil(miles) + " MIL")
    if unidades: partes.append(_menor_mil(unidades))
    txt = " ".join(partes) or "CERO"
    txt = re.sub(r"\bUNO MIL\b", "UN MIL", txt)
    return f"{txt} CON {cent:02d}/100 DÓLARES DE LOS ESTADOS UNIDOS DE AMÉRICA"

def main(ruta_json):
    d = json.loads(Path(ruta_json).read_text(encoding="utf-8"))
    emp = d["emisor"]
    st = lambda **k: ParagraphStyle("x", **{"fontName": "Helvetica", "fontSize": 9, "leading": 11, **k})
    p_norm, p_small = st(), st(fontSize=7.5, leading=9, textColor=GRIS)
    p_bold = st(fontName="Helvetica-Bold")
    p_title = st(fontName="Helvetica-Bold", fontSize=14, leading=17, alignment=1, textColor=VERDE)
    p_proj = st(fontName="Helvetica-Bold", fontSize=11, leading=14, alignment=1, textColor=AZUL)

    ascii_cli = unicodedata.normalize("NFKD", d['cliente']['nombre']).encode("ascii", "ignore").decode()
    nombre_pdf = f"{d['numero']}_{re.sub(r'[^A-Za-z0-9]+', '-', ascii_cli).strip('-')}.pdf"
    salida = RAIZ / "proformas" / "emitidas" / nombre_pdf
    doc = SimpleDocTemplate(str(salida), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=12*mm, bottomMargin=15*mm,
                            title=f"Proforma {d['numero']} - {d['proyecto']}")
    W = A4[0] - 30*mm
    el = []

    # Encabezado
    logo = Image(str(RAIZ / emp["logo"]), width=42*mm, height=18.5*mm)
    datos = Paragraph(
        f"<font size=15 color='#2E7D32'><b>{emp['nombre']}</b></font><br/>"
        f"<font size=9 color='#2E7D32'>{emp['subtitulo']}</font><br/>"
        f"<font size=7.5 color='#555555'>RUC: {emp['ruc']} · {emp['licencia']}<br/>"
        f"{emp['direccion']} · Telf. {emp['telefono']} · Cel. {emp['celular']}<br/>{emp['correo']}</font>", p_norm)
    caja_num = Table([["PROFORMA"], [f"N.º {d['numero']}"], [d["fecha"]]], colWidths=[35*mm])
    caja_num.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), VERDE), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,1), "Helvetica-Bold"), ("FONTSIZE", (0,1), (-1,1), 12),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), ("BOX", (0,0), (-1,-1), 1, VERDE),
        ("FONTSIZE", (0,2), (-1,2), 8)]))
    enc = Table([[logo, datos, caja_num]], colWidths=[46*mm, W-46*mm-37*mm, 37*mm])
    enc.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                             ("LINEBELOW", (0,0), (-1,0), 2, VERDE)]))
    el += [enc, Spacer(1, 5*mm), Paragraph("PRESUPUESTO REFERENCIAL DE OBRA", p_title),
           Spacer(1, 1*mm), Paragraph(d["proyecto"].upper(), p_proj), Spacer(1, 4*mm)]

    # Datos del cliente
    c = d["cliente"]
    filas = [[Paragraph("<b>Cliente:</b>", p_norm), Paragraph(c["nombre"], p_norm),
              Paragraph("<b>RUC/C.I.:</b>", p_norm), Paragraph(c.get("ruc", "—"), p_norm)],
             [Paragraph("<b>Atención:</b>", p_norm), Paragraph(c.get("contacto", "—"), p_norm),
              Paragraph("<b>Ubicación:</b>", p_norm), Paragraph(d.get("ubicacion", "—"), p_norm)],
             [Paragraph("<b>Plazo:</b>", p_norm), Paragraph(d.get("plazo", "—"), p_norm),
              Paragraph("<b>Validez:</b>", p_norm), Paragraph(d.get("validez", "15 días"), p_norm)]]
    tc = Table(filas, colWidths=[20*mm, W/2-20*mm, 22*mm, W/2-22*mm])
    tc.setStyle(TableStyle([("BOX", (0,0), (-1,-1), 0.6, GRIS), ("BACKGROUND", (0,0), (-1,-1), VERDE_CLARO),
                            ("VALIGN", (0,0), (-1,-1), "TOP")]))
    el += [tc, Spacer(1, 4*mm)]

    # Rubros
    cols = [10*mm, W-10*mm-16*mm-20*mm-22*mm-25*mm, 16*mm, 20*mm, 22*mm, 25*mm]
    data = [["N.º", "DESCRIPCIÓN DEL RUBRO", "UNIDAD", "CANTIDAD", "P. UNITARIO", "P. TOTAL"]]
    estilos = [("BACKGROUND", (0,0), (-1,0), VERDE), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
               ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
               ("ALIGN", (0,0), (-1,0), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
               ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#BDBDBD"))]
    subtotal = 0; n = 0
    for g in d["grupos"]:
        r = len(data); data.append([g["titulo"].upper(), "", "", "", "", ""])
        estilos += [("SPAN", (0,r), (-1,r)), ("BACKGROUND", (0,r), (-1,r), VERDE_CLARO),
                    ("FONTNAME", (0,r), (-1,r), "Helvetica-Bold"), ("TEXTCOLOR", (0,r), (-1,r), AZUL)]
        sg = 0
        for rb in g["rubros"]:
            n += 1; tot = round(rb["cantidad"] * rb["pu"], 2); sg += tot
            desc = rb["descripcion"] + (f"<br/><font size=7 color='#555555'>{rb['especificacion']}</font>"
                                        if rb.get("especificacion") else "")
            data.append([str(n), Paragraph(desc, st(fontSize=8.5, leading=10)), rb["unidad"],
                         money(rb["cantidad"]), money(rb["pu"]), money(tot)])
        if len(d["grupos"]) > 1:
            r = len(data); data.append(["", f"Subtotal {g['titulo'].lower()}", "", "", "", money(sg)])
            estilos += [("FONTNAME", (0,r), (-1,r), "Helvetica-Bold"), ("SPAN", (1,r), (4,r)), ("ALIGN", (1,r), (1,r), "RIGHT")]
        subtotal += sg
    estilos += [("ALIGN", (2,1), (2,-1), "CENTER"), ("ALIGN", (3,1), (-1,-1), "RIGHT"), ("ALIGN", (0,1), (0,-1), "CENTER")]
    t = Table(data, colWidths=cols, repeatRows=1); t.setStyle(TableStyle(estilos))
    el += [t]

    # Totales
    subtotal = round(subtotal, 2); iva = round(subtotal * IVA, 2); total = round(subtotal + iva, 2)
    tt = Table([["SUBTOTAL SIN IVA", money(subtotal)], [f"IVA {int(IVA*100)} %", money(iva)],
                ["TOTAL USD", money(total)]], colWidths=[40*mm, 25*mm], hAlign="RIGHT")
    tt.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "RIGHT"), ("FONTSIZE", (0,0), (-1,-1), 9),
                            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
                            ("BACKGROUND", (0,2), (-1,2), VERDE), ("TEXTCOLOR", (0,2), (-1,2), colors.white),
                            ("BOX", (0,0), (-1,-1), 0.6, GRIS), ("LINEBELOW", (0,0), (-1,1), 0.3, GRIS)]))
    el += [Spacer(1, 1*mm), tt, Spacer(1, 2*mm),
           Paragraph(f"<b>Son:</b> {en_letras(total)}", p_norm), Spacer(1, 4*mm)]

    # Condiciones
    bloque = []
    for titulo, clave in [("Condiciones comerciales", "condiciones"), ("Incluye", "incluye"),
                          ("No incluye", "no_incluye"), ("Notas técnicas", "notas")]:
        if d.get(clave):
            bloque.append(Paragraph(f"<b>{titulo}</b>", st(fontName="Helvetica-Bold", textColor=VERDE)))
            bloque += [Paragraph(f"• {x}", st(fontSize=8, leading=10, leftIndent=6)) for x in d[clave]]
            bloque.append(Spacer(1, 2*mm))
    firma = Table([[""], [emp["firmante"]], [emp["licencia"]]], colWidths=[70*mm], hAlign="CENTER")
    firma.setStyle(TableStyle([("LINEABOVE", (0,1), (0,1), 0.8, colors.black), ("ALIGN", (0,0), (-1,-1), "CENTER"),
                               ("FONTSIZE", (0,0), (-1,-1), 9), ("TOPPADDING", (0,0), (0,0), 18*mm)]))
    bloque += [firma]
    el.append(KeepTogether(bloque))

    def pie(canv, _doc):
        canv.saveState(); canv.setFont("Helvetica", 7); canv.setFillColor(GRIS)
        canv.drawString(15*mm, 8*mm, f"{emp['nombre']} · Proforma {d['numero']} · {d['cliente']['nombre']}")
        canv.drawRightString(A4[0]-15*mm, 8*mm, f"Página {_doc.page}"); canv.restoreState()
    doc.build(el, onFirstPage=pie, onLaterPages=pie)
    print(f"PDF: {salida}\nSubtotal {money(subtotal)} | IVA {money(iva)} | Total {money(total)}")

if __name__ == "__main__":
    main(sys.argv[1])
