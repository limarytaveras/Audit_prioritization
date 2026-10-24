# Priorización explicable de auditorías

Prototipo en Python para ordenar procesos por riesgo, cobertura, hallazgos e incidentes y construir una cartera preliminar según horas. Todos los datos son ficticios.

El flujo valida entradas, reconstruye eventos a la fecha de corte, calcula puntuaciones, prioriza obligaciones y asigna capacidad. Explica los componentes y reporta faltantes de horas.

El modelo opcional estima decisiones históricas de selección. No predice hallazgos graves y no modifica el ranking experto. Sus métricas sintéticas no representan desempeño real.

Para ejecutarlo desde esta carpeta:

```bash
python -m pip install -e .
python -m audit_planner --demo --with-model
python -m unittest discover -s tests -v
```

`examples/` contiene resultados reproducidos. `docs/GITHUB_SETUP_ES.md` incluye qué subir, descripción, etiquetas y texto para tu portafolio. Esta edición pública consume CSV de esquema explícito y exporta CSV/JSON; no conserva los alias libres, Excel ni el ranking de oficinas del prototipo anterior. Los documentos ejecutivos institucionales se sustituyen por un caso ficticio en Markdown.
