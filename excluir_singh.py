# Excluye Singh2025 (DOI 10.1145/3705926) en la etapa de elegibilidad a texto completo.
import sys, openpyxl
DOI = '10.1145/3705926'
MOTIVO = ('Excluido en la evaluacion de elegibilidad a texto completo (octubre 2026): '
          'el estudio evalua ResMLP en CIFAR-10 y SVHN (clasificacion de imagenes); '
          'no optimiza ni evalua ningun LLM, por lo que no cumple el criterio de inclusion sobre LLM.')
wb = openpyxl.load_workbook(sys.argv[1])
fila_copia = None
for n in ['SELECCIONADOS-FINAL', 'VERIFICAR-ACCESS']:
    ws = wb[n]; H = [c.value for c in ws[1]]; di = H.index('DI') + 1
    for r in range(ws.max_row, 1, -1):
        if str(ws.cell(r, di).value or '').strip().lower() == DOI:
            if n == 'SELECCIONADOS-FINAL':
                fila_copia = (H, [c.value for c in ws[r]])
            ws.delete_rows(r)
if 'EXCLUIDOS-TEXTO-COMPLETO' not in wb.sheetnames and fila_copia:
    H, vals = fila_copia
    ex = wb.create_sheet('EXCLUIDOS-TEXTO-COMPLETO', index=wb.sheetnames.index('VERIFICAR-ACCESS') + 1)
    keep = [h for h in H if h]
    ex.append(keep + ['MOTIVO_EXCLUSION'])
    d = dict(zip(H, vals)); ex.append([d[h] for h in keep] + [MOTIVO])
wb.save(sys.argv[2])
