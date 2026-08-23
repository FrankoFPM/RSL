# Paquete de replicación — RSL: Optimización de LLMs en dispositivos de recursos limitados

Materiales de replicación de la revisión sistemática de literatura sobre técnicas de optimización de Modelos de Lenguaje de Gran Escala (LLMs) para despliegue en hardware perimetral (2024–2026).

**Autores:** Johann Gudwig Camiloaga Cuenca, Franco Johan Perez Melgarejo
Universidad Tecnológica del Perú — Ingeniería de Sistemas e Informática

---

## Contenido

| Archivo | Descripción |
|---|---|
| `ARTICULOS_UNIFICADOS_CRIBADO.xlsx` | Datos primarios: búsqueda cruda, cribado y corpus final |
| `process_rsl.py` | Genera las figuras bibliométricas |
| `analisis_auditoria.py` | Genera las tablas cuantitativas y el reporte de consistencia |
| `anexoA_hardware.py` | Hardware declarado por cada estudio (Anexo A del manuscrito) |
| `tablas/` | Tablas LaTeX generadas, listas para `\input` |
| `graficos_sin_titulo/` | Figuras sin título, para insertar en el manuscrito |
| `graficos_fuente_grande/` | Variantes con tipografía ampliada |

## Hojas del libro de datos

| Hoja | Filas | Etapa PRISMA |
|---|---|---|
| `ARTICULOS SCOPUS` | 586 | Identificación (Scopus) |
| `ARTICULOS WoS` | 138 | Identificación (Web of Science) |
| `SELECCIONADOS` | 149 | Tras depuración y cribado preliminar |
| `SELECCIONADOS-CRIBADO` | 149 | Cribado con decisión y motivo |
| `SELECCIONADOS-FINAL` | **80** | **Corpus definitivo del estudio** |
| `VERIFICAR-ACCESS` | 80 | Seguimiento de acceso a texto completo |

> **Importante:** todo análisis debe leer `SELECCIONADOS-FINAL` (n=80). La hoja
> `SELECCIONADOS` (n=149) es la etapa previa a la aplicación de los criterios
> de elegibilidad y **no** constituye el corpus del estudio.

## Reproducción

```bash
pip install -r requirements.txt

python process_rsl.py          # figuras  -> ./  y  ./graficos_sin_titulo/
python analisis_auditoria.py   # tablas   -> ./tablas/
```

`analisis_auditoria.py` emite además `tablas/reporte_consistencia.txt`, que
verifica las cifras del flujo PRISMA contra los datos y resume la cobertura de
acceso a texto completo.

## Cifras de referencia

Salida esperada de `analisis_auditoria.py` sobre el corpus de 80 estudios:

```
Distribución anual        2024: 9  |  2025: 31  |  2026: 40
Fuentes normalizadas      57 revistas
Zonas de Bradford         Z1 = 7 rev / 28 art; Z2 = 25 / 27; Z3 = 25 / 25
Multiplicadores           [3.57, 1.00]  -> la Ley de Bradford no se cumple
Dispersión                48 de 57 revistas (84%) aportan un solo artículo
Autores                   398 únicos; 379 con un artículo (95.2%)
Estudios sin citas        43 de 80 (54%)
Plataforma Edge concreta  18 de 80 (22%)  |  FPGA = 8, Jetson = 4
Sin plataforma            57 de 80 (71%)
```

## Limitaciones declaradas

Estas limitaciones se documentan en la sección de Amenazas a la Validez del
manuscrito y se hacen explícitas aquí para quien reutilice los datos:

- **Cobertura de fuentes.** La búsqueda se ejecutó sobre Scopus y Web of Science.
  El criterio de exclusión CE-4 restringió el corpus a artículos de revista, lo
  que dejó fuera las actas de congreso (67% de los registros recuperados en
  Scopus). En ingeniería de sistemas de aprendizaje automático las conferencias
  constituyen un canal primario de publicación arbitrada.
- **Acceso a texto completo.** 36 de los 80 estudios incluidos (45%) fueron
  codificados a partir de resumen y metadatos indexados.
- **Extracción de hardware.** 57 estudios (71%) no declaran una plataforma
  física concreta; el análisis de métricas físicas se restringe a los 18 que sí
  lo hacen.
- **Evaluación de calidad.** Se aplicó como instrumento descriptivo, no como
  filtro de exclusión. Los resultados no están ponderados por calidad.
- **Fiabilidad inter-evaluador.** No se calculó coeficiente de concordancia
  entre evaluadores para las decisiones de cribado y extracción.

## Licencia

Los datos y el código se distribuyen bajo licencia MIT. Los artículos
referenciados permanecen sujetos a los derechos de sus respectivos editores.
