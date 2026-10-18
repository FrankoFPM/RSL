# -*- coding: utf-8 -*-
"""Genera la version publica del libro de datos: quita resumenes, referencias,
financiamiento y correos electronicos, y conserva todo lo que usan los scripts.
Uso: python sanear_excel.py ENTRADA.xlsx SALIDA.xlsx"""
import re, sys, openpyxl
EMAIL = re.compile(r'[\w.+-]+@[\w-]+(\.[\w-]+)+')
# Columnas que se eliminan por hoja (las demas se conservan tal cual)
QUITAR_PROCESADAS = {'AB', 'CR', 'EM'}
QUITAR_SCOPUS = {'Abstract', 'References', 'Correspondence Address', 'Funding Details',
                 'Funding Texts', 'Funding Text 1', 'Funding Text 2', 'Funding Text 3',
                 'Chemicals/CAS', 'Tradenames', 'Manufacturers', 'Molecular Sequence Numbers'}
QUITAR_WOS = {'AB', 'CR', 'EM', 'RP', 'FU', 'FX', 'OI', 'RI'}
def quitar_por_hoja(nombre):
    if nombre == 'ARTICULOS SCOPUS': return QUITAR_SCOPUS
    if nombre == 'ARTICULOS WoS': return QUITAR_WOS
    return QUITAR_PROCESADAS
def main(src, dst):
    wb = openpyxl.load_workbook(src)
    for ws in wb.worksheets:
        quitar = quitar_por_hoja(ws.title)
        cab = [c.value for c in ws[1]]
        for idx in sorted([i + 1 for i, h in enumerate(cab) if h in quitar], reverse=True):
            ws.delete_cols(idx)
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and EMAIL.search(c.value):
                    c.value = EMAIL.sub('[correo omitido]', c.value)
    wb.save(dst)
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
