#!/usr/bin/env python3
"""Exporta una obra completa (o cualquier carpeta con CSV) a un Excel con una hoja por archivo.

Uso:  python3 herramientas/exportar_excel.py obras/OB-2026-01-prodegel-anden-gf
Salida: <carpeta>/<nombre-carpeta>.xlsx
"""
import csv, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

def num(v):
    try: return float(v) if v.strip() != "" else v
    except ValueError: return v

carpeta = Path(sys.argv[1]); wb = Workbook(); wb.remove(wb.active)
for f in sorted(carpeta.rglob("*.csv")):
    ws = wb.create_sheet(f.stem[:31])
    with open(f, encoding="utf-8") as fh:
        for i, fila in enumerate(csv.reader(fh)):
            ws.append([num(v) if i else v for v in fila])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="2E7D32")
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(45, max(10, max(len(str(c.value or "")) for c in col) + 2))
    ws.freeze_panes = "A2"
salida = carpeta / f"{carpeta.name}.xlsx"; wb.save(salida); print(f"Excel: {salida}")
