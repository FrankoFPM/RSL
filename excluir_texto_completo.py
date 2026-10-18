# Excluye estudios en la evaluacion de elegibilidad a texto completo y los registra en la hoja EXCLUIDOS-TEXTO-COMPLETO.
import sys, openpyxl
EXCL = {
 '10.1109/tvlsi.2025.3544342': 'Song2025: aceleracion FPGA de busqueda ANNS (IVF-PQ); no optimiza ni evalua un LLM.',
 '10.1109/tcsi.2025.3609631': 'Song2026: construccion de indices IVF-PQ en FPGA; no optimiza ni evalua un LLM.',
 '10.1109/tmc.2024.3355764': 'Wang2024: swapping de DNN genericas (SwapNet); los LLM se mencionan solo como trabajo futuro.',
 '10.1016/j.neucom.2025.131745': 'Zhang2025d: estimacion de profundidad con camaras de eventos (vision); el texto completo no menciona LLM.',
 '10.1016/j.asoc.2026.115112': 'Xue2026: copiloto industrial multimodal de video y series de tiempo; el resumen no describe ningun modelo de lenguaje.',
 '10.1109/access.2026.3678895': 'Choi2026: Whisper-small y OPUS-MT para traduccion de voz; los autores distinguen explicitamente su carga de un LLM.',
}
wb = openpyxl.load_workbook(sys.argv[1])
moved = []
for n in ['SELECCIONADOS-FINAL', 'VERIFICAR-ACCESS']:
    ws = wb[n]; H = [c.value for c in ws[1]]; di = H.index('DI') + 1
    for r in range(ws.max_row, 1, -1):
        d = str(ws.cell(r, di).value or '').strip().lower()
        if d in EXCL:
            if n == 'SELECCIONADOS-FINAL': moved.append((H, [c.value for c in ws[r]], EXCL[d]))
            ws.delete_rows(r)
ex = wb['EXCLUIDOS-TEXTO-COMPLETO']
keep = [c.value for c in ex[1]][:-1]
for H, vals, why in reversed(moved):
    d = dict(zip(H, vals)); ex.append([d.get(h) for h in keep] + ['Excluido en la evaluacion a texto completo (octubre 2026). ' + why])
wb.save(sys.argv[2]); print('excluidos', len(moved))
